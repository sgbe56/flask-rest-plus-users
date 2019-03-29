from secrets import token_hex
from typing import Union, Tuple

import bcrypt
from flask_mail import Message

from app import db, TOKEN_LENGTH, config
from app.models.Keys import Keys
from app.models.Users import Users
from app.services.MailManager import MailManager


class AuthManager:
    @staticmethod
    def hash_password(password: str) -> str:
        return str(bcrypt.hashpw(str.encode(password), bcrypt.gensalt()), 'utf-8')

    @staticmethod
    def register_user(username: str, password: str) -> bool:
        hash = AuthManager.hash_password(password)
        with db.atomic():
            if not Users.select(Users.username).where(Users.username == username):
                user = Users.create(username=username, password=hash)

                key = token_hex(TOKEN_LENGTH)
                Keys.create(user_id=user.id, key=key, type='activation')

                msg = Message(
                    body=f'Ключ для активации аккаунта: {key}',
                    subject='Account activating',
                    sender=config.mail.mail_username,
                    recipients=[username]
                )
                MailManager.send_mail(msg, False)
                return False
            else:
                return True

    @staticmethod
    def check_user(username: str, password: str) -> bool:
        try:
            hash = Users.get(Users.username == username).password
            return bcrypt.checkpw(bytes(password, 'utf-8'),
                                  bytes(hash, 'utf-8'))
        except Users.DoesNotExist:
            return False

    @staticmethod
    def user_is_active(username: str) -> Union[bool, Tuple]:
        user = Users.get_or_none(Users.username == username)
        if user:
            return user.active
        return {
                   'status': 'Error',
                   'message': 'Пользователя не существует'
               }, 406
