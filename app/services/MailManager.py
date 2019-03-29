from flask_mail import Message

from app import mail


class MailManager:
    @staticmethod
    def send_mail(msg: Message, send: bool = True):
        if send:
            with mail.connect() as connection:
                connection.send(msg)
        else:
            print(msg.body)
