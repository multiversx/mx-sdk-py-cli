import logging
import nacl.encoding
import nacl.signing
import base64
from os import path

from erdpy import utils, guards

logger = logging.getLogger("wallet.generator")


def generate_accounts():
	signing_key = nacl.signing.SigningKey.generate()