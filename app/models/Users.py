from datetime import datetime

import peewee

from app import db


class Users(peewee.Model):
    id = peewee.PrimaryKeyField(null=False)
    username = peewee.TextField(unique=True, null=False)
    password = peewee.TextField(null=False)
    reg_date = peewee.DateTimeField(default=datetime.now)

    class Meta:
        database = db


Users.create_table()
