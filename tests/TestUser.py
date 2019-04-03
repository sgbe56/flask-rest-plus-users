import base64
import json

from app.models.Keys import Keys


class TestUser:
    def test_user_activate(self, client):
        url = '/api/user/activate'
        key = Keys.get_or_none(Keys.id == 1).key

        headers = {
            'Content-Type': "application/json"
        }
        data = {
            'key': key
        }

        request = client.post(url, data=json.dumps(data), headers=headers)
        response = json.loads(request.data)
        assert 'Учетная запись активирована' in response['message']

        request = client.post(url, data=json.dumps(data), headers=headers)
        response = json.loads(request.data)
        assert 'Заданного ключа не существует' in response['message']

    def test_user_auth(self, client):
        url = 'api/user'
        username = 'qwertyu'
        password = '12345678'
        basic_auth = base64.b64encode(str(username + ':' + password).encode('utf-8'))
        headers = {
            'Authorization': 'Basic ' + basic_auth.decode('utf-8'),
        }

        request = client.get(url, headers=headers)
        response = json.loads(request.data)
        assert username in response['user']['username']

        username = 'uytrewq'
        password = '87654321'
        basic_auth = base64.b64encode(str(username + ':' + password).encode('utf-8'))
        headers = {
            'Authorization': 'Basic ' + basic_auth.decode('utf-8'),
        }

        request = client.get(url, headers=headers)
        response = json.loads(request.data)
        assert 'Неверные логин или пароль' in response['message']

    def test_users(self, client):
        url = 'api/user/all'
        username = 'qwertyu'
        password = '12345678'
        basic_auth = base64.b64encode(str(username + ':' + password).encode('utf-8'))
        headers = {
            'Authorization': 'Basic ' + basic_auth.decode('utf-8'),
        }

        request = client.get(url, headers=headers)
        response = json.loads(request.data)
        assert 'Success' in response['status']

        username = 'uytrewq'
        password = '87654321'
        basic_auth = base64.b64encode(str(username + ':' + password).encode('utf-8'))
        headers = {
            'Authorization': 'Basic ' + basic_auth.decode('utf-8'),
        }

        request = client.get(url, headers=headers)
        response = json.loads(request.data)
        assert 'Неверные логин или пароль' in response['message']

    def test_restore_password(self, client):
        url = '/api/user/restore_password'
        headers = {
            'Content-Type': "application/json"
        }

        username = 'uytrewq'
        data = {
            'username': username
        }

        request = client.post(url, data=json.dumps(data), headers=headers)
        response = json.loads(request.data)
        assert 'Пользователя с заданным username не существует' in response['message']

        username = 'qwertyu'
        data = {
            'username': username
        }

        request = client.post(url, data=json.dumps(data), headers=headers)
        response = json.loads(request.data)
        assert 'Запрос на восстановление пароля отправлен' in response['message']

        request = client.post(url, data=json.dumps(data), headers=headers)
        response = json.loads(request.data)
        assert 'Запрос на восстановление пароля уже был отправлен ранее' in response['message']

    def test_change_password(self, client):
        url = '/api/user/change_password'
        headers = {
            'Content-Type': "application/json"
        }

        key = Keys.get_or_none(Keys.id == 1).key
        password = '1234567'
        data = {
            'key': key,
            'password': password
        }

        request = client.post(url, data=json.dumps(data), headers=headers)
        response = json.loads(request.data)
        assert 'Длина пароля не может быть меньше' in response['message']

        password = '12345678'
        data = {
            'key': key,
            'password': password
        }

        request = client.post(url, data=json.dumps(data), headers=headers)
        response = json.loads(request.data)
        assert 'Пароль изменён' in response['message']

        request = client.post(url, data=json.dumps(data), headers=headers)
        response = json.loads(request.data)
        assert 'Заданного ключа не существует' in response['message']
