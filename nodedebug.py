import os
import signal
from os import path

from psutil import process_iter

from erdpy import dependencies, myprocess


def start(force=False):
    # TODO: if already started and no force, noop.
    _install_if_missing()
    directory = dependencies.get_module_by_key("nodedebug").get_directory()
    args = [path.join(directory, "nodedebug")]

    # let port: any = MySettings.getRestDebuggerPort();
    # let configPath: any = path.join(toolPathFolder, "config", "config.toml");
    # let genesisPath: any = path.join(toolPathFolder, "config", "genesis.json");
    # args: ["--rest-api-port", port, "--config", configPath, "--genesis-file", genesisPath]
    myprocess.run_process_nowait(args)

def _is_running():
    pass

def _install_if_missing():
    dependencies.install_module("nodedebug", overwrite=False)


def stop():
    for proc in process_iter():
        if proc.name() == "nodedebug":
            print("Stopping nodedebug.")
            proc.send_signal(signal.SIGTERM)


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
