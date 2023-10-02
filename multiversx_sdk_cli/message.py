from typing import Dict

from multiversx_sdk_cli.accounts import Account


class SignableMessage:
    def __init__(self, message: str, account: Account) -> None:
        self.message = message
        self.account = account

    def sign(self) -> None:
        hex_signature = self.account.sign_message(self.message.encode())
        self.signature = bytes.fromhex(hex_signature)

    def to_dictionary(self) -> Dict[str, str]:
        return {
            "address": self.account.address.bech32(),
            "message": "0x" + self.message.encode().hex(),
            "signature": "0x" + self.signature.hex()
        }
