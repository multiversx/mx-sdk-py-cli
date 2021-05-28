from typing import Any

from erdpy import cli_shared, utils
from erdpy.proxy.core import ElrondProxy


def setup_parser(subparsers: Any) -> Any:
    parser = cli_shared.add_group_subparser(subparsers, "hyperblock", "Get Hyperblock from the Network")
    subparsers = parser.add_subparsers()

    sub = cli_shared.add_command_subparser(subparsers, "hyperblock", "get", "Get hyperblock")

    cli_shared.add_proxy_arg(sub)
    sub.add_argument("--key", required=True, help="the hash or the nonce of the hyperblock")

    sub.set_defaults(func=get_hyperblock)


def get_hyperblock(args: Any) -> Any:
    proxy_url = args.proxy
    proxy = ElrondProxy(proxy_url)
    response = proxy.get_hyperblock(args.key)
    utils.dump_out_json(response)
