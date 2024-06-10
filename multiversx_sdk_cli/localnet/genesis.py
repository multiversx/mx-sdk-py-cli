from multiversx_sdk_cli.localnet import wallets


def get_owner_of_genesis_contracts():
    users = wallets.get_users()
    return users["alice"]


def is_last_user(nickname: str) -> bool:
    return nickname == "mike"
