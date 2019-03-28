from peewee import PrimaryKeyField, ForeignKeyField, TextField

from app.models.BaseDbModel import BaseDbModel
from app.models.Users import Users


class PassowordRecoveryKeys(BaseDbModel):
    id = PrimaryKeyField(null=False)
    user_id = ForeignKeyField(model=Users, field=Users.id, unique=True, null=False, on_delete='CASCADE')
    key = TextField(null=False)


PassowordRecoveryKeys.create_table()
