import logging
from typing import Any

from multiversx_sdk import (
    AccountOnNetwork,
    Address,
    BlockCoordinates,
    ProxyNetworkProvider,
)

from multiversx_sdk_cli import cli_shared, utils
from multiversx_sdk_cli.config import get_config_for_network_providers

logger = logging.getLogger("cli.accounts")


def setup_parser(subparsers: Any) -> Any:
    parser = cli_shared.add_group_subparser(subparsers, "account", "Get Account data (nonce, balance) from the Network")
    subparsers = parser.add_subparsers()

    sub = cli_shared.add_command_subparser(subparsers, "account", "get", "Query account details (nonce, balance etc.)")
    cli_shared.add_proxy_arg(sub)
    _add_address_arg(sub)
    mutex = sub.add_mutually_exclusive_group()
    mutex.add_argument("--balance", action="store_true", help="whether to only fetch the balance")
    mutex.add_argument("--nonce", action="store_true", help="whether to only fetch the nonce")
    mutex.add_argument("--username", action="store_true", help="whether to only fetch the username")
    cli_shared.add_omit_fields_arg(sub)
    sub.set_defaults(func=get_account)

    parser.epilog = cli_shared.build_group_epilog(subparsers)
    return subparsers


def _add_address_arg(sub: Any):
    sub.add_argument("--address", required=True, help="🖄 the address to query")


def get_account(args: Any):
    omitted_fields = cli_shared.parse_omit_fields_arg(args)

    proxy_url = args.proxy
    address = args.address
    config = get_config_for_network_providers()
    proxy = ProxyNetworkProvider(url=proxy_url, config=config)
    account = proxy.get_account(Address.new_from_bech32(address))

    if args.balance:
        print(account.balance)
    elif args.nonce:
        print(account.nonce)
    elif args.username:
        print(account.username)
    else:
        account = _account_on_network_to_dictionary(account)
        utils.dump_out_json(utils.omit_fields(account, omitted_fields))


def _account_on_network_to_dictionary(account: AccountOnNetwork) -> dict[str, Any]:
    return {
        "address": account.address.to_bech32(),
        "nonce": account.nonce,
        "balance": account.balance,
        "is_guarded": account.is_guarded,
        "username": account.username,
        "block_coordinates": (
            _block_coordinates_to_dictionary(account.block_coordinates) if account.block_coordinates else {}
        ),
        "contract_code_hash": account.contract_code_hash.hex(),
        "contract_code": account.contract_code.hex(),
        "contract_developer_reward": account.contract_developer_reward,
        "contract_owner_address": account.contract_owner_address.to_bech32() if account.contract_owner_address else "",
        "is_contract_upgradable": account.is_contract_upgradable,
        "is_contract_readable": account.is_contract_readable,
        "is_contract_payable": account.is_contract_payable,
        "is_contract_payable_by_contract": account.is_contract_payable_by_contract,
    }


def _block_coordinates_to_dictionary(block: BlockCoordinates) -> dict[str, Any]:
    return {
        "nonce": block.nonce,
        "hash": block.hash.hex(),
        "root_hash": block.root_hash.hex(),
    }
