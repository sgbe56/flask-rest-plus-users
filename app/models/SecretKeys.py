from peewee import PrimaryKeyField, TextField

from app.models.BaseDbModel import BaseDbModel


class SecretKeys(BaseDbModel):
    id = PrimaryKeyField(null=False)
    username = TextField(unique=True, null=False)
    key = TextField(null=False)


SecretKeys.create_table()
