from flask import session
from flask_restplus import Resource, fields, Namespace

from app import db
from app.models.SecretKeys import SecretKeys
from app.models.Users import Users
from app.services.BasicAuthManager import auth_required

ns = Namespace('UserAPI', path='/user', description='Работа пользователями')

activate_user_request_model = ns.model('ActivateUserRequestModel', {
    'key': fields.String(description='Ключ активации пользователя')
})
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
auth_all_users_response_model = ns.model('AuthAllUsersResponse', {
    'status': fields.String(description='Статус'),
    'message': fields.String(description='Сообщение'),
    'users': fields.List(cls_or_instance=fields.String, description='Список username всех пользователей')
})
activate_user_response_model = ns.model('ActivateUserResponse', {
    'status': fields.String(description='Статус'),
    'message': fields.String(description='Сообщение'),
})


@ns.route('/')
class UserData(Resource):
    @ns.doc(description='Получение информации о пользователе')
    @ns.response(model=auth_user_response_model, skip_none=True, code=401, description='Unauthorized')
    @ns.marshal_with(auth_user_response_model, skip_none=True, code=202, description='Accepted')
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
                   }, 202


@ns.route('/all')
class AllUsers(Resource):
    @ns.doc(description='Получение списка всех пользователей')
    @ns.response(model=auth_all_users_response_model, skip_none=True, code=401, description='Unauthorized')
    @ns.response(model=auth_all_users_response_model, skip_none=True, code=403, description='Forbidden')
    @ns.marshal_with(auth_all_users_response_model, skip_none=True, code=202, description='Accepted')
    @auth_required
    def get(self):
        with db.atomic():
            users = Users.select(Users.username)
            usernames = [user.username for user in users]
            return {'status': 'Success', 'users': usernames}, 202


@ns.route('/activate')
class UserActivate(Resource):
    @ns.doc(description='Активация учётной записи')
    @ns.expect(activate_user_request_model)
    @ns.response(model=activate_user_response_model, skip_none=True, code=406, description='Not Acceptable')
    @ns.marshal_with(activate_user_response_model, skip_none=True, code=202, description='Accepted')
    def post(self):
        key = ns.payload['key']
        user_from_keys = SecretKeys.get_or_none(SecretKeys.key == key)
        if user_from_keys:
            with db.atomic():
                Users.update(active=True).where(Users.id == user_from_keys.user_id).execute()
                SecretKeys.delete().where(SecretKeys.key == key).execute()
            return {'status': 'Success', 'message': 'Учетная запись активирована'}
        else:
            return {'status': 'Error', 'message': 'Заданного ключа не существует'}
