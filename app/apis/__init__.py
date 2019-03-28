from flask_restplus import Api

from .RegistrationAPI import api as registration_namespace
from .UserAPI import api as user_namespace

api = Api()

api.add_namespace(registration_namespace, path='/api/registration')
api.add_namespace(user_namespace, path='/api/user')