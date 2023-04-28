import argparse
import ast
import sys
from argparse import FileType
from typing import Any, List, Text, Tuple, cast

from multiversx_sdk_network_providers.proxy_network_provider import \
    ProxyNetworkProvider

from multiversx_sdk_cli import config, deprecations, errors, utils
from multiversx_sdk_cli.accounts import Account, Address, LedgerAccount
from multiversx_sdk_cli.cli_output import CLIOutputBuilder
from multiversx_sdk_cli.cli_password import load_password
from multiversx_sdk_cli.simulation import Simulator
from multiversx_sdk_cli.transactions import Transaction


def wider_help_formatter(prog: Text):
    return argparse.RawDescriptionHelpFormatter(prog, max_help_position=50, width=120)


def add_group_subparser(subparsers: Any, group: str, description: str) -> Any:
    parser = subparsers.add_parser(
        group,
        usage=f"mxpy {group} COMMAND [-h] ...",
        description=description,
        formatter_class=argparse.RawDescriptionHelpFormatter
    )
    parser._positionals.title = "COMMANDS"
    parser._optionals.title = "OPTIONS"

    return parser


def build_group_epilog(subparsers: Any) -> str:
    epilog = """
----------------
COMMANDS summary
----------------
"""
    for choice, sub in subparsers.choices.items():
        description_first_line = sub.description.splitlines()[0]
        epilog += f"{choice.ljust(30)} {description_first_line}\n"

    return epilog


def add_command_subparser(subparsers: Any, group: str, command: str, description: str):
    return subparsers.add_parser(
        command,
        usage=f"mxpy {group} {command} [-h] ...",
        description=description,
        formatter_class=wider_help_formatter
    )


def add_tx_args(args: List[str],
                sub: Any,
                with_receiver: bool = True,
                with_data: bool = True,
                with_estimate_gas: bool = False):
    group_nonce = sub.add_argument_group("nonce", "transaction nonce (necessary for serializing transactions on the Network)")
    mutex_nonce = group_nonce.add_mutually_exclusive_group(required=True)
    mutex_nonce.add_argument("--nonce", type=int, help="# the nonce for the transaction")
    mutex_nonce.add_argument("--recall-nonce", action="store_true", default=False, help="⭮ whether to recall the nonce when creating the transaction (default: %(default)s)")

    group_participants = sub.add_argument_group("participants", "the addresses (and usernames) involved in the transaction; the sender is learned from the wallet arguments group")
    group_participants.add_argument("--sender-username", help="🖄 the username of the sender")
    if with_receiver:
        group_participants.add_argument("--receiver", required=True, help="🖄 the address of the receiver")
        group_participants.add_argument("--receiver-username", required=False, help="🖄 the username of the receiver")

    group_gas = sub.add_argument_group("gas", "the Network requires gas to process transactions")

    group_gas.add_argument("--gas-price", default=config.DEFAULT_GAS_PRICE, help="⛽ the gas price (default: %(default)d)")

    if with_estimate_gas:
        mutex_gas_limit = group_gas.add_mutually_exclusive_group(required=True)
        mutex_gas_limit.add_argument("--gas-limit", help="⛽ the gas limit")
        mutex_gas_limit.add_argument("--estimate-gas", action="store_true", default=False, help="⛽ whether to estimate the gas limit (default: %(default)d)")
    else:
        group_gas.add_argument("--gas-limit", required=True, help="⛽ the gas limit")

    sub.add_argument("--value", default="0", help="the value to transfer (default: %(default)s)")

    if with_data:
        sub.add_argument("--data", default="", help="the payload, or 'memo' of the transaction (default: %(default)s)")

    sub.add_argument("--chain", default=config.get_chain_id(), help="the chain identifier (default: %(default)s)")
    sub.add_argument("--version", type=int, default=config.get_tx_version(), help="the transaction version (default: %(default)s)")
    sub.add_argument("--options", type=int, default=0, help="the transaction options (default: 0)")


def add_wallet_args(args: List[str], sub: Any):
    group = sub.add_argument_group("wallet", "sender's wallet (used for signing)")

    group.add_argument("--pem", help="🔑 the PEM file, if keyfile not provided")
    group.add_argument("--pem-index", default=0, help="🔑 the index in the PEM file (default: %(default)s)")
    group.add_argument("--keyfile", help="🔑 a JSON keyfile, if PEM not provided")
    group.add_argument("--passfile", help="🔑 a file containing keyfile's password, if keyfile provided")
    group.add_argument("--ledger", action="store_true", default=False, help="🔐 bool flag for signing transaction using ledger")
    group.add_argument("--ledger-account-index", type=int, default=0, help="🔐 the index of the account when using Ledger")
    group.add_argument("--ledger-address-index", type=int, default=0, help="🔐 the index of the address when using Ledger")


