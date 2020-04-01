import hashlib
from erdpy import errors, config
from erdpy.transactions import PlainTransaction, TransactionPayloadToSign, PreparedTransaction
from erdpy.wallet import signing


class SmartContract:
    def __init__(self, address=None, bytecode=None):
        self.address = address
        self.bytecode = bytecode

    def deploy(self, proxy, owner, arguments, gas_price, gas_limit):
        self.owner = owner
        self.owner.sync_nonce(proxy)
        self.compute_address()
        transaction = self.prepare_deploy_transaction(owner, arguments, gas_price, gas_limit)
        tx_hash = transaction.send(proxy)
        return tx_hash, self.address

    def prepare_deploy_transaction(self, owner, arguments, gas_price, gas_limit):
        arguments = arguments or []
        gas_price = int(gas_price or config.DEFAULT_GASPRICE)
        gas_limit = int(gas_limit or config.DEFAULT_GASLIMIT)

        plain = PlainTransaction()
        plain.nonce = owner.nonce
        plain.value = "0"   # TODO
        plain.sender = owner.address
        plain.receiver = "0" * 64
        plain.gasPrice = gas_price
        plain.gasLimit = gas_limit
        plain.data = self.prepare_deploy_transaction_data(arguments)

        payload = TransactionPayloadToSign(plain)
        signature = signing.sign_transaction(payload, owner.pem_file)
        prepared = PreparedTransaction(plain, signature)
        return prepared

    def prepare_deploy_transaction_data(self, arguments):
        tx_data = self.bytecode

        for arg in arguments:
            tx_data += f"@{_prepare_argument(arg)}"

        return tx_data

    def compute_address(self):
        """
        8 bytes of zero + 2 bytes for VM type + 20 bytes of hash(owner) + 2 bytes of shard(owner)
        """
        owner_bytes = self.owner.address_bytes()
        nonce_bytes = self.owner.nonce.to_bytes(8, byteorder="little")
        bytes_to_hash = owner_bytes + nonce_bytes
        address = hashlib.sha3_256(bytes_to_hash).digest()
        address = bytes([0] * 8) + bytes([0, 5]) + address[10:30] + owner_bytes[30:]
        self.address = address.hex()

    def execute(self, proxy, caller, function, arguments, gas_price, gas_limit):
        self.caller = caller
        self.caller.sync_nonce(proxy)
        transaction = self.prepare_execute_transaction(caller, function, arguments, gas_price, gas_limit)
        tx_hash = transaction.send(proxy)
        return tx_hash

    def prepare_execute_transaction(self, caller, function, arguments, gas_price, gas_limit):
        arguments = arguments or []
        gas_price = int(gas_price or config.DEFAULT_GASPRICE)
        gas_limit = int(gas_limit or config.DEFAULT_GASLIMIT)

        plain = PlainTransaction()
        plain.nonce = caller.nonce
        plain.value = "0"   # TODO
        plain.sender = caller.address
        plain.receiver = self.address
        plain.gasPrice = gas_price
        plain.gasLimit = gas_limit
        plain.data = self.prepare_execute_transaction_data(function, arguments)

        payload = TransactionPayloadToSign(plain)
        signature = signing.sign_transaction(payload, caller.pem_file)
        prepared = PreparedTransaction(plain, signature)
        return prepared

    def prepare_execute_transaction_data(self, function, arguments):
        tx_data = function

        for arg in arguments:
            tx_data += f"@{_prepare_argument(arg)}"

        return tx_data


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
