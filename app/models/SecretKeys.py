from peewee import PrimaryKeyField, ForeignKeyField, TextField

from app.models.BaseDbModel import BaseDbModel
from app.models.Users import Users


class SecretKeys(BaseDbModel):
    id = PrimaryKeyField(null=False)
    user_id = ForeignKeyField(model=Users, field=Users.id, unique=True, null=False)
    key = TextField(null=False)


SecretKeys.create_table()
