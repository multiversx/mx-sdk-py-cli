import os
import signal
from os import path

from psutil import process_iter

from erdpy import dependencies, myprocess


def start(force=False):
    _install_if_missing()
    directory = dependencies.get_module_by_key("nodedebug").get_directory()
    args = [path.join(directory, "nodedebug")]
    myprocess.run_process_nowait(args)


def stop():
    for proc in process_iter():
        if proc.name() == "nodedebug":
            print("Stopping nodedebug.")
            proc.send_signal(signal.SIGTERM)


def _install_if_missing():
    dependencies.install_module("nodedebug", overwrite=False)
