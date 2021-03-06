from secrets import token_hex

from flask import session
from flask_mail import Message
from flask_restplus import Resource, fields, Namespace

from app import db, TOKEN_LENGTH, config, PASSWORD_LENGTH
from app.models.Keys import Keys
from app.models.KeysTypes import KeysTypes
from app.models.Users import Users
from app.services.AuthManager import AuthManager
from app.services.BasicAuthManager import auth_required
from app.services.MailManager import MailManager

ns = Namespace('UserAPI', path='/user', description='Работа пользователями')

user_fields = ns.model('UserFields', {
    'id': fields.Integer(description='id пользователя'),
    'username': fields.String(description='Username пользователя'),
    'reg_date': fields.String(description='Дата регистарции пользователя'),
})
auth_user_response_model = ns.model('AuthUserResponse', {
    'status': fields.String(description='Статус'),
    'message': fields.String(description='Сообщение'),
    'user': fields.Nested(user_fields, skip_none=True, description='Информация о пользователе')
})


@ns.route('/')
class UserData(Resource):
    @ns.doc(description='Получение информации о пользователе')
    @ns.response(model=auth_user_response_model, skip_none=True, code=401, description='Unauthorized')
    @ns.response(model=auth_user_response_model, skip_none=True, code=406, description='Not Acceptable')
    @ns.marshal_with(auth_user_response_model, skip_none=True, code=200, description='OK')
    @auth_required
    def get(self):
        if session['username']:
            user = Users.select(Users.id, Users.username, Users.registration_date).where(
                Users.username == session['username'])[0]
            return {
                       'status': 'Success',
                       'user': {
                           'id': user.id,
                           'username': user.username,
                           'registration_date': str(user.registration_date)
                       }
                   }, 200


auth_all_users_response_model = ns.model('AuthAllUsersResponse', {
    'status': fields.String(description='Статус'),
    'message': fields.String(description='Сообщение'),
    'users': fields.List(cls_or_instance=fields.String, description='Список username всех пользователей')
})


@ns.route('/all')
class AllUsers(Resource):
    @ns.doc(description='Получение списка всех пользователей')
    @ns.response(model=auth_all_users_response_model, skip_none=True, code=401, description='Unauthorized')
    @ns.response(model=auth_all_users_response_model, skip_none=True, code=403, description='Forbidden')
    @ns.marshal_with(auth_all_users_response_model, skip_none=True, code=200, description='OK')
    @auth_required
    def get(self):
        with db.atomic():
            users = Users.select(Users.username)
            usernames = [user.username for user in users]
            return {
                       'status': 'Success',
                       'users': usernames
                   }, 200


activate_user_request_model = ns.model('ActivateUserRequest', {
    'key': fields.String(required=True, description='Ключ активации пользователя')
})
activate_user_response_model = ns.model('ActivateUserResponse', {
    'status': fields.String(description='Статус'),
    'message': fields.String(description='Сообщение'),
})


@ns.route('/activate')
class UserActivate(Resource):
    @ns.doc(description='Активация учётной записи')
    @ns.expect(activate_user_request_model)
    @ns.response(model=activate_user_response_model, skip_none=True, code=400, description='Bad request')
    @ns.marshal_with(activate_user_response_model, skip_none=True, code=200, description='Accepted')
    def post(self):
        key = ns.payload['key']
        user_from_keys = Keys.get_or_none(Keys.key == key and Keys.type == KeysTypes.ACTIVATION.value)
        if user_from_keys:
            with db.atomic():
                Users.update(active=True).where(Users.id == user_from_keys.user_id).execute()
                Keys.delete().where(Keys.key == key and Keys.type == KeysTypes.ACTIVATION.value).execute()
            return {
                       'status': 'Success',
                       'message': 'Учетная запись активирована'
                   }, 202
        else:
            return {
                       'status': 'Error',
                       'message': 'Заданного ключа не существует'
                   }, 400


recover_password_request_model = ns.model('RestorePasswordRequest', {
    'username': fields.String(required=True, description='Username пользователя'),
})
recover_password_response_model = ns.model('RestorePasswordResponse', {
    'status': fields.String(description='Статус'),
    'message': fields.String(description='Сообщение'),
})


@ns.route('/restore_password')
class UserRestorePassword(Resource):
    @ns.doc(description='Запрос на восстановление пароля')
    @ns.expect(recover_password_request_model)
    @ns.response(model=recover_password_response_model, skip_none=True, code=400, description='Bad request')
    @ns.response(model=recover_password_response_model, skip_none=True, code=406, description='Not Acceptable')
    @ns.marshal_with(recover_password_response_model, skip_none=True, code=202, description='Accepted')
    def post(self):
        username = ns.payload['username']
        with db.atomic():
            user = Users.get_or_none(Users.username == username)
            if user:
                user_from_keys = Keys.get_or_none(Keys.user_id == user.id and Keys.type == KeysTypes.RECOVERY.value)
                if not user_from_keys:
                    key = token_hex(TOKEN_LENGTH)
                    Keys.create(user_id=user.id, key=key, type=KeysTypes.RECOVERY.value)

                    msg = Message(
                        body=f'Ключ для восстановления пароля: {key}',
                        subject='Password recover',
                        sender=config.mail.mail_username,
                        recipients=[username]
                    )
                    MailManager.send_mail(msg)
                    return {
                               'status': 'Success',
                               'message': 'Запрос на восстановление пароля отправлен'
                           }, 202
                else:
                    return {
                               'status': 'Error',
                               'message': 'Запрос на восстановление пароля уже был отправлен ранее'
                           }, 406
            else:
                return {
                           'status': 'Error',
                           'message': 'Пользователя с заданным username не существует'
                       }, 400


change_password_request_model = ns.model('ChangePasswordRequest', {
    'key': fields.String(required=True, description='Ключ для смены пароля'),
    'password': fields.String(required=True, description='Новый пароль')
})
change_password_response_model = ns.model('ChangePasswordResponse', {
    'status': fields.String(description='Статус'),
    'message': fields.String(description='Сообщение'),
})


@ns.route('/change_password')
class UserChangePassword(Resource):
    @ns.doc(description='Смена пароля')
    @ns.expect(change_password_request_model)
    @ns.response(model=change_password_response_model, skip_none=True, code=400, description='Bad request')
    @ns.response(model=change_password_response_model, skip_none=True, code=406, description='Not Acceptable')
    @ns.marshal_with(change_password_response_model, skip_none=True, code=202, description='Accepted')
    def post(self):
        key = ns.payload['key']
        password = ns.payload['password']

        user_from_keys = Keys.get_or_none(Keys.key == key and Keys.type == KeysTypes.RECOVERY.value)
        if user_from_keys:
            if len(password) < PASSWORD_LENGTH:
                return {
                           'status': 'Error',
                           'message': f'Длина пароля не может быть меньше {PASSWORD_LENGTH} знаков(-а)'
                       }, 406

            hash = AuthManager.hash_password(password)
            with db.atomic():
                Users.update(password=hash).where(Users.id == user_from_keys.user_id).execute()
                Keys.delete().where(Keys.key == key and Keys.type == KeysTypes.RECOVERY.value).execute()
            return {
                       'status': 'Success',
                       'message': 'Пароль изменён'
                   }, 202
        else:
            return {
                       'status': 'Error',
                       'message': 'Заданного ключа не существует'
                   }, 400
