from flask_restplus import Api

from .RegistrationAPI import ns as registration_namespace
from .UserAPI import ns as user_namespace

api = Api(prefix='/api', doc='/docs')

api.add_namespace(registration_namespace)
api.add_namespace(user_namespace)
