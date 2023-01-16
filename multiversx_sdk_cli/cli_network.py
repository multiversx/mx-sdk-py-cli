from multiversx_sdk_network_providers.proxy_network_provider import ProxyNetworkProvider
from multiversx_sdk_cli import cli_shared
import logging
from typing import Any

logger = logging.getLogger("cli.network")


def setup_parser(subparsers: Any) -> Any:
    parser = cli_shared.add_group_subparser(subparsers, "network", "Get Network parameters, such as number of shards, chain identifier etc.")
    subparsers = parser.add_subparsers()

    sub = cli_shared.add_command_subparser(subparsers, "network", "num-shards", "Get the number of shards.")
    cli_shared.add_proxy_arg(sub)
    sub.set_defaults(func=get_num_shards)

    sub = cli_shared.add_command_subparser(subparsers, "network", "block-nonce", "Get the latest block nonce, by shard.")
    cli_shared.add_proxy_arg(sub)
    sub.add_argument("--shard", required=True, help="the shard ID (use 4294967295 for metachain)")
    sub.set_defaults(func=get_last_block_nonce)

    sub = cli_shared.add_command_subparser(subparsers, "network", "chain", "Get the chain identifier.")
    cli_shared.add_proxy_arg(sub)
    sub.set_defaults(func=get_chain_id)

    parser.epilog = cli_shared.build_group_epilog(subparsers)
    return subparsers


def get_num_shards(args: Any):
    proxy_url = args.proxy
    proxy = ProxyNetworkProvider(proxy_url)
    num_shards = proxy.get_network_config().num_shards_without_meta
    print(num_shards)
    return num_shards


def get_last_block_nonce(args: Any):
    proxy_url = args.proxy
    shard = args.shard
    proxy = ProxyNetworkProvider(proxy_url)
    nonce = proxy.get_network_status(shard).highest_final_nonce
    print(nonce)
    return nonce


def get_chain_id(args: Any):
    proxy_url = args.proxy
    proxy = ProxyNetworkProvider(proxy_url)
    chain_id = proxy.get_network_config().chain_id
    print(chain_id)
    return chain_id
