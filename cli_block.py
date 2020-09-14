from erdpy import block
import sys
from typing import Any

from erdpy import cli_shared, utils


def setup_parser(subparsers: Any) -> Any:
    parser = cli_shared.add_group_subparser(subparsers, "block", "Get Block data from the Network")
    subparsers = parser.add_subparsers()

    sub = cli_shared.add_command_subparser(subparsers, "block", "get", "Get block")

    cli_shared.add_proxy_arg(sub)
    sub.add_argument("--hash", required=not (utils.is_arg_present("--nonce", sys.argv)), help="the hash of block")
    sub.add_argument("--nonce", required=not (utils.is_arg_present("--hash", sys.argv)), help="the nonce of block")
    sub.add_argument("--shard", type=int, required=True, help="the shard of block")
    sub.add_argument("--with-txs", action="store_true", default=False, help="the returned block will contains all "
                                                                            "transactions")
    sub.set_defaults(func=get_block)


def get_block(args: Any) -> Any:
    block.get_block(args)
