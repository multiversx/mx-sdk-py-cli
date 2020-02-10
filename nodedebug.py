import logging
import os
import signal
import time
from os import path

from psutil import process_iter

from erdpy import dependencies, myprocess, utils

logger = logging.getLogger("nodedebug")


def start(force=False):
    _install_if_missing()

    if _is_running() and not force:
        return

    if force:
        stop()

    logger.info("Starting nodedebug...")
    myprocess.run_process_async(_get_args())


def _get_args():
    directory = dependencies.get_module_by_key("nodedebug").get_directory()
    executable = path.join(directory, "nodedebug")
    config_path = path.join(directory, "config", "config.toml")
    genesis_path = path.join(directory, "config", "genesis.json")

    args = [executable, "--rest-api-port", "8080", "--config",
            config_path, "--genesis-file", genesis_path]
    return args


async def start_async():
    await myprocess.async_subprocess(_get_args(), sinks=["nodedebug"])


def _is_running():
    proc = _get_proc()
    return proc is not None


def _get_proc():
    for proc in process_iter():
        if proc.name() == "nodedebug":
            return proc


def _install_if_missing():
    dependencies.install_module("nodedebug", overwrite=False)


def stop():
    proc = _get_proc()
    if proc:
        logger.info("Stopping nodedebug...")
        proc.send_signal(signal.SIGTERM)
        logger.info("Stopped nodedebug.")
    else:
        logger.info("Nodedebug wasn't started.")


def deploy(bytecode, sender):
    url = "http://localhost:8080/vm-values/deploy"
    data = {
        "OnTestnet": False,
        # "PrivateKey": "",
        # "TestnetNodeEndpoint": "",
        "SndAddress": sender,
        "Value": "0",
        "GasLimit": 500000000,
        "GasPrice": 200000000000000,
        "TxData": bytecode
    }

    response = utils.post_json(url, data)
    print(response)
    tx_hash = None
    contract_address = response["data"]["Address"]

    return tx_hash, contract_address


def execute(address, sender, function):
    url = "http://localhost:8080/vm-values/run"
    data = {

    }

    response = utils.post_json(url, data)
    print(response)


def query(address, function, arguments):
    url = "http://localhost:8080/vm-values/query"
    data = {
        "ScAddress": address,
        "FuncName": function,
        "Args": []
    }

    response = utils.post_json(url, data)
    print(response)
    return_data = response["data"]["ReturnData"]
    return return_data
