import logging
from datetime import datetime

from personalcapital import PersonalCapital

from .common import PC_CASHFLOW, PC_PASSWORD, PC_SESSION, PC_USERNAME

_logger = logging.getLogger(__name__)

MAX_VALUES = 30


def update_worth(db, limit):
    """Update the worth, returning at most limit days of history.

    :param db: database set up with PC credentials.
    :param limit: max number of days for which to retrieve history.
    :raise RequireTwoFactorException: if the user needs to re-authenticate.
    :raise DataError: if the account data could not be retrieved.
    """
    data = _fetch_accounts_data(db)

    value = _calculate_cashflow_worth(data)
    value = round(value / 1000)  # Store $ in whole thousands.

    existing_data = db.get(PC_CASHFLOW, {})
    now = datetime.now()
    today = now.date().isoformat()
    existing_data[today] = value
    existing_data = _limit_values(existing_data, MAX_VALUES)
    db[PC_CASHFLOW] = existing_data

    return {
        "values": _limit_values(existing_data, limit),
        "lastUpdate": now.isoformat(),
    }


def _limit_values(data, limit):
    return {k: v for k, v in sorted(data.items())[-limit:]}


class DataError(Exception):
    pass


def _calculate_cashflow_worth(data):
    cash = data["spData"]["cashAccountsTotal"]
    credit = data["spData"]["creditCardAccountsTotal"]
    net = cash - credit
    _logger.info("cash: %s, credit: %s, net: %s", cash, credit, net)
    return net


def _fetch_accounts_data(db):
    username = db.get(PC_USERNAME)
    password = db.get(PC_PASSWORD)
    session = db.get(PC_SESSION)
    pc = PersonalCapital()
    pc.set_session(session)
    pc.login(username, password)
    response = pc.fetch("/newaccount/getAccounts2")
    response.raise_for_status()
    data = response.json()
    if data.get("spHeader", {}).get("success"):
        db[PC_SESSION] = pc.get_session()
        return data
    errors = [e["message"] for e in data["spHeader"].get("errors")]
    raise DataError(" ".join(errors))