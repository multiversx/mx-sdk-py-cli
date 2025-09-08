from typing import Any

from multiversx_sdk import TransactionsFactoryConfig

from multiversx_sdk_cli import cli_shared
from multiversx_sdk_cli.args_validation import (
    validate_broadcast_args,
    validate_chain_id_args,
)
from multiversx_sdk_cli.cli_output import CLIOutputBuilder
from multiversx_sdk_cli.tokens import TokenWrapper


def setup_parser(args: list[str], subparsers: Any) -> Any:
    parser = cli_shared.add_group_subparser(
        subparsers, "token", "Perform token management operations (issue tokens, create NFTs, set roles, etc.)"
    )
    subparsers = parser.add_subparsers()

    sub = cli_shared.add_command_subparser(
        subparsers,
        "token",
        "issue-fungible",
        f"Issue a new fungible ESDT token.{CLIOutputBuilder.describe()}",
    )
    sub.add_argument(
        "--token-name",
        required=True,
        type=str,
        help="the name of the token to be issued: 3-20 alphanumerical characters",
    )
    sub.add_argument(
        "--token-ticker",
        required=True,
        type=str,
        help="the ticker of the token to be issued: 3-10 UPPERCASE alphanumerical characters",
    )
    sub.add_argument("--initial-supply", required=True, type=int, help="the initial supply of the token to be issued")
    sub.add_argument(
        "--num-decimals",
        required=True,
        type=int,
        help="a numerical value between 0 and 18 representing number of decimals",
    )
    sub.add_argument(
        "--can-freeze", required=True, type=lambda x: x.lower() == "true", help="whether a token can be freezed"
    )
    sub.add_argument(
        "--can-wipe", required=True, type=lambda x: x.lower() == "true", help="whether a token can be wiped"
    )
    sub.add_argument(
        "--can-pause", required=True, type=lambda x: x.lower() == "true", help="whether a token can be paused"
    )
    sub.add_argument(
        "--can-change-owner", required=True, type=lambda x: x.lower() == "true", help="whether a token can change owner"
    )
    sub.add_argument(
        "--can-upgrade", required=True, type=lambda x: x.lower() == "true", help="whether a token can be upgraded"
    )
    sub.add_argument(
        "--can-add_special-roles",
        required=lambda x: x.lower() == "true",
        type=bool,
        help="whether special roles can be added for the token",
    )

    cli_shared.add_wallet_args(args, sub)
    cli_shared.add_tx_args(args, sub, with_receiver=False, with_data=False)
    sub.add_argument("--data-file", type=str, default=None, help="a file containing transaction data")
    cli_shared.add_broadcast_args(sub)
    cli_shared.add_proxy_arg(sub)
    cli_shared.add_wait_result_and_timeout_args(sub)
    cli_shared.add_guardian_wallet_args(args, sub)
    cli_shared.add_relayed_v3_wallet_args(args, sub)
    cli_shared.add_outfile_arg(sub)

    sub.set_defaults(func=issue_fungible)

    parser.epilog = cli_shared.build_group_epilog(subparsers)
    return subparsers


def validate_token_args(args: Any):
    if args.initial_supply < 0:
        raise ValueError("Initial supply must be a non-negative integer")

    if not (0 <= args.num_decimals <= 18):
        raise ValueError("Number of decimals must be between 0 and 18")

    if not (3 <= len(args.token_name) <= 20) or not args.token_name.isalnum():
        raise ValueError("Token name must be 3-20 alphanumerical characters")

    if not (3 <= len(args.token_ticker) <= 10) or not args.token_ticker.isalnum() or not args.token_ticker.isupper():
        raise ValueError("Token ticker must be 3-10 UPPERCASE alphanumerical characters")


def _ensure_args(args: Any):
    validate_broadcast_args(args)
    validate_chain_id_args(args)
    validate_token_args(args)


def issue_fungible(args: Any):
    _ensure_args(args)

    sender = cli_shared.prepare_sender(args)
    guardian_and_relayer_data = cli_shared.get_guardian_and_relayer_data(
        sender=sender.address.to_bech32(),
        args=args,
    )
    chain_id = cli_shared.get_chain_id(args.proxy, args.chain)
    gas_estimator = cli_shared.initialize_gas_limit_estimator(args)
    controller = TokenWrapper(config=TransactionsFactoryConfig(chain_id), gas_limit_estimator=gas_estimator)

    transaction = controller.create_transaction_for_issuing_fungible_token(
        sender=sender,
        nonce=sender.nonce,
        token_name=args.token_name,
        token_ticker=args.token_ticker,
        initial_supply=args.initial_supply,
        num_decimals=args.num_decimals,
        gas_limit=args.gas_limit,
        gas_price=args.gas_price,
        version=args.version,
        options=args.options,
        guardian_and_relayer_data=guardian_and_relayer_data,
        can_freeze=args.can_freeze,
        can_wipe=args.can_wipe,
        can_pause=args.can_pause,
        can_change_owner=args.can_change_owner,
        can_upgrade=args.can_upgrade,
        can_add_special_roles=args.can_add_special_roles,
    )

    cli_shared.send_or_simulate(transaction, args)
