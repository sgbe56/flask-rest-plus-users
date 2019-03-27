from flask import request
from flask_restplus import Resource, fields

from app import api, db
from app.models.SecretKeys import SecretKeys
from app.models.Users import Users

activate_user_response_model = api.model('ActivateUserResponse', {
    'status': fields.String(description='Статус'),
    'message': fields.String(description='Сообщение'),
})


@api.route('/api/user/activate')
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
