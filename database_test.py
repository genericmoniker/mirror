from database import (
    db,
    init,
    EncryptedCharField,
    NetWorth,
    add_net_worth_value,
    get_net_worth_values,
)

from peewee import Model
import pytest

from datetime import date


class EncryptedModel(Model):
    field = EncryptedCharField()

    class Meta:
        database = db


@pytest.fixture(autouse=True)
def db_init():
    db.init(':memory:')
    db.connect()
    db.create_tables([EncryptedModel, NetWorth])
    yield
    db.close()


def test_encryption_round_trip():
    text = '↕ Hello ↕'
    m = EncryptedModel(field=text)
    m.save()
    m = EncryptedModel.get()
    assert m.field == text


def test_worth_table_stores_data():
    add_net_worth_value(10000, date(2019, 2, 26), 3)
    values = get_net_worth_values()
    assert values == [10000]


def test_worth_table_overwrites_same_date():
    add_net_worth_value(10000, date(2019, 2, 26), 3)
    add_net_worth_value(20000, date(2019, 2, 26), 3)
    values = get_net_worth_values()
    assert values == [20000]


def test_worth_table_truncated_on_insert():
    add_net_worth_value(10000, date(2019, 2, 26), 3)
    add_net_worth_value(20000, date(2019, 2, 27), 3)
    add_net_worth_value(30000, date(2019, 2, 28), 3)
    add_net_worth_value(40000, date(2019, 3, 1), 3)
    add_net_worth_value(50000, date(2019, 3, 2), 3)
    values = get_net_worth_values()
    assert values == [30000, 40000, 50000]
