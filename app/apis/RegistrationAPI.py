from flask_restplus import Resource, fields, Namespace

from app.services.AuthManager import AuthManager

api = Namespace('RegistrationAPI', description='Регистрация нового пользователя')

registration_request_model = api.model('RegistrationRequest', {
    'username': fields.String(required=True, description='Username пользователя'),
    'password': fields.String(required=True, description='Пароль пользователя')
})
registration_response_model = api.model('RegistrationResponse', {
    'status': fields.String(description='Статус'),
    'message': fields.String(description='Сообщение')
})


@api.route('')
class Registration(Resource):
    @api.doc(description='Регистрация нового пользователя')
    @api.expect(registration_request_model)
    @api.response(model=registration_response_model, code=400, description='Bad request')
    @api.response(model=registration_response_model, code=406, description='Not Acceptable')
    @api.marshal_with(registration_response_model, code=201, description='Object created')
    def post(self):
        if api.payload['username'] and api.payload['password']:
            username = api.payload['username']
            login_exist = AuthManager.register_user(username, api.payload['password'])
            if not login_exist:
                return {'status': 'Success', 'message': 'Пользователь зарегистрирован'}, 201
            else:
                return {'status': 'Error', 'message': 'Логин занят другим пользователем'}, 406
        else:
            return {'status': 'Error', 'message': 'Введены не все данные'}, 400
