import base64
import logging

from erdpy import scope
from erdpy.projects import load_project
from erdpy.proxy.http_facade import do_post
from erdpy.proxy.tx_types import TxTypes

logger = logging.getLogger("proxy")


class TransactionCostEstimator:
    # needs these constant because when the observer node receive a post request from proxy with a transaction needs
    # to can figure out what type of transaction was send to can calculate an estimation
    _SENDER_ADDRESS = "erd1l453hd0gt5gzdp7czpuall8ggt2dcv5zwmfdf3sd3lguxseux2fsmsgldz"
    _RECEIVER_ADDRESS = "erd1cux02zersde0l7hhklzhywcxk4u9n4py5tdxyx7vrvhnza2r4gmq4vw35r"

    def __init__(self, proxy_url):
        self.proxy_url = proxy_url

    def estimate_tx_cost(self, arguments, tx_type):
        if tx_type == TxTypes.MOVE_BALANCE:
            return self._estimate_move_balance(arguments.data)
        elif tx_type == TxTypes.SC_DEPLOY:
            return self._estimate_sc_deploy(arguments.project)
        else:
            return self._estimate_sc_call(arguments.contract, arguments.function, arguments.arguments)

    def _estimate_move_balance(self, data):
        sender = self._SENDER_ADDRESS
        receiver = self._RECEIVER_ADDRESS
        data = data or ""
        data_bytes = base64.b64encode(data.encode())

        estimate = self._send_transaction(sender, receiver, data_bytes.decode())
        return estimate

    def _estimate_sc_deploy(self, contract_path):
        if contract_path is None:
            logger.fatal("contract-path argument missing")
            return

        project = load_project(contract_path)
        bytecode = project.get_bytecode()
        base64_bytecode = base64.b64encode(bytecode.encode())

        sender = self._SENDER_ADDRESS
        receiver = self._RECEIVER_ADDRESS
        estimate = self._send_transaction(sender, receiver, base64_bytecode.decode())
        return estimate

    def _estimate_sc_call(self, sc_address, function, arguments):
        if function is None:
            logger.fatal("function argument missing")
            return

        if sc_address is None:
            logger.fatal("sc-address argument missing")
            return

        sender = self._SENDER_ADDRESS
        receiver = sc_address
        arguments = arguments or []
        tx_data = function
        for arg in arguments:
            # TODO: call prepare_argument()
            tx_data += f"@0x0000"

        base64_bytes = base64.b64encode(tx_data.encode())
        estimate = self._send_transaction(sender, receiver, base64_bytes.decode())
        return estimate

    def _send_transaction(self, sender, receiver, data):
        tx_object = {
            "nonce": 1,
            "value": "0",
            "receiver": receiver,
            "sender": sender,
            "data": data,
            "chainID": scope.get_chain_id(),
            "version": scope.get_tx_version()
        }

        url = f"{self.proxy_url}/transaction/cost"

        raw_response = do_post(url, tx_object)
        return raw_response.get("txGasUnits", raw_response)
