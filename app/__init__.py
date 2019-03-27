import peewee
from flask import Flask
from flask_restplus import Api

from app.models.Config import Config

config = Config()
config.load('config_dev.json')

db = peewee.SqliteDatabase(config.db_name)

app = Flask(__name__)
app.config['RESTPLUS_MASK_SWAGGER'] = False
app.config['SECRET_KEY'] = config.secret_key
api = Api(app, validate=True)

from app.handlers import RegistrationHandler, UserHandler, UsersHandler, UserActivateHandler
