import bcrypt

from app.models.Users import Users


class AuthManager:
    @staticmethod
    def register_user(username, password):
        hash = str(bcrypt.hashpw(str.encode(password), bcrypt.gensalt()), 'utf-8')
        if not Users.select(Users.username).where(
                Users.username == username):
            Users.create(username=username, password=hash)
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
