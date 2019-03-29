from cool_config import *


class Config(AbstractConfig):
    class client(Section):
        db_name = String
        secret_key = String
        password_length = Integer
        send_mail = Integer

    class mail(Section):
        mail_server = String
        mail_port = Integer
        mail_username = String
        mail_password = String
