import logging
import os
import signal
import time
from os import path

from psutil import process_iter

from erdpy import dependencies, myprocess

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
    await myprocess.async_subprocess(_get_args())


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


def deploy():
    start()


    # let response = await RequestsFacade.post({
    #     url: url,
    #     data: {
    #         "OnTestnet": options.onTestnet,
    #         "PrivateKey": options.privateKey,
    #         "TestnetNodeEndpoint": MySettings.getTestnetUrl(),
    #         "SndAddress": options.senderAddress,
    #         "Value": options.value.toString(),
    #         "GasLimit": options.gasLimit,
    #         "GasPrice": options.gasPrice,
    #         "TxData": options.transactionData
    #     },
    # });
    pass
