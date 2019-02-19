from database import EncryptedCharField

from peewee import Model, SqliteDatabase
import pytest

db = SqliteDatabase(':memory:')


class EncryptedModel(Model):
    field = EncryptedCharField()

    class Meta:
        database = db


@pytest.fixture(autouse=True)
def db_init():
    db.connect()
    db.create_tables([EncryptedModel])
    yield
    db.close()


def test_encryption_round_trip():
    text = '↕ Hello ↕'
    m = EncryptedModel(field=text)
    m.save()
    m = EncryptedModel.get()
    assert m.field == text
