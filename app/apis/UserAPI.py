from flask import session
from flask_restplus import Resource, fields, Namespace

from app import db
from app.services.BasicAuthManager import auth_required
from app.models.SecretKeys import SecretKeys
from app.models.Users import Users

api = Namespace('UserAPI', description='Работа пользователями')

user_fields = api.model('UserFields', {
    'id': fields.Integer(description='id пользователя'),
    'username': fields.String(description='Username пользователя'),
    'reg_date': fields.String(description='Дата регистарции пользователя'),
})

auth_user_response_model = api.model('AuthUserResponse', {
    'status': fields.String(description='Статус'),
    'message': fields.String(description='Сообщение'),
    'user': fields.Nested(user_fields, skip_none=True, description='Информация о пользователе')
})
auth_all_users_response_model = api.model('AuthAllUsersResponse', {
    'status': fields.String(description='Статус'),
    'message': fields.String(description='Сообщение'),
    'users': fields.List(cls_or_instance=fields.String, description='Список username всех пользователей')
})
activate_user_response_model = api.model('ActivateUserResponse', {
    'status': fields.String(description='Статус'),
    'message': fields.String(description='Сообщение'),
})


@api.route('')
class UserData(Resource):
    @api.doc(description='Получение информации о пользователе')
    @api.response(model=auth_user_response_model, skip_none=True, code=401, description='Unauthorized')
    @api.marshal_with(auth_user_response_model, skip_none=True, code=202, description='Accepted')
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


@api.route('/all')
class AllUsers(Resource):
    @api.doc(description='Получение списка всех пользователей')
    @api.response(model=auth_all_users_response_model, skip_none=True, code=401, description='Unauthorized')
    @api.response(model=auth_all_users_response_model, skip_none=True, code=403, description='Forbidden')
    @api.marshal_with(auth_all_users_response_model, skip_none=True, code=202, description='Accepted')
    @auth_required
    def get(self):
        with db.atomic():
            users = Users.select(Users.username)
            usernames = [user.username for user in users]
            return {'status': 'Success', 'users': usernames}, 202


@api.route('/activate')
class UserActivate(Resource):
    @api.doc(description='Активация учётной записи')
    @api.response(model=activate_user_response_model, skip_none=True, code=406, description='Not Acceptable')
    @api.marshal_with(activate_user_response_model, skip_none=True, code=202, description='Accepted')
    def post(self):
        key = api.payload['key']
        user_from_keys = SecretKeys.get_or_none(SecretKeys.key == key)
        if user_from_keys:
            with db.atomic():
                Users.update(active=True).where(Users.id == user_from_keys.user_id).execute()
                SecretKeys.delete().where(SecretKeys.key == key).execute()
            return {'status': 'Success', 'message': 'Учетная запись активирована'}
        else:
            return {'status': 'Error', 'message': 'Заданного ключа не существует'}
