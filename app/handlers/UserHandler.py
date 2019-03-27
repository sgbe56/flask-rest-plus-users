from flask import session
from flask_restplus import Resource, fields

from app import api
from app.BasicAuthManager import auth_required
from app.models.Users import Users

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


@api.route('/api/user')
class UserData(Resource):
    @api.doc(description='Получение информации о пользователе')
    @api.response(model=auth_user_response_model, skip_none=True, code=401, description='Unauthorized')
    @api.marshal_with(auth_user_response_model, skip_none=True, code=202, description='Accepted')
    @auth_required
    def get(self):
        if session['username']:
            user = Users.select(Users.id, Users.username, Users.reg_date).where(
                Users.username == session['username'])[0]
            return {
                       'status': 'Success',
                       'user': {
                           'id': user.id,
                           'username': user.username,
                           'reg_date': str(user.reg_date)
                       }
                   }, 201


@api.route('/api/users')
class AllUsers(Resource):
    @api.doc(description='Получение списка всех пользователей')
    @api.response(model=auth_all_users_response_model, skip_none=True, code=401, description='Unauthorized')
    @api.marshal_with(auth_all_users_response_model, skip_none=True, code=202, description='Accepted')
    @auth_required
    def get(self):
        users = Users.select(Users.username)
        usernames = [user.username for user in users]
        return {'status': 'Success', 'users': usernames}, 202
