from secrets import token_hex

from flask import session
from flask_mail import Message
from flask_restplus import Resource, fields, Namespace

from app import db, TOKEN_LENGTH, mail, config
from app.models.AccountActivationKeys import AccountActivationKeys
from app.models.PasswordRecoveryKeys import PassowordRecoveryKeys
from app.models.Users import Users
from app.services.AuthManager import AuthManager
from app.services.BasicAuthManager import auth_required

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
    'key': fields.String(description='Ключ активации пользователя')
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
        user_from_keys = AccountActivationKeys.get_or_none(AccountActivationKeys.key == key)
        if user_from_keys:
            with db.atomic():
                Users.update(active=True).where(Users.id == user_from_keys.user_id).execute()
                AccountActivationKeys.delete().where(AccountActivationKeys.key == key).execute()
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
    'username': fields.String(description='Username пользователя'),
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
                user_from_keys = PassowordRecoveryKeys.get_or_none(PassowordRecoveryKeys.user_id == user.id)
                if not user_from_keys:
                    PassowordRecoveryKeys.create(user_id=user.id, key=token_hex(TOKEN_LENGTH))
                    # with mail.connect() as connection:
                    #     msg = Message(body='Test',
                    #                   subject='Password recover',
                    #                   sender=config.mail.mail_username,
                    #                   recipients=[username]
                    #                   )
                    #     connection.send(msg)
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
    'key': fields.String(description='Ключ для смены пароля'),
    'password': fields.String(description='Новый пароль')
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
    @ns.marshal_with(change_password_response_model, skip_none=True, code=202, description='Accepted')
    def post(self):
        key = ns.payload['key']
        user_from_keys = PassowordRecoveryKeys.get_or_none(PassowordRecoveryKeys.key == key)
        if user_from_keys:
            hash = AuthManager.hash_password(ns.payload['password'])
            with db.atomic():
                Users.update(password=hash).where(Users.id == user_from_keys.user_id).execute()
                PassowordRecoveryKeys.delete().where(PassowordRecoveryKeys.key == key).execute()
            return {
                       'status': 'Success',
                       'message': 'Пароль изменён'
                   }, 202
        else:
            return {
                       'status': 'Error',
                       'message': 'Заданного ключа не существует'
                   }, 400
