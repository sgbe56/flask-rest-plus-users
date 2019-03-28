import peewee
from flask import Flask

from app.models.Config import Config

config = Config()
config.load('config.json')

db = peewee.SqliteDatabase(config.db_name)

from app.apis import api

app = Flask(__name__)
app.config['RESTPLUS_MASK_SWAGGER'] = False
app.config['SECRET_KEY'] = config.secret_key
