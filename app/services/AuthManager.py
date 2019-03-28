from secrets import token_hex

import bcrypt

from app import db
from app.models.SecretKeys import SecretKeys
from app.models.Users import Users

TOKEN_LENGHT = 16


class AuthManager:
    @staticmethod
    def register_user(username, password):
        hash = str(bcrypt.hashpw(str.encode(password), bcrypt.gensalt()), 'utf-8')
        with db.atomic():
            if not Users.select(Users.username).where(Users.username == username):
                user = Users.create(username=username, password=hash)
                SecretKeys.create(user_id=user.id, key=token_hex(TOKEN_LENGHT))
                return False
            else:
                return True

    @staticmethod
    def check_user(username, password):
        try:
            hash = Users.get(Users.username == username).password
            return bcrypt.checkpw(bytes(password, 'utf-8'),
                                  bytes(hash, 'utf-8'))
        except Users.DoesNotExist:
            return False

    @staticmethod
    def user_is_active(username):
        user = Users.get_or_none(Users.username == username)
        if user:
            return user.active
        return {'status': 'Error', 'message': 'Пользователя не существует'}
