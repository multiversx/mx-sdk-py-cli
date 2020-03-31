import base64
import json
import logging
from os import path

from erdpy import utils
from erdpy.wallet import signing
from collections import OrderedDict


logger = logging.getLogger("transactions")


class PlainTransaction:
    def __init__(self):
        self.nonce = 0
        self.value = ""
        self.sender = ""
        self.receiver = ""
        self.gasPrice = 0
        self.gasLimit = 0
        self.data = ""

    def payload(self):
        return self.__dict__.copy()


class TransactionPayloadToSign:
    def __init__(self, transaction):
        self.__dict__.update(transaction.payload())

        receiver_bytes = bytes.fromhex(transaction.receiver)
        receiver_base64 = base64.b64encode(receiver_bytes).decode()
        self.receiver = receiver_base64

        sender_bytes = bytes.fromhex(transaction.sender)
        sender_base64 = base64.b64encode(sender_bytes).decode()
        self.sender = sender_base64

        if transaction.data:
            data_bytes = transaction.data.encode("utf-8")
            data_base64 = base64.b64encode(data_bytes).decode()
            self.data = data_base64

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
            data_bytes = transaction.data.encode("utf-8")
            self.data = base64.b64encode(data_bytes).decode()

    @classmethod
    def from_file(cls, filename):
        data_json = utils.read_file(filename).encode()
        return cls.from_json(data_json)

    def save_to_file(self, filename):
        utils.write_file(filename, self.to_json())

    @classmethod
    def from_json(cls, json_data):
        dictionary = json.loads(json_data)
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


def prepare(args):
    workspace = args.workspace
    utils.ensure_folder(workspace)

    # "sender" taken from the PEM file
    sender_bytes = signing.get_address_from_pem(args.pem)
    sender_hex = sender_bytes.hex()

    plain = PlainTransaction()
    plain.nonce = int(args.nonce)
    plain.value = args.value
    plain.sender = sender_hex
    plain.receiver = args.receiver
    plain.gasPrice = int(args.gas_price)
    plain.gasLimit = int(args.gas_limit)
    plain.data = args.data

    payload = TransactionPayloadToSign(plain)
    signature = signing.sign_transaction(payload, args.pem)
    prepared = PreparedTransaction(plain, signature)

    prepared_filename = path.join(workspace, f"tx-{args.tag}.json")
    prepared.save_to_file(prepared_filename)
    logger.info(f"Saved prepared transaction to {prepared_filename}")
