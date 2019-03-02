from cryptography.fernet import Fernet
from peewee import SqliteDatabase, Model, CharField, DateField, IntegerField

from pathlib import Path

import datetime

HERE = Path(__file__).parent
DB_PATH = HERE / 'instance' / 'mirror.db'
KEY_PATH = HERE / 'instance' / 'mirror.key'

db = SqliteDatabase(None)
key = None


class EncryptedCharField(CharField):

    def db_value(self, value):
        value_bytes = self._fernet.encrypt(value.encode())
        return super().db_value(value_bytes.decode())

    def python_value(self, value):
        value_bytes = self._fernet.decrypt(value.encode())
        return super().python_value(value_bytes.decode())

    @property
    def _fernet(self):
        if not hasattr(self, '_fernet_'):
            self._fernet_ = Fernet(KEY_PATH.read_bytes())
        return self._fernet_


class Secret(Model):
    """A key, value pair, where the value is obfuscated."""
    key = CharField(unique=True)
    value = EncryptedCharField()

    class Meta:
        database = db


def get_secret(key):
    return Secret.get(Secret.key == key).value


def set_secret(key, value):
    return Secret.replace(key=key, value=value).execute()


class NetWorth(Model):
    """A net worth record."""
    date = DateField()
    value = IntegerField()  # value in whole dollars

    class Meta:
        database = db


def get_net_worth_values():
    return [nw.value for nw in NetWorth.select(NetWorth.value)]


def add_net_worth_value(value, date=None, max_days=30):
    date = date or datetime.date.today()
    cut_off = date - datetime.timedelta(days=max_days)
    NetWorth.delete().where(NetWorth.date <= cut_off).execute()
    entry = NetWorth.get_or_none(NetWorth.date == date)
    if entry:
        entry.value = value
    else:
        entry = NetWorth(date=date, value=value)
    entry.save()


def init():
    db.init(str(DB_PATH))
    db.connect()
    db.create_tables([Secret, NetWorth])
    db.close()
    if not KEY_PATH.exists():
        KEY_PATH.write_bytes(Fernet.generate_key())
