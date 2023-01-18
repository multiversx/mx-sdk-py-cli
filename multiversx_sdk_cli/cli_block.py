from typing import Any

from multiversx_sdk_cli import cli_shared, utils
from multiversx_sdk_network_providers.proxy_network_provider import ProxyNetworkProvider


def setup_parser(subparsers: Any) -> Any:
    parser = cli_shared.add_group_subparser(subparsers, "hyperblock", "Get Hyperblock from the Network")
    subparsers = parser.add_subparsers()

    sub = cli_shared.add_command_subparser(subparsers, "hyperblock", "get", "Get hyperblock")

    cli_shared.add_proxy_arg(sub)
    sub.add_argument("--key", required=True, help="the hash or the nonce of the hyperblock")

    sub.set_defaults(func=get_hyperblock)


def get_hyperblock(args: Any) -> Any:
    proxy_url = args.proxy
    proxy = ProxyNetworkProvider(proxy_url)
    key =  args.key

    url = f"hyperblock/by-hash/{key}"
    if str(key).isnumeric():
        url = f"hyperblock/by-nonce/{key}"

    response = proxy.do_get_generic(url)
    response = response.get("hyperblock", {})

    utils.dump_out_json(response)
