from flask_restplus import Resource, fields, Namespace

from app import PASSWORD_LENGTH
from app.services.AuthManager import AuthManager

ns = Namespace('RegistrationAPI', path='/registration', description='Регистрация нового пользователя')

registration_request_model = ns.model('RegistrationRequest', {
    'username': fields.String(required=True, description='Username пользователя'),
    'password': fields.String(required=True, description='Пароль пользователя')
})
registration_response_model = ns.model('RegistrationResponse', {
    'status': fields.String(description='Статус'),
    'message': fields.String(description='Сообщение')
})


@ns.route('/')
class Registration(Resource):
    @ns.doc(description='Регистрация нового пользователя')
    @ns.expect(registration_request_model)
    @ns.response(model=registration_response_model, code=400, description='Bad request')
    @ns.response(model=registration_response_model, code=406, description='Not Acceptable')
    @ns.marshal_with(registration_response_model, code=201, description='Created')
    def post(self):
        username = ns.payload['username']
        password = ns.payload['password']

        if len(password) < PASSWORD_LENGTH:
            return {
                       'status': 'Error',
                       'message': f'Длина пароля не может быть меньше {PASSWORD_LENGTH} знаков(-а)'
                   }, 406

        login_exist = AuthManager.register_user(username, password)
        if not login_exist:
            return {
                        'status': 'Success',
                        'message': 'Пользователь зарегистрирован'
                    }, 201

        else:
            return {
                        'status': 'Error',
                        'message': 'Логин занят другим пользователем'
                    }, 406
