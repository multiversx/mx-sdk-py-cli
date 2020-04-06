import logging
import signal
from os import path

from erdpy import config, dependencies, errors, myprocess, utils

logger = logging.getLogger("nodedebug")


def start(force=False):
    install_if_missing()

    if _is_running() and not force:
        return

    if force:
        stop()

    logger.info("Starting nodedebug...")
    myprocess.run_process_async(_get_args(), env=_get_env())


def _get_args():
    directory = dependencies.get_module_by_key("nodedebug").get_directory()
    executable = path.join(directory, "nodedebug")
    config_path = path.join(directory, "config", "config.toml")
    genesis_path = path.join(directory, "config", "genesis.json")

    args = [executable, "--rest-api-port", "8080", "--config",
            config_path, "--genesis-file", genesis_path]
    return args


async def start_async():
    await myprocess.async_subprocess(_get_args(), env=_get_env(), sinks=["nodedebug"])


def _is_running():
    proc = _get_proc()
    return proc is not None


def _get_proc():
    # TODO: Find another way to get the process, so that psutil is not needed
    # psutil requires "sudo apt-get install python3-dev" / "build-essentials"
    from psutil import process_iter

    for proc in process_iter():
        if proc.name() == "nodedebug":
            return proc


def install_if_missing():
    dependencies.install_module("nodedebug", overwrite=False)


def stop():
    proc = _get_proc()
    if proc:
        logger.info("Stopping nodedebug...")
        proc.send_signal(signal.SIGTERM)
        logger.info("Stopped nodedebug.")
    else:
        logger.info("Nodedebug wasn't started.")


def deploy(bytecode, owner, arguments=None, gas_price=None, gas_limit=None):
    logger.debug("deploy")

    arguments = arguments or []
    gas_limit = gas_limit or config.DEFAULT_GASLIMIT
    gas_price = gas_price or config.DEFAULT_GASPRICE

    url = _get_url("deploy")

    tx_data = bytecode
    for arg in arguments:
        tx_data += f"@{_prepare_argument(arg)}"

    data = {
        "SndAddress": owner.address,
        "Value": "0",
        "GasLimit": gas_limit,
        "GasPrice": gas_price,
        "TxData": tx_data
    }

    raw_response = utils.post_json(url, data)
    logger.debug("Response: %s", raw_response)
    response = _Response(raw_response)
    response.verify()
    return response.tx_hash, response.contract_address


def execute(contract_address, caller, function, arguments=None, gas_price=None, gas_limit=None):
    logger.debug(f"execute, address={contract_address}")

    arguments = arguments or []
    gas_limit = gas_limit or config.DEFAULT_GASLIMIT
    gas_price = gas_price or config.DEFAULT_GASPRICE

    url = _get_url("run")

    tx_data = function
    for arg in arguments:
        tx_data += f"@{_prepare_argument(arg)}"

    data = {
        "SndAddress": caller.address,
        "ScAddress": contract_address,
        "Value": "0",
        "GasLimit": gas_limit,
        "GasPrice": gas_price,
        "TxData": tx_data
    }

    raw_response = utils.post_json(url, data)
    logger.debug("Response: %s", raw_response)
    response = _VMOutputResponse(raw_response)
    response.verify()
    return response


def query(contract_address, function, arguments=None):
    logger.debug(f"query, address={contract_address}")

    arguments = [_prepare_argument(arg) for arg in arguments or []]

    url = _get_url("query")

    data = {
        "ScAddress": contract_address,
        "FuncName": function,
        "Args": arguments
    }

    raw_response = utils.post_json(url, data)
    logger.debug("Response: %s", raw_response)
    response = _VMOutputResponse(raw_response)
    response.verify()
    return response.return_data


def _get_url(action):
    return f"http://localhost:8080/vm-values/{action}"


class _Response:
    def __init__(self, raw_dict):
        def find(key):
            return utils.find_in_dictionary(raw_dict, key)

        self.error = find("error")
        self.contract_address = find("data.Address")
        self.tx_hash = find("data.Other.txHash")

    def verify(self):
        if self.error:
            raise errors.KnownError(self.error)


class _VMOutputResponse:
    def __init__(self, raw_dict):
        def find(key):
            return utils.find_in_dictionary(raw_dict, key)

        self.error = find("error")
        self.return_data = find("data.ReturnData")
        self.return_code = find("data.ReturnCode")

    def verify(self):
        if self.error:
            raise errors.KnownError(self.error)        


def _get_env():
    return dependencies.get_module_by_key("nodedebug").get_env()
