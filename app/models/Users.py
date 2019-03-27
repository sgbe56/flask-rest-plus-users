from datetime import datetime

from peewee import PrimaryKeyField, TextField, DateTimeField, BooleanField

from app.models.BaseDbModel import BaseDbModel


class Users(BaseDbModel):
    id = PrimaryKeyField(null=False)
    username = TextField(unique=True, null=False)
    password = TextField(null=False)
    reg_date = DateTimeField(default=datetime.now)
    active = BooleanField(default=False)


Users.create_table()
