import json
import re

from _pytest.monkeypatch import MonkeyPatch

import app.services.MailManager


class TestRestorePassword:
    monkeypatch = MonkeyPatch()
    key = None

    def restore_password(self, client, username):
        url = '/api/user/restore_password'
        headers = {
            'Content-Type': "application/json"
        }

        data = {
            'username': username
        }

        request = client.post(url, data=json.dumps(data), headers=headers)
        response = json.loads(request.data)
        return response

    def change_password(self, client, password):
        url = '/api/user/change_password'
        headers = {
            'Content-Type': "application/json"
        }

        data = {
            'key': self.key,
            'password': password
        }

        request = client.post(url, data=json.dumps(data), headers=headers)
        response = json.loads(request.data)
        return response

    def test_restore_password(self, client, monkeypatch):
        def mock_key(msg):
            result = re.search(r"(:\s)(\w+)", msg.body)
            if result and result.group(1) == ': ':
                self.key = result.group(2)

        monkeypatch.setattr(app.services.MailManager.MailManager, 'send_mail', mock_key)

        response = self.restore_password(client, 'uytrewq')
        assert 'Пользователя с заданным username не существует' in response['message']
        response = self.restore_password(client, 'qwertyu')
        assert 'Запрос на восстановление пароля отправлен' in response['message']
        response = self.restore_password(client, 'qwertyu')
        assert 'Запрос на восстановление пароля уже был отправлен ранее' in response['message']

        response = self.change_password(client, '1234567')
        assert 'Длина пароля не может быть меньше' in response['message']
        response = self.change_password(client, '12345678')
        assert 'Пароль изменён' in response['message']
        response = self.change_password(client, '12345678')
        assert 'Заданного ключа не существует' in response['message']
