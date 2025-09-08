from typing import Any

from multiversx_sdk_cli import cli_shared
from multiversx_sdk_cli.cli_output import CLIOutputBuilder
from multiversx_sdk_cli.cli_transactions import _add_common_arguments


def setup_parser(args: list[str], subparsers: Any) -> Any:
    parser = cli_shared.add_group_subparser(subparsers, "token", "Perform operations with tokens")
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
    sub.add_argument("--can-freeze", type=bool, help="whether a token can be freezed")
    sub.add_argument("--can-wipe", type=bool, help="whether a token can be wiped")
    sub.add_argument("--can-pause", type=bool, help="whether a token can be paused")
    sub.add_argument("--can-change-owner", type=bool, help="whether a token can change owner")
    sub.add_argument("--can-upgrade", type=bool, help="whether a token can be upgraded")
    sub.add_argument("--can-add_special-roles", type=bool, help="whether special roles can be added for the token")

    _add_common_arguments(args, sub)
    cli_shared.add_broadcast_args(sub)
    cli_shared.add_proxy_arg(sub)
    cli_shared.add_wait_result_and_timeout_args(sub)

    sub.set_defaults(func=issue_fungible)


def issue_fungible(arg: Any):
    pass
