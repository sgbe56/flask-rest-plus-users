from peewee import Model

from app import db


class BaseDbModel(Model):
    class Meta:
        database = db
