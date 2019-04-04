import json
import re

from _pytest.monkeypatch import MonkeyPatch

import app.services.MailManager


class TestRegistration:
    monkeypatch = MonkeyPatch()
    key = None

    def registration(self, client, username, password):
        url = '/api/registration'
        headers = {
            'Content-Type': "application/json"
        }
        data = {
            'username': username,
            'password': password
        }

        request = client.post(url, data=json.dumps(data), headers=headers)
        response = json.loads(request.data)
        return response

    def user_activate(self, client, str_to_assert):
        url = '/api/user/activate'
        headers = {
            'Content-Type': "application/json"
        }
        data = {
            'key': self.key
        }

        request = client.post(url, data=json.dumps(data), headers=headers)
        response = json.loads(request.data)
        return response

    def test_registration(self, client, monkeypatch):
        def mock_key(msg):
            result = re.search(r"(:\s)(\w+)", msg.body)
            if result and result.group(1) == ': ':
                self.key = result.group(2)

        monkeypatch.setattr(app.services.MailManager.MailManager, 'send_mail', mock_key)

        response = self.registration(client, 'qwertyu', '1234567')
        assert 'Длина пароля не может быть меньше' in response['message']
        response = self.registration(client, 'qwertyu', '12345678')
        assert 'Пользователь зарегистрирован' in response['message']
        response = self.registration(client, 'qwertyu', '12345678')
        assert 'Логин занят другим пользователем' in response['message']

        response = self.user_activate(client, '')
        assert 'Учетная запись активирована' in response['message']
        response = self.user_activate(client, '')
        assert 'Заданного ключа не существует' in response['message']
