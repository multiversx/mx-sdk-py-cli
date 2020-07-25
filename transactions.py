import base64
from erdpy.proxy.core import ElrondProxy
from erdpy import errors
import json
import logging
from binascii import unhexlify
from collections import OrderedDict
from os import path
from typing import Any, Dict

from erdpy import utils
from erdpy.accounts import Account
from erdpy.wallet import signing

logger = logging.getLogger("transactions")


class Transaction:
    def __init__(self):
        self.nonce = 0
        self.value = "0"
        self.sender = ""
        self.receiver = ""
        self.gasPrice = 0
        self.gasLimit = 0
        self.data = ""
        self.chainID = ""
        self.version = 0
        self.signature = ""

    # The data field is base64-encoded. erdpy only supports utf-8 "data" at this moment.
    def data_encoded(self) -> str:
        data_bytes = self.data.encode("utf-8")
        data_base64 = base64.b64encode(data_bytes).decode()
        return data_base64

    def serialize_for_signing(self) -> bytes:
        dictionary = self.to_dictionary()
        serialized = json.dumps(dictionary, separators=(',', ':')).encode("utf8")
        return serialized

    @classmethod
    def load_from_file(cls, f: Any):
        data_json: bytes = utils.read_file(f).encode()
        fields = json.loads(data_json).get("tx", None)
        instance = cls()
        instance.__dict__.update(fields)
        return instance

    def save_to_file(self, f: Any):
        utils.write_file(f, self.to_json())

    def to_json(self):
        data_json = json.dumps(self.to_dictionary(), indent=4)
        return data_json

    def send(self, proxy: Any):
        if not self.signature:
            raise errors.TransactionIsNotSigned()

        logger.info(f"Transaction.send: nonce={self.nonce}")

        dictionary = self.to_dictionary()
        tx_hash = proxy.send_transaction(dictionary)
        logger.info(f"Hash: {tx_hash}")
        return tx_hash

    def to_dictionary(self) -> Dict[str, Any]:
        dictionary: Dict[str, Any] = OrderedDict()
        dictionary["nonce"] = self.nonce
        dictionary["value"] = self.value
        dictionary["receiver"] = self.receiver
        dictionary["sender"] = self.sender
        dictionary["gasPrice"] = self.gasPrice
        dictionary["gasLimit"] = self.gasLimit

        if self.data:
            dictionary["data"] = self.data_encoded()

        dictionary["chainID"] = self.chainID
        dictionary["version"] = int(self.version)

        if self.signature:
            dictionary["signature"] = self.signature

        return dictionary


class BunchOfTransactions:
    def __init__(self):
        self.transactions = []

    def add_prepared(self, transaction: Transaction):
        self.transactions.append(transaction)

    def add(self, sender: Account, receiver_address: str, nonce: Any, value: Any, data: str, gas_price: int, gas_limit: int, chain: str, version: int):
        tx = Transaction()
        tx.nonce = int(nonce)
        tx.value = str(value)
        tx.sender = sender.address.bech32()
        tx.receiver = receiver_address
        tx.gasPrice = gas_price
        tx.gasLimit = gas_limit
        tx.data = data
        tx.chainID = chain
        tx.version = version

        seed: bytes = unhexlify(sender.private_key_seed)
        tx.signature = signing.sign_transaction_with_seed(tx, seed)
        self.transactions.append(tx)

    def add_in_sequence(self):
        pass

    def send(self, proxy: ElrondProxy):
        logger.info(f"BunchOfTransactions.send: {len(self.transactions)} transactions")
        payload = [transaction.to_dictionary() for transaction in self.transactions]
        num_sent, hashes = proxy.send_transactions(payload)
        logger.info(f"Sent: {num_sent}")
        logger.info(f"TxsHashes: {hashes}")
        return num_sent, hashes


def prepare(args: Any) -> None:
    workspace = args.workspace
    utils.ensure_folder(workspace)

    tx = do_prepare_transaction(args)
    prepared_filename = path.join(workspace, f"tx-{args.tag}.json")
    tx.save_to_file(prepared_filename)
    logger.info(f"Saved prepared transaction to {prepared_filename}")


def do_prepare_transaction(args: Any) -> Transaction:
    account = Account()
    if args.pem:
        account = Account(pem_file=args.pem)
    elif args.keyfile and args.passfile:
        account = Account(key_file=args.keyfile, pass_file=args.passfile)

    tx = Transaction()
    tx.nonce = int(args.nonce)
    tx.value = args.value
    tx.sender = account.address.bech32()
    tx.receiver = args.receiver
    tx.gasPrice = int(args.gas_price)
    tx.gasLimit = int(args.gas_limit)
    tx.data = args.data
    tx.chainID = args.chain
    tx.version = int(args.version)

    seed: bytes = unhexlify(account.private_key_seed)
    tx.signature = signing.sign_transaction_with_seed(tx, seed)
    return tx
