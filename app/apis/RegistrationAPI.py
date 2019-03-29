from flask_mail import Message
from flask_restplus import Resource, fields, Namespace

from app import mail, config
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
        if ns.payload['username'] and ns.payload['password']:
            username = ns.payload['username']
            login_exist = AuthManager.register_user(username, ns.payload['password'])
            if not login_exist:
                # with mail.connect() as connection:
                #     msg = Message(body='Test',
                #                   subject='Account activating',
                #                   sender=config.mail.mail_username,
                #                   recipients=[username]
                #                   )
                #     connection.send(msg)
                return {
                           'status': 'Success',
                           'message': 'Пользователь зарегистрирован'
                       }, 201
            else:
                return {
                           'status': 'Error',
                           'message': 'Логин занят другим пользователем'
                       }, 406
        else:
            return {
                       'status': 'Error',
                       'message': 'Введены не все данные'
                   }, 400
