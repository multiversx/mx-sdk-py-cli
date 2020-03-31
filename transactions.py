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
        print(data_json)
        return data_json


class PreparedTransaction(PlainTransaction):
    def __init__(self, transaction, signature):
        self.__dict__.update(transaction.payload())
        self.signature = signature

        if transaction.data:
            data_bytes = transaction.data.encode("utf-8")
            self.data = base64.b64encode(data_bytes).decode()

    def to_json(self):
        data_json = json.dumps(self.payload(), separators=(',', ':')).encode("utf8")
        return data_json


def prepare(args):
    workspace = args.workspace
    utils.ensure_folder(workspace)

    # "sender" taken from the PEM file
    sender_bytes = signing.get_address_from_pem(args.pem)
    sender_hex = sender_bytes.hex()

    transaction = PlainTransaction()
    transaction.nonce = int(args.nonce)
    transaction.value = args.value
    transaction.sender = sender_hex
    transaction.receiver = args.receiver
    transaction.gasPrice = int(args.gas_price)
    transaction.gasLimit = int(args.gas_limit)
    transaction.data = args.data

    transaction_payload = TransactionPayloadToSign(transaction)
    signature = signing.sign_transaction(transaction_payload, args.pem)
    signed_transaction = PreparedTransaction(transaction, signature)
    signed_transaction_json = signed_transaction.to_json().decode()

    prepared_transaction_filename = path.join(workspace, f"tx-{args.tag}.json")
    utils.write_file(prepared_transaction_filename, signed_transaction_json)
    logger.info(f"Saved prepared transaction to {prepared_transaction_filename}")


def send_prepared(args):
    tx_json = utils.read_file(args.tx).encode()

    logger.info(f"send_prepared:\n{tx_json}")

    url = f"{args.proxy}/transaction/send"
    raw_response = utils.post_json(url, data_json=tx_json)
    print(raw_response)
    pass
