from flask_restplus import Resource, fields

from app import api, db
from app.models import Users
from app.services.BasicAuthManager import auth_required

auth_all_users_response_model = api.model('AuthAllUsersResponse', {
    'status': fields.String(description='Статус'),
    'message': fields.String(description='Сообщение'),
    'users': fields.List(cls_or_instance=fields.String, description='Список username всех пользователей')
})


@api.route('/api/users')
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