def add_proxy_arg(sub: Any):
    sub.add_argument("--proxy", default=config.get_proxy(), help="🔗 the URL of the proxy (default: %(default)s)")


def add_outfile_arg(sub: Any, what: str = ""):
    what = f"({what})" if what else ""
    sub.add_argument("--outfile", type=FileType("w"), default=sys.stdout, help=f"where to save the output {what} (default: stdout)")


def add_infile_arg(sub: Any, what: str = ""):
    what = f"({what})" if what else ""
    sub.add_argument("--infile", type=FileType("r"), required=True, help=f"input file {what}")


def add_omit_fields_arg(sub: Any):
    sub.add_argument("--omit-fields", default="[]", type=str, required=False, help="omit fields in the output payload (default: %(default)s)")


def parse_omit_fields_arg(args: Any) -> List[str]:
    literal = args.omit_fields
    parsed = ast.literal_eval(literal)
    return cast(List[str], parsed)


def acquire_tx_prerequisites(args: Any) -> Tuple[Account, int]:
    _check_broadcast_args(args)

    chain_id = _acquire_chain_id(args)
    sender = acquire_signer(args)
    nonce = _aquire_nonce(args, sender.address)

    args.chain = chain_id
    args.nonce = nonce

    return sender, nonce


def _acquire_chain_id(args: Any) -> str:
    if args.chain is not None:
        return args.chain

    provider = ProxyNetworkProvider(args.proxy)
    chain_id = provider.get_network_config().chain_id
    return chain_id


def acquire_signer(args: Any) -> Account:
    if args.pem:
        return Account(pem_file=args.pem, pem_index=args.pem_index)
    elif args.keyfile:
        password = load_password(args)
        return Account(key_file=args.keyfile, password=password)
    elif args.ledger:
        return LedgerAccount(
            account_index=args.ledger_account_index,
            address_index=args.ledger_address_index
        )
    else:
        raise errors.BadUsage("You must provide an account wallet, using either '--pem' or '--keyfile' or '--ledger'")


def _aquire_nonce(args: Any, address: Address) -> int:
    if args.nonce is not None:
        return args.nonce

    provider = ProxyNetworkProvider(args.proxy)
    nonce = provider.get_account(address).nonce
    return nonce


def add_broadcast_args(sub: Any, simulate: bool = True, relay: bool = False, with_wait_result: bool = True):
    group = sub.add_argument_group("broadcasting", "broadcasting options")

    group.add_argument("--send", action="store_true", default=False, help="✓ whether to broadcast the transaction (default: %(default)s)")

    if with_wait_result:
        group.add_argument("--wait-result", action="store_true", default=False, help="signal to wait for the transaction result - only valid if --send is set")
        group.add_argument("--timeout", default=100, help="max num of seconds to wait for result - only valid if --wait-result is set")

    if simulate:
        group.add_argument("--simulate", action="store_true", default=False, help="whether to simulate the transaction (default: %(default)s)")
    if relay:
        group.add_argument("--relay", action="store_true", default=False, help="deprecated, will be removed in next major version")


def _check_broadcast_args(args: Any):
    if hasattr(args, "relay"):
        deprecations.relay_cli_argument_is_deprecated()

    if hasattr(args, "relay") and args.relay and args.send:
        raise errors.BadUsage("Cannot directly send a relayed transaction. Use 'mxpy tx new --relay' first, then 'mxpy tx send --data-file'")
    if args.send and args.simulate:
        raise errors.BadUsage("Cannot both 'simulate' and 'send' a transaction")


def send_or_simulate(tx: Transaction, args: Any, dump_output: bool = True) -> CLIOutputBuilder:
    proxy = ProxyNetworkProvider(args.proxy)

    is_set_wait_result = hasattr(args, "wait_result") and args.wait_result
    is_set_send = hasattr(args, "send") and args.send
    is_set_simulate = hasattr(args, "simulate") and args.simulate

    send_wait_result = is_set_wait_result and is_set_send and not is_set_simulate
    send_only = is_set_send and not (is_set_wait_result or is_set_simulate)
    simulate = is_set_simulate and not (send_only or send_wait_result)

    output_builder = CLIOutputBuilder()
    output_builder.set_emitted_transaction(tx)
    outfile = args.outfile if hasattr(args, "outfile") else None

    try:
        if send_wait_result:
            transaction_on_network = tx.send_wait_result(proxy, args.timeout)
            output_builder.set_awaited_transaction(transaction_on_network)
        elif send_only:
            tx.send(proxy)
        elif simulate:
            simulation = Simulator(proxy).run(tx)
            output_builder.set_simulation_results(simulation)
    finally:
        if dump_output:
            utils.dump_out_json(output_builder.build(), outfile=outfile)

    return output_builder
