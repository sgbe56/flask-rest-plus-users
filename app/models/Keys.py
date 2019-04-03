from peewee import PrimaryKeyField, ForeignKeyField, TextField

from app.models.BaseDbModel import BaseDbModel
from app.models.Users import Users


class Keys(BaseDbModel):
    id = PrimaryKeyField(null=False)
    user_id = ForeignKeyField(model=Users, field=Users.id, null=False, on_delete='CASCADE')
    key = TextField(null=False)
    type = TextField(null=False)


Keys.create_table()
