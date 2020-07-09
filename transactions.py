import json
import logging
from collections import OrderedDict
from os import path

from erdpy import config, utils
from erdpy.accounts import Address
from erdpy.wallet import pem, signing

logger = logging.getLogger("transactions")


class PlainTransaction:
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

    def payload(self):
        return self.__dict__.copy()


class TransactionPayloadToSign:
    def __init__(self, transaction):
        self.__dict__.update(transaction.payload())

        # When signing the transaction, we base64 encode the "Data" field
        if transaction.data:
            self.data = transaction.data

    def to_json(self):
        ordered_fields = OrderedDict()
        ordered_fields["nonce"] = self.nonce
        ordered_fields["value"] = self.value
        ordered_fields["receiver"] = self.receiver
        ordered_fields["sender"] = self.sender
        ordered_fields["gasPrice"] = self.gasPrice
        ordered_fields["gasLimit"] = self.gasLimit

        if self.data:
            ordered_fields["data"] = self.data

        if config.get_with_chain_and_version():
            ordered_fields["chainID"] = self.chainID
            ordered_fields["version"] = int(self.version)

        data_json = json.dumps(ordered_fields, separators=(',', ':')).encode("utf8")
        return data_json


class PreparedTransaction(PlainTransaction):
    def __init__(self, transaction=None, signature=None, dictionary=None):
        if dictionary:
            self._init_with_dictionary(dictionary)
        else:
            self._init_default(transaction, signature)

    def _init_with_dictionary(self, dictionary):
        self.__dict__.update(dictionary)

    def _init_default(self, transaction, signature):
        self.__dict__.update(transaction.payload())
        self.signature = signature

        if transaction.data:
            self.data = transaction.data

    @classmethod
    def from_file(cls, f):
        data_json = utils.read_file(f).encode()
        return cls.from_json(data_json)

    def save_to_file(self, f):
        utils.write_file(f, self.to_json())

    @classmethod
    def from_json(cls, json_data):
        dictionary = json.loads(json_data)
        # Handle both the old and the new format (wrapped tx or unwrapped)
        dictionary = dictionary.get("tx", dictionary)
        return cls.from_dictionary(dictionary)

    def to_json(self):
        data_json = json.dumps(self.to_dictionary(), indent=4)
        return data_json

    @classmethod
    def from_dictionary(cls, dictionary):
        return cls(dictionary=dictionary)

    def to_dictionary(self):
        return self.__dict__.copy()

    def send(self, proxy):
        logger.info(f"PreparedTransaction.send:\n{self.to_json()}")
        tx_hash = proxy.send_transaction(self.to_dictionary())
        logger.info(f"Hash: {tx_hash}")
        return tx_hash


class BunchOfTransactions:
    def __init__(self):
        self.transactions = []

    def add_prepared(self, transaction):
        self.transactions.append(transaction)

    def add(self, sender, receiver_address, nonce, value, data, gas_price, gas_limit):
        plain = PlainTransaction()
        plain.nonce = int(nonce)
        plain.value = str(value)
        plain.sender = sender.address.bech32()
        plain.receiver = receiver_address
        plain.gasPrice = gas_price
        plain.gasLimit = gas_limit
        plain.data = data

        payload = TransactionPayloadToSign(plain)
        signature = signing.sign_transaction(payload, sender.pem_file)
        prepared = PreparedTransaction(plain, signature)

        self.transactions.append(prepared)

    def add_in_sequence(self):
        pass

    def send(self, proxy):
        logger.info(f"BunchOfTransactions.send: {len(self.transactions)} transactions")
        payload = [transaction.to_dictionary() for transaction in self.transactions]
        num_sent, hashes = proxy.send_transactions(payload)
        logger.info(f"Sent: {num_sent}")
        logger.info(f"TxsHashes: {hashes}")
        return num_sent, hashes


def prepare(args):
    workspace = args.workspace
    utils.ensure_folder(workspace)

    prepared = do_prepare_transaction(args)
    prepared_filename = path.join(workspace, f"tx-{args.tag}.json")
    prepared.save_to_file(prepared_filename)
    logger.info(f"Saved prepared transaction to {prepared_filename}")


def do_prepare_transaction(args):
    # "sender" taken from the PEM file
    sender_bytes = pem.get_pubkey(args.pem)
    sender_bech32 = Address(sender_bytes).bech32()

    plain = PlainTransaction()
    plain.nonce = int(args.nonce)
    plain.value = args.value
    plain.sender = sender_bech32
    plain.receiver = args.receiver
    plain.gasPrice = int(args.gas_price)
    plain.gasLimit = int(args.gas_limit)
    plain.data = args.data
    plain.chainID = args.chain
    plain.version = int(args.version)

    payload = TransactionPayloadToSign(plain)
    signature = signing.sign_transaction(payload, args.pem)
    prepared = PreparedTransaction(plain, signature)
    return prepared
