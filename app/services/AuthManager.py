import bcrypt

from secrets import token_hex

from app.models.SecretKeys import SecretKeys
from app.models.Users import Users

TOKEN_LENGHT = 16


class AuthManager:
    @staticmethod
    def register_user(username, password):
        hash = str(bcrypt.hashpw(str.encode(password), bcrypt.gensalt()), 'utf-8')
        if not Users.select(Users.username).where(
                Users.username == username):
            Users.create(username=username, password=hash)
            SecretKeys.create(username=username, key=token_hex(TOKEN_LENGHT))
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
