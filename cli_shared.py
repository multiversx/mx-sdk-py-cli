import argparse
from argparse import FileType

import sys
from erdpy import config, utils
from typing import Any, Text


def wider_help_formatter(prog: Text):
    return argparse.HelpFormatter(prog, max_help_position=50, width=120)


def add_tx_args(sub: Any):
    sub.add_argument("--nonce", type=int, required=not("--recall-nonce" in sys.argv), help="# the nonce for the transaction")
    sub.add_argument("--recall-nonce", action="store_true", default=False, help="⭮ whether to recall the nonce when creating the transaction (default: %(default)s)")
    sub.add_argument("--gas-price", default=config.DEFAULT_GAS_PRICE, help="⛽ the gas price (default: %(default)d)")
    sub.add_argument("--gas-limit", required=True, help="⛽ the gas limit")
    sub.add_argument("--value", default="0", help="the value to transfer (default: %(default)s)")
    sub.add_argument("--chain", default=config.get_chain_id(), help="the chain identifier (default: %(default)s)")
    sub.add_argument("--version", type=int, default=config.get_tx_version(), help="the transaction version (default: %(default)s)")


def add_wallet_args(sub: Any):
    sub.add_argument("--pem", required=not (utils.is_arg_present("--keyfile", sys.argv)), help="🔑 the PEM file, if keyfile not provided")
    sub.add_argument("--keyfile", required=not (utils.is_arg_present("--pem", sys.argv)), help="🔑 a JSON keyfile, if PEM not provided")
    sub.add_argument("--passfile", required=not (utils.is_arg_present("--pem", sys.argv)), help="🔑 a file containing keyfile's password, if keyfile provided")


def add_proxy_arg(sub: Any):
    sub.add_argument("--proxy", default=config.get_proxy(), help="🖧 the URL of the proxy (default: %(default)s)")


def add_outfile_arg(sub: Any):
    sub.add_argument("--outfile", type=FileType("w"), default=sys.stdout, help="where to save the command's output (default: stdout)")
