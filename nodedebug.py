import logging
import os
import signal
import time
from os import path

from psutil import process_iter

from erdpy import dependencies, myprocess

logger = logging.getLogger("nodedebug")


def start(force=False):
    # TODO: if already started and no force, noop.
    _install_if_missing()
    directory = dependencies.get_module_by_key("nodedebug").get_directory()
    args = [path.join(directory, "nodedebug")]

    # let port: any = MySettings.getRestDebuggerPort();
    # let configPath: any = path.join(toolPathFolder, "config", "config.toml");
    # let genesisPath: any = path.join(toolPathFolder, "config", "genesis.json");
    # args: ["--rest-api-port", port, "--config", configPath, "--genesis-file", genesisPath]
    logger.info("Starting nodedebug...")
    myprocess.run_process_nowait(args)


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
