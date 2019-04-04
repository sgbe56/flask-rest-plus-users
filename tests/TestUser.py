import base64
import json


class TestUser:
    def get_user(self, client, username, password):
        url = 'api/user'
        basic_auth = base64.b64encode(str(username + ':' + password).encode('utf-8'))
        headers = {
            'Authorization': 'Basic ' + basic_auth.decode('utf-8'),
        }

        request = client.get(url, headers=headers)
        response = json.loads(request.data)
        return response

    def get_users(self, client, username, password):
        url = 'api/user/all'
        basic_auth = base64.b64encode(str(username + ':' + password).encode('utf-8'))
        headers = {
            'Authorization': 'Basic ' + basic_auth.decode('utf-8'),
        }

        request = client.get(url, headers=headers)
        response = json.loads(request.data)
        return response

    def test_user(self, client):
        response = self.get_user(client, 'qwertyu', '1234567')
        assert 'Неверные логин или пароль' in response['message']
        response = self.get_user(client, 'qwertyu', '12345678')
        assert 'qwertyu' in response['user']['username']

        response = self.get_users(client, 'uytrewq', '87654321')
        assert 'Неверные логин или пароль' in response['message']
        response = self.get_users(client, 'qwertyu', '12345678')
        assert 'Success' in response['status']
