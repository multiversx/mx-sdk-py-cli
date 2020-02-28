import base64

from erdpy.proxy.tx_types import TxTypes
from erdpy import utils, errors
from erdpy.projects import load_project


def prepare_argument(argument):
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


class TransactionCostEstimator:
    def __init__(self, proxy_url):
        self.proxy = proxy_url

    def estimate_tx_cost(self, arguments):
        tx_type = arguments.tx_type

        if tx_type == TxTypes.MOVE_BALANCE:
            self.__estimate_move_balance(arguments.data)
        elif tx_type == TxTypes.SC_DEPLOY:
            self.__estimate_sc_deploy(arguments.path)
        else:
            self.__estimate_sc_call(arguments.sc_address, arguments.function, arguments.arguments)

    def __estimate_move_balance(self, data):
        sender = "e3784da068cca901c0c629b304d024eb777fdf604dd8f6b5c0dc0c7f75877473"
        receiver = "e3784da068cca901c0c629b304d024eb777fdf604dd8f6b5c0dc0c7f75877471"
        data = data or ""
        data_bytes = list(bytes(data, "ascii"))

        self.__sent_tx(sender, receiver, data_bytes)

    def __estimate_sc_deploy(self, contract_path):
        project = load_project(contract_path)
        bytecode = project.get_bytecode()

        base64_bytecode = base64.b64encode(bytecode.encode())

        sender = "e3784da068cca901c0c629b304d024eb777fdf604dd8f6b5c0dc0c7f75877473"
        receiver = "0000000000000000000000000000000000000000000000000000000000000000"
        self.__sent_tx(sender, receiver, base64_bytecode.decode())

    def __estimate_sc_call(self, sc_address, function, arguments):
        sender = "aaaaaaaa112233441122334411223344112233441122334411223344aaaaaaaa"
        receiver = sc_address
        arguments = arguments or []
        tx_data = function
        for arg in arguments:
            tx_data += f"@{prepare_argument(arg)}"

        base64_bytes = base64.b64encode(tx_data.encode())
        self.__sent_tx(sender, receiver, base64_bytes.decode())

    def __sent_tx(self, sender, receiver, data):
        tx_object = {
            "nonce": 1,
            "value": "0",
            "receiver": receiver,
            "sender": sender,
            "data": data
        }
        url = f"{self.proxy}/transaction/cost"

        raw_response = utils.post_json(url, tx_object)
        print(raw_response)
