from getpass import getpass

from personalcapital import (
    PersonalCapital,
    RequireTwoFactorException,
    TwoFactorVerificationModeEnum,
)

from .common import PC_PASSWORD, PC_SESSION, PC_USERNAME


def configure_plugin(config_context):
    db = config_context.db
    print("Worth Plugin Set Up")
    username = input("Personal Capital username: ").strip()
    password = getpass("Personal Capital password: ").strip()
    pc = PersonalCapital()
    try:
        pc.login(username, password)
    except RequireTwoFactorException:
        pc.two_factor_challenge(TwoFactorVerificationModeEnum.SMS)
        code = input("Two factor required. Enter code from SMS: ")
        pc.two_factor_authenticate(TwoFactorVerificationModeEnum.SMS, code)
        pc.authenticate_password(password)

    db[PC_USERNAME] = username
    db[PC_PASSWORD] = password

    # The session is a dict of the cookies set on authentication.
    db[PC_SESSION] = pc.get_session()
