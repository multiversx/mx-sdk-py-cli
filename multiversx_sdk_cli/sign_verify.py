from typing import Protocol

from multiversx_sdk import (
    Address,
    Message,
    MessageComputer,
    UserVerifier,
    ValidatorPublicKey,
    ValidatorSigner,
)


# fmt: off
class IAccount(Protocol):
    address: Address

    def sign_message(self, message: Message) -> bytes:
        ...
# fmt: off


class SignedMessage:
    def __init__(self, address: str, message: str, signature: str) -> None:
        self.address = address
        self.message = message

        hex_prefixes = ["0x", "0X"]
        signature_start_sequence = signature[0:2]

        if signature_start_sequence in hex_prefixes:
            signature = signature[2:]

        self.signature = signature

    def verify_user_signature(self) -> bool:
        verifiable_message = Message(self.message.encode())
        verifiable_message.signature = bytes.fromhex(self.signature)
        message_computer = MessageComputer()

        verifier = UserVerifier.from_address(Address.new_from_bech32(self.address))
        is_signed = verifier.verify(
            message_computer.compute_bytes_for_signing(verifiable_message),
            verifiable_message.signature,
        )
        return is_signed

    def verify_validator_signature(self) -> bool:
        validator_pubkey = ValidatorPublicKey(bytes.fromhex(self.address))
        return validator_pubkey.verify(
            self.message.encode(),
            bytes.fromhex(self.signature),
        )

    def to_dictionary(self) -> dict[str, str]:
        return {
            "address": self.address,
            "message": self.message,
            "signature": "0x" + self.signature,
        }


def sign_message(message: str, account: IAccount) -> SignedMessage:
    signature = account.sign_message(Message(message.encode()))
    return SignedMessage(account.address.to_bech32(), message, signature.hex())


def sign_message_by_validator(message: str, validator: ValidatorSigner) -> SignedMessage:
    signature = validator.sign(message.encode())
    return SignedMessage(validator.get_pubkey().hex(), message, signature.hex())
