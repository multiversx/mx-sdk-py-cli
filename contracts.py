import base64
import logging

from Cryptodome.Hash import keccak

from erdpy import config, errors, utils
from erdpy.accounts import Address
from erdpy.transactions import (PlainTransaction, PreparedTransaction,
                                TransactionPayloadToSign)
from erdpy.wallet import signing

logger = logging.getLogger("cli.deps")

VM_TYPE_ARWEN = "0500"


class SmartContract:
    def __init__(self, address=None, bytecode=None, metadata=None):
        self.address = Address(address)
        self.bytecode = bytecode
        self.metadata = metadata or CodeMetadata()

    def deploy(self, proxy, owner, arguments, gas_price, gas_limit, value, chain, version):
        self.owner = owner
        self.compute_address()
        transaction = self.prepare_deploy_transaction(owner, arguments, gas_price, gas_limit, value, chain, version)
        tx_hash = transaction.send(proxy)
        return tx_hash, self.address

    def prepare_deploy_transaction(self, owner, arguments, gas_price, gas_limit, value, chain, version):
        arguments = arguments or []
        gas_price = int(gas_price)
        gas_limit = int(gas_limit)
        value = str(value or "0")

        plain = PlainTransaction()
        plain.nonce = owner.nonce
        plain.value = value
        plain.sender = owner.address.bech32()
        plain.receiver = Address.zero().bech32()
        plain.gasPrice = gas_price
        plain.gasLimit = gas_limit
        plain.data = self.prepare_deploy_transaction_data(arguments)
        plain.chainID = chain
        plain.version = version

        payload = TransactionPayloadToSign(plain)
        signature = signing.sign_transaction(payload, owner.pem_file)
        prepared = PreparedTransaction(plain, signature)
        return prepared

    def prepare_deploy_transaction_data(self, arguments):
        tx_data = f"{self.bytecode}@{VM_TYPE_ARWEN}@{self.metadata.to_hex()}"

        for arg in arguments:
            tx_data += f"@{_prepare_argument(arg)}"

        return tx_data

    def compute_address(self):
        """
        8 bytes of zero + 2 bytes for VM type + 20 bytes of hash(owner) + 2 bytes of shard(owner)
        """
        owner_bytes = self.owner.address.pubkey()
        nonce_bytes = self.owner.nonce.to_bytes(8, byteorder="little")
        bytes_to_hash = owner_bytes + nonce_bytes
        address = keccak.new(digest_bits=256).update(bytes_to_hash).digest()
        address = bytes([0] * 8) + bytes([5, 0]) + address[10:30] + owner_bytes[30:]
        self.address = Address(address)

    def execute(self, proxy, caller, function, arguments, gas_price, gas_limit, value, chain, version):
        self.caller = caller
        transaction = self.prepare_execute_transaction(caller, function, arguments, gas_price, gas_limit, value, chain, version)
        tx_hash = transaction.send(proxy)
        return tx_hash

    def prepare_execute_transaction(self, caller, function, arguments, gas_price, gas_limit, value, chain, version):
        arguments = arguments or []
        gas_price = int(gas_price)
        gas_limit = int(gas_limit)
        value = str(value or "0")

        plain = PlainTransaction()
        plain.nonce = caller.nonce
        plain.value = value
        plain.sender = caller.address.bech32()
        plain.receiver = self.address.bech32()
        plain.gasPrice = gas_price
        plain.gasLimit = gas_limit
        plain.data = self.prepare_execute_transaction_data(function, arguments)
        plain.chainID = chain
        plain.version = version

        payload = TransactionPayloadToSign(plain)
        signature = signing.sign_transaction(payload, caller.pem_file)
        prepared = PreparedTransaction(plain, signature)
        return prepared

    def prepare_execute_transaction_data(self, function, arguments):
        tx_data = function

        for arg in arguments:
            tx_data += f"@{_prepare_argument(arg)}"

        return tx_data

    def upgrade(self, proxy, caller, arguments, gas_price, gas_limit, value, chain, version):
        self.caller = caller
        transaction = self.prepare_upgrade_transaction(caller, arguments, gas_price, gas_limit, value, chain, version)
        tx_hash = transaction.send(proxy)
        return tx_hash

    def prepare_upgrade_transaction(self, owner, arguments, gas_price, gas_limit, value, chain, version):
        arguments = arguments or []
        gas_price = int(gas_price or config.DEFAULT_GAS_PRICE)
        gas_limit = int(gas_limit)
        value = str(value or "0")

        plain = PlainTransaction()
        plain.nonce = owner.nonce
        plain.value = value
        plain.sender = owner.address.bech32()
        plain.receiver = self.address.bech32()
        plain.gasPrice = gas_price
        plain.gasLimit = gas_limit
        plain.data = self.prepare_upgrade_transaction_data(arguments)
        plain.chainID = chain
        plain.version = version

        payload = TransactionPayloadToSign(plain)
        signature = signing.sign_transaction(payload, owner.pem_file)
        prepared = PreparedTransaction(plain, signature)
        return prepared

    def prepare_upgrade_transaction_data(self, arguments):
        tx_data = f"upgradeContract@{self.bytecode}@{self.metadata.to_hex()}"

        for arg in arguments:
            tx_data += f"@{_prepare_argument(arg)}"

        return tx_data

    def query(self, proxy, function, arguments):
        arguments = arguments or []
        prepared_arguments = [_prepare_argument(argument) for argument in arguments]

        # TODO: move to proxy/core.py?
        payload = {
            "ScAddress": self.address.bech32(),
            "FuncName": function,
            "Args": prepared_arguments
        }

        response = proxy.query_contract(payload)
        return_data = response["data"]["ReturnData"]
        return [self._interpret_return_data(data) for data in return_data]

    def _interpret_return_data(self, data):
        try:
            as_bytes = base64.b64decode(data)
            as_hex = as_bytes.hex()
            as_number = int(as_hex, 16)

            result = utils.Object()
            result.base64 = data
            result.hex = as_hex
            result.number = as_number
            return result
        except Exception:
            logger.warn(f"Cannot interpret return data: {data}")
            return None


def _prepare_argument(argument):
    hex_prefix = "0X"
    as_string = str(argument).upper()

    if as_string.startswith(hex_prefix):
        return as_string[len(hex_prefix):]

    if not as_string.isnumeric():
        raise errors.UnknownArgumentFormat(as_string)

    as_number = int(as_string)
    as_hexstring = hex(as_number)[len(hex_prefix):]
    if len(as_hexstring) % 2 == 1:
        as_hexstring = "0" + as_hexstring

    return as_hexstring


class CodeMetadata:
    def __init__(self, upgradeable=False):
        self.upgradeable = upgradeable

    def to_hex(self):
        if self.upgradeable:
            return "0100"
        return "0000"
