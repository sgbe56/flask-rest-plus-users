from flask import session, request
from flask_restplus import Resource, fields

from app import api, db
from app.services.BasicAuthManager import auth_required
from app.models.SecretKeys import SecretKeys
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


@api.route('/api/user')
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
