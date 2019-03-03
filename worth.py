"""
Net worth data of some number of financial accounts via Personal Capital.
"""
from database import (
    get_secret,
    set_secret,
    get_net_worth_values,
    add_net_worth_value,
)
from personalcapital import (
    PersonalCapital,
    RequireTwoFactorException,
    TwoFactorVerificationModeEnum,
)
import json
import logging

REFRESH_HOURS = 12
logger = logging.getLogger()


class DataError(Exception):
    pass


def init(scheduler):
    username = get_secret('PC_USERNAME')
    if not username:
        logger.info('Worth not configured. Skipping update schedule.')
        return

    scheduler.add_job(
        _update_worth, 'interval', name='Refresh Worth', hours=REFRESH_HOURS
    )


def get_worth(limit):
    """Get net worth for the past several days."""
    values = get_net_worth_values() or [_update_worth()]
    return {'values': values[-limit:]}


def _update_worth():
    username = get_secret('PC_USERNAME')
    password = get_secret('PC_PASSWORD')
    data = _fetch_accounts_data(username, password)
    value = _calculate_worth(data)
    value = int(value * 100)  # Store as a fixed point decimal (or cents).
    add_net_worth_value(value)
    return value


def _calculate_worth(data):
    cash = data['spData']['cashAccountsTotal']
    credit = data['spData']['creditCardAccountsTotal']
    net = cash - credit
    logger.info('cash: %s, credit: %s, net: %s', cash, credit, net)
    return net


def _fetch_accounts_data(username, password, interactive=False):
    pc = PersonalCapital()
    session = get_secret('PC_SESSION')
    if session:
        pc.set_session(json.loads(session))
    try:
        pc.login(username, password)
    except RequireTwoFactorException:
        if not interactive:
            raise  # user will need to setup again
        pc.two_factor_challenge(TwoFactorVerificationModeEnum.SMS)
        code = input('Two factor required. Enter code from SMS: ')
        pc.two_factor_authenticate(TwoFactorVerificationModeEnum.SMS, code)
        pc.authenticate_password(password)
    response = pc.fetch('/newaccount/getAccounts2')
    response.raise_for_status()
    data = response.json()
    if data.get('spHeader', {}).get('success'):
        set_secret('PC_SESSION', json.dumps(pc.get_session()))
        return data
    errors = [e['message'] for e in data['spHeader'].get('errors')]
    raise DataError(' '.join(errors))


def _setup_creds():
    username = input('Personal Capital username: ')
    password = input('Personal Capital password: ')
    _fetch_accounts_data(username, password, interactive=True)
    set_secret('PC_USERNAME', username)
    set_secret('PC_PASSWORD', password)


def setup():
    """Interview the user for Personal Capital credentials."""
    success = False
    while not success:
        do_this = input('Setup Personal Capital [y/n]? ')
        if do_this.lower() == 'y':
            try:
                _setup_creds()
                success = True
                print('Personal Capital credentials stored.')
            except Exception as e:
                print('Personal Capital setup failed.', e)
        else:
            break
