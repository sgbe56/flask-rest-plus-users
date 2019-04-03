import json


class TestRegistration:
    def test_registration(self, client):
        url = '/api/registration'
        username = 'qwertyu'
        password = '1234567'

        headers = {
            'Content-Type': "application/json"
        }

        data = {
            'username': username,
            'password': password
        }

        request = client.post(url, data=json.dumps(data), headers=headers)
        response = json.loads(request.data)
        assert 'Длина пароля не может быть меньше' in response['message']

        password = '12345678'
        data = {
            'username': username,
            'password': password
        }

        request = client.post(url, data=json.dumps(data), headers=headers)
        response = json.loads(request.data)
        assert 'Пользователь зарегистрирован' in response['message']

        request = client.post(url, data=json.dumps(data), headers=headers)
        response = json.loads(request.data)
        assert 'Логин занят другим пользователем' in response['message']
