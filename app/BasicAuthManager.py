from functools import wraps

from flask import request, session

from app.AuthManager import AuthManager


def auth_required(handler):
    @wraps(handler)
    def wrapper(*args, **kwargs):
        auth = request.authorization
        if not auth or not AuthManager.check_user(auth.username, auth.password):
            return {'status': 'Error', 'message': 'Неверные логин или пароль'}, 401
        session['username'] = auth.username
        return handler(*args, **kwargs)

    return wrapper
