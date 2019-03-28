import peewee
from flask import Flask

from app.models.Config import Config

config = Config()
config.load('config.json')

db = peewee.SqliteDatabase(config.client.db_name)

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