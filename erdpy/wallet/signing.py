import logging
from os import path
from typing import Any

import nacl.encoding
import nacl.signing
from erdpy import dependencies, myprocess
from erdpy.errors import CannotSignMessageWithBLSKey
from erdpy.interfaces import IAccount, ITransaction

logger = logging.getLogger("wallet")


def sign_message_with_bls_key(message, seed):
    dependencies.install_module("mcl_signer")
    tool = path.join(dependencies.get_module_directory("mcl_signer"), "signer")

    try:
        signed_message = myprocess.run_process([tool, message, seed], dump_to_stdout=False)
        return signed_message
    except Exception:
        raise CannotSignMessageWithBLSKey()
