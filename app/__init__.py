import peewee
from flask import Flask

from app.models.Config import Config

TOKEN_LENGTH = 16

config = Config()
config.load('config.json')

PASSWORD_LENGTH = config.client.password_length

if not config.client.is_test:
    db = peewee.SqliteDatabase(config.client.db_name, pragmas={'foreign_keys': 1})
else:
    db = peewee.SqliteDatabase('tests/test_db.db', pragmas={'foreign_keys': 1})

from flask_mail import Mail

mail = Mail()

from app.apis import api

app = Flask(__name__)

app.url_map.strict_slashes = False

app.config['RESTPLUS_MASK_SWAGGER'] = False
app.config['SECRET_KEY'] = config.client.secret_key

app.config['MAIL_USE_SSL'] = True
app.config['MAIL_SERVER'] = config.mail.mail_server
app.config['MAIL_PORT'] = config.mail.mail_port
app.config['MAIL_USERNAME'] = config.mail.mail_username
app.config['MAIL_PASSWORD'] = config.mail.mail_password
app.config['MAIL_DEFAULT_SENDER'] = config.mail.mail_username

api.init_app(app)
mail.init_app(app)
