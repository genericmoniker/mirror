import contextlib
from datetime import datetime
from unittest.mock import patch

import pytest

from .common import PC_CASHFLOW
from .worth import update_worth

# Mark all tests as asyncio:
pytestmark = pytest.mark.asyncio


@contextlib.contextmanager
def fetch_result(event_loop, cash, credit):
    with patch(
        "worth.worth._fetch_accounts_data",
        return_value=event_loop.create_future(),
    ) as fetch_mock:
        fetch_mock.return_value.set_result(_pc_response(cash, credit))
        yield


def _pc_response(cash, credit):
    return {"spData": {"cashAccountsTotal": cash, "creditCardAccountsTotal": credit}}


def _today_iso():
    """Get today in ISO format."""
    return datetime.now().date().isoformat()


async def test_values_converted_to_nearest_thousands(event_loop):
    with fetch_result(event_loop, cash=10500.99, credit=3000.05):
        result = await update_worth(db={}, limit=10)

    values = result.get("values")
    assert values == {_today_iso(): 8}


async def test_first_value_is_populated_when_the_database_is_empty(event_loop):
    with fetch_result(event_loop, cash=10000, credit=3000):
        result = await update_worth(db={}, limit=10)

    values = result.get("values")
    assert values == {_today_iso(): 7}


async def test_new_values_are_added_to_existing_ones(event_loop):
    with fetch_result(event_loop, cash=500000, credit=30000):
        db = {
            PC_CASHFLOW: {
                "2020-09-10": 100,
                "2020-09-11": 200,
                "2020-09-13": 300,
            }
        }
        result = await update_worth(db=db, limit=10)

    values = result.get("values")
    assert values == {
        "2020-09-10": 100,
        "2020-09-11": 200,
        "2020-09-13": 300,
        _today_iso(): 470,
    }


async def test_total_number_of_saved_values_is_capped(event_loop):
    with fetch_result(event_loop, cash=500000, credit=300000):
        db = {PC_CASHFLOW: {f"2020-07-{i:02}": i for i in range(1, 31)}}
        await update_worth(db=db, limit=10)

    assert len(db[PC_CASHFLOW]) == 30  # MAX_ITEMS
    items = list(db[PC_CASHFLOW].items())
    assert items[0][1] == 2  # the first value (1) gets knocked off
    assert items[-1][1] == 200  # the new value is added


async def test_new_values_replace_existing_values_for_the_same_day(event_loop):
    with fetch_result(event_loop, cash=5000, credit=7000):
        db = {
            PC_CASHFLOW: {
                _today_iso(): 100,
            }
        }
        result = await update_worth(db=db, limit=10)

    values = result.get("values")
    assert values == {_today_iso(): -2}


async def test_limit_retrieves_the_most_recent_values(event_loop):
    with fetch_result(event_loop, cash=10000, credit=3000):
        # Even if the original data is out-of-order.
        db = {
            PC_CASHFLOW: {
                "2020-09-10": 500,
                "2020-09-13": 300,
                "2020-09-11": 200,
            }
        }
        result = await update_worth(db=db, limit=2)

    values = result.get("values")
    assert values == {"2020-09-13": 300, _today_iso(): 7}
