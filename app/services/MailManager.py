from flask_mail import Message

from app import mail, config


class MailManager:
    @staticmethod
    def send_mail(msg: Message):
        if config.client.send_mail:
            with mail.connect() as connection:
                connection.send(msg)
        else:
            print(msg.body)
