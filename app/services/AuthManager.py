from secrets import token_hex

import bcrypt

from app import db, TOKEN_LENGTH
from app.models.AccountActivationKeys import AccountActivationKeys
from app.models.Users import Users


class AuthManager:
    @staticmethod
    def hash_password(password):
        return str(bcrypt.hashpw(str.encode(password), bcrypt.gensalt()), 'utf-8')

    @staticmethod
    def register_user(username, password):
        hash = AuthManager.hash_password(password)
        with db.atomic():
            if not Users.select(Users.username).where(Users.username == username):
                user = Users.create(username=username, password=hash)
                AccountActivationKeys.create(user_id=user.id, key=token_hex(TOKEN_LENGTH))
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
