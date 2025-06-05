import argparse
import ast
import base64
import logging
import sys
from argparse import FileType
from functools import cache
from pathlib import Path
from typing import Any, Optional, Text, Union, cast

from multiversx_sdk import (
    Account,
    Address,
    ApiNetworkProvider,
    LedgerAccount,
    ProxyNetworkProvider,
    Token,
    TokenComputer,
    TokenTransfer,
    Transaction,
)

from multiversx_sdk_cli import config, utils
from multiversx_sdk_cli.address import (
    get_active_address,
    read_address_config_file,
    resolve_address_config_path,
)
from multiversx_sdk_cli.cli_output import CLIOutputBuilder
from multiversx_sdk_cli.cli_password import (
    load_guardian_password,
    load_password,
    load_relayer_password,
)
from multiversx_sdk_cli.constants import (
    DEFAULT_GAS_PRICE,
    DEFAULT_TX_VERSION,
    TCS_SERVICE_ID,
)
from multiversx_sdk_cli.env import MxpyEnv, get_address_hrp
from multiversx_sdk_cli.errors import (
    AddressConfigFileError,
    ArgumentsNotProvidedError,
    BadUsage,
    IncorrectWalletError,
    InvalidAddressConfigValue,
    NoWalletProvided,
    UnknownAddressAliasError,
)
from multiversx_sdk_cli.guardian_relayer_data import GuardianRelayerData
from multiversx_sdk_cli.interfaces import IAccount
from multiversx_sdk_cli.simulation import Simulator
from multiversx_sdk_cli.transactions import send_and_wait_for_result
from multiversx_sdk_cli.utils import log_explorer_transaction
from multiversx_sdk_cli.ux import confirm_continuation

logger = logging.getLogger("cli_shared")


trusted_cosigner_service_url_by_chain_id = {
    "1": "https://tools.multiversx.com/guardian",
    "D": "https://devnet-tools.multiversx.com/guardian",
    "T": "https://testnet-tools.multiversx.com/guardian",
}


def get_trusted_cosigner_service_url_by_chain_id(chain_id: str) -> str:
    try:
        return trusted_cosigner_service_url_by_chain_id[chain_id]
    except:
        raise BadUsage(f"Could not get Trusted Cosigner Service Url. No match found for chain id: {chain_id}")


def wider_help_formatter(prog: Text):
    return argparse.RawDescriptionHelpFormatter(prog, max_help_position=50, width=120)


def add_group_subparser(subparsers: Any, group: str, description: str) -> Any:
    parser = subparsers.add_parser(
        group,
        usage=f"mxpy {group} COMMAND [-h] ...",
        description=description,
        formatter_class=argparse.RawDescriptionHelpFormatter,
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
        formatter_class=wider_help_formatter,
    )


def add_tx_args(
    args: list[str],
    sub: Any,
    with_nonce: bool = True,
    with_receiver: bool = True,
    with_data: bool = True,
):
    if with_nonce:
        sub.add_argument(
            "--nonce",
            type=int,
            required=False,
            default=None,
            help="# the nonce for the transaction. If not provided, is fetched from the network.",
        )
        sub.add_argument(
            "--recall-nonce",
            action="store_true",
            default=False,
            help="⭮ whether to recall the nonce when creating the transaction (default: %(default)s). This argument is OBSOLETE.",
        )

    if with_receiver:
        sub.add_argument("--receiver", required=False, help="🖄 the address of the receiver")
        sub.add_argument("--receiver-username", required=False, help="🖄 the username of the receiver")

    sub.add_argument(
        "--gas-price",
        default=DEFAULT_GAS_PRICE,
        type=int,
        help="⛽ the gas price (default: %(default)d)",
    )
    sub.add_argument("--gas-limit", required=False, type=int, help="⛽ the gas limit")

    sub.add_argument("--value", default=0, type=int, help="the value to transfer (default: %(default)s)")

    if with_data:
        sub.add_argument(
            "--data",
            default="",
            help="the payload, or 'memo' of the transaction (default: %(default)s)",
        )

    sub.add_argument("--chain", type=str, help="the chain identifier")
    sub.add_argument(
        "--version",
        type=int,
        default=DEFAULT_TX_VERSION,
        help="the transaction version (default: %(default)s)",
    )
    sub.add_argument("--options", type=int, default=0, help="the transaction options (default: %(default)s)")

    sub.add_argument("--relayer", type=str, help="the bech32 address of the relayer", default="")
    sub.add_argument("--guardian", type=str, help="the bech32 address of the guardian", default="")


def add_wallet_args(args: list[str], sub: Any):
    sub.add_argument("--sender", type=str, help="the alias of the wallet set in the address config")
    sub.add_argument(
        "--pem",
        required=False,
        help="🔑 the PEM file, if keyfile not provided",
    )
    sub.add_argument(
        "--keyfile",
        required=False,
        help="🔑 a JSON keyfile, if PEM not provided",
    )
    sub.add_argument(
        "--passfile",
        help="🔑 a file containing keyfile's password, if keyfile provided. If not provided, you'll be prompted to enter the password.",
    )
    sub.add_argument(
        "--ledger",
        action="store_true",
        required=False,
        default=False,
        help="🔐 bool flag for signing transaction using ledger",
    )
    sub.add_argument(
        "--sender-wallet-index",
        type=int,
        default=0,
        help="🔑 the address index; can be used for PEM files, keyfiles of type mnemonic or Ledger devices (default: %(default)s)",
    )
    sub.add_argument("--sender-username", required=False, help="🖄 the username of the sender")
    sub.add_argument(
        "--hrp", required=False, type=str, help="The hrp used to convert the address to its bech32 representation"
    )


def add_guardian_wallet_args(args: list[str], sub: Any):
    sub.add_argument(
        "--guardian-service-url",
        type=str,
        help="the url of the guardian service",
        default="",
    )
    sub.add_argument(
        "--guardian-2fa-code",
        type=str,
        help="the 2fa code for the guardian",
        default="",
    )
    sub.add_argument(
        "--guardian-pem",
        help="🔑 the PEM file, if keyfile not provided",
    )
    sub.add_argument(
        "--guardian-keyfile",
        help="🔑 a JSON keyfile, if PEM not provided",
    )
    sub.add_argument(
        "--guardian-passfile",
        help="🔑 a file containing keyfile's password, if keyfile provided. If not provided, you'll be prompted to enter the password.",
    )
    sub.add_argument(
        "--guardian-ledger",
        action="store_true",
        default=False,
        help="🔐 bool flag for signing transaction using ledger",
    )
    sub.add_argument(
        "--guardian-wallet-index",
        type=int,
        default=0,
        help="🔑 the address index; can be used for PEM files, keyfiles of type mnemonic or Ledger devices (default: %(default)s)",
    )


def add_relayed_v3_wallet_args(args: list[str], sub: Any):
    sub.add_argument("--relayer-pem", help="🔑 the PEM file, if keyfile not provided")
    sub.add_argument("--relayer-keyfile", help="🔑 a JSON keyfile, if PEM not provided")
    sub.add_argument(
        "--relayer-passfile",
        help="🔑 a file containing keyfile's password, if keyfile provided. If not provided, you'll be prompted to enter the password.",
    )
    sub.add_argument(
        "--relayer-ledger",
        action="store_true",
        default=False,
        help="🔐 bool flag for signing transaction using ledger",
    )
    sub.add_argument(
        "--relayer-wallet-index",
        type=int,
        default=0,
        help="🔑 the address index; can be used for PEM files, keyfiles of type mnemonic or Ledger devices (default: %(default)s)",
    )


def add_proxy_arg(sub: Any):
    sub.add_argument("--proxy", type=str, help="🔗 the URL of the proxy")


def add_outfile_arg(sub: Any, what: str = ""):
    what = f"({what})" if what else ""
    sub.add_argument(
        "--outfile",
        type=FileType("w"),
        default=sys.stdout,
        help=f"where to save the output {what} (default: stdout)",
    )


def add_infile_arg(sub: Any, what: str = ""):
    what = f"({what})" if what else ""
    sub.add_argument("--infile", type=FileType("r"), required=True, help=f"input file {what}")


def add_omit_fields_arg(sub: Any):
    sub.add_argument(
        "--omit-fields",
        default="[]",
        type=str,
        required=False,
        help="omit fields in the output payload (default: %(default)s); fields should be passed as a string containing a list of fields (e.g. \"['field1', 'field2']\")",
    )


def add_token_transfers_args(sub: Any):
    sub.add_argument(
        "--token-transfers",
        nargs="+",
        help="token transfers for transfer & execute, as [token, amount] "
        "E.g. --token-transfers NFT-123456-0a 1 ESDT-987654 100000000",
    )


def add_metadata_arg(sub: Any):
    sub.add_argument(
        "--metadata-not-upgradeable",
        dest="metadata_upgradeable",
        action="store_false",
        help="‼ mark the contract as NOT upgradeable (default: upgradeable)",
    )
    sub.add_argument(
        "--metadata-not-readable",
        dest="metadata_readable",
        action="store_false",
        help="‼ mark the contract as NOT readable (default: readable)",
    )
    sub.add_argument(
        "--metadata-payable",
        dest="metadata_payable",
        action="store_true",
        help="‼ mark the contract as payable (default: not payable)",
    )
    sub.add_argument(
        "--metadata-payable-by-sc",
        dest="metadata_payable_by_sc",
        action="store_true",
        help="‼ mark the contract as payable by SC (default: not payable by SC)",
    )
    sub.set_defaults(metadata_upgradeable=True, metadata_payable=False)


def add_wait_result_and_timeout_args(sub: Any):
    sub.add_argument(
        "--wait-result",
        action="store_true",
        default=False,
        help="signal to wait for the transaction result - only valid if --send is set",
    )
    sub.add_argument(
        "--timeout",
        default=100,
        help="max num of seconds to wait for result" " - only valid if --wait-result is set",
    )


def parse_omit_fields_arg(args: Any) -> list[str]:
    literal = args.omit_fields
    parsed = ast.literal_eval(literal)
    return cast(list[str], parsed)


def prepare_account(args: Any):
    hrp = _get_address_hrp(args)

    if args.pem:
        return Account.new_from_pem(file_path=Path(args.pem), index=args.sender_wallet_index, hrp=hrp)
    elif args.keyfile:
        password = load_password(args)
        index = args.sender_wallet_index if args.sender_wallet_index != 0 else None

        return Account.new_from_keystore(
            file_path=Path(args.keyfile),
            password=password,
            address_index=index,
            hrp=hrp,
        )
    elif args.ledger:
        return LedgerAccount(address_index=args.sender_wallet_index)
    elif args.sender:
        file_path = resolve_address_config_path()
        if not file_path.is_file():
            raise AddressConfigFileError("The address config file was not found")

        file = read_address_config_file()
        if file == dict():
            raise AddressConfigFileError("Address config file is empty")

        addresses: dict[str, Any] = file["addresses"]
        wallet = addresses.get(args.sender, None)
        if not wallet:
            raise UnknownAddressAliasError(args.sender)

        logger.info(f"Using sender [{args.sender}] from address config.")
        return _load_wallet_from_address_config(wallet=wallet, hrp=hrp)
    else:
        active_address = get_active_address()
        if active_address == dict():
            logger.info("No default wallet found in address config.")
            raise NoWalletProvided()

        alias_of_default_wallet = read_address_config_file().get("active", "")
        logger.info(f"Using sender [{alias_of_default_wallet}] from address config.")

        return _load_wallet_from_address_config(wallet=active_address, hrp=hrp)


def _load_wallet_from_address_config(wallet: dict[str, str], hrp: str) -> Account:
    kind = wallet.get("kind", None)
    if not kind:
        raise AddressConfigFileError("'kind' field must be set in the address config")

    if kind not in ["pem", "keystore"]:
        raise InvalidAddressConfigValue("'kind' must be 'pem' or 'keystore'")

    path = wallet.get("path", None)
    if not path:
        raise AddressConfigFileError("'path' field must be set in the address config")
    path = Path(path)

    index = int(wallet.get("index", 0))

    if kind == "pem":
        return Account.new_from_pem(file_path=path, index=index, hrp=hrp)
    else:
        password = wallet.get("password", "")
        password_path = wallet.get("passwordPath", None)

        if not password and not password_path:
            raise AddressConfigFileError(
                "'password' or 'passwordPath' must be set in the address config for keystore wallets"
            )

        if password_path:
            password = Path(password_path).read_text().splitlines()[0].strip()

        return Account.new_from_keystore(file_path=path, password=password, address_index=index, hrp=hrp)


def _get_address_hrp(args: Any) -> str:
    """Use hrp provided by the user. If not provided, fetch from network. If proxy not provided, get hrp from config."""
    hrp: str = ""

    if hasattr(args, "hrp") and args.hrp:
        hrp = args.hrp
        return hrp

    if hasattr(args, "proxy") and args.proxy:
        hrp = _get_hrp_from_proxy(args)
    elif hasattr(args, "api") and args.api:
        hrp = _get_hrp_from_api(args)

    if hrp:
        return hrp

    return get_address_hrp()


def _get_hrp_from_proxy(args: Any) -> str:
    network_provider_config = config.get_config_for_network_providers()
    proxy = ProxyNetworkProvider(url=args.proxy, config=network_provider_config)
    network_config = proxy.get_network_config()
    hrp: str = network_config.raw.get("erd_address_hrp", "")
    return hrp


def _get_hrp_from_api(args: Any) -> str:
    network_provider_config = config.get_config_for_network_providers()
    proxy = ApiNetworkProvider(url=args.api, config=network_provider_config)
    network_config = proxy.get_network_config()
    hrp: str = network_config.raw.get("erd_address_hrp", "")
    return hrp


def load_guardian_account(args: Any) -> Union[IAccount, None]:
    hrp = _get_address_hrp(args)

    if args.guardian_pem:
        return Account.new_from_pem(file_path=Path(args.guardian_pem), index=args.guardian_wallet_index, hrp=hrp)
    elif args.guardian_keyfile:
        password = load_guardian_password(args)
        index = args.guardian_wallet_index if args.guardian_wallet_index != 0 else None

        return Account.new_from_keystore(
            file_path=Path(args.guardian_keyfile),
            password=password,
            address_index=index,
            hrp=hrp,
        )
    elif args.guardian_ledger:
        return LedgerAccount(address_index=args.guardian_wallet_index)

    return None


def get_guardian_address(guardian: Union[IAccount, None], args: Any) -> Union[Address, None]:
    address_from_account = guardian.address if guardian else None
    address_from_args = Address.new_from_bech32(args.guardian) if hasattr(args, "guardian") and args.guardian else None

    if not _is_matching_address(address_from_account, address_from_args):
        raise IncorrectWalletError("Guardian wallet does not match the guardian's address set in the arguments.")

    return address_from_account or address_from_args


def get_guardian_and_relayer_data(sender: str, args: Any) -> GuardianRelayerData:
    guardian = load_guardian_account(args)

    # get guardian address from account or from cli args
    guardian_address = get_guardian_address(guardian, args)

    relayer = load_relayer_account(args)
    relayer_address = get_relayer_address(relayer, args)

    guardian_and_relayer_data = GuardianRelayerData(
        guardian=guardian,
        guardian_address=guardian_address,
        relayer=relayer,
        relayer_address=relayer_address,
    )

    if guardian_and_relayer_data.guardian_address:
        guardian_and_relayer_data.guardian_service_url = args.guardian_service_url
        guardian_and_relayer_data.guardian_2fa_code = args.guardian_2fa_code
    else:
        _get_guardian_data_from_network(sender, args, guardian_and_relayer_data)

    return guardian_and_relayer_data


def _get_guardian_data_from_network(sender: str, args: Any, guardian_and_relayer_data: GuardianRelayerData):
    """Updates the `guardian_and_relayer_data` parameter, that is later used."""

    # if guardian not provided, get guardian from the network
    guardian_data = _get_guardian_data(sender, args.proxy)

    if guardian_data:
        guardian_and_relayer_data.guardian_address = Address.new_from_bech32(guardian_data["guardian_address"])

        # if tcs is used, set url, else get service url from args
        tcs_url = guardian_data["cosigner_service_url"]
        guardian_and_relayer_data.guardian_service_url = tcs_url if tcs_url else args.guardian_service_url

    if guardian_and_relayer_data.guardian_service_url:
        guardian_and_relayer_data.guardian_2fa_code = _ask_for_2fa_code(args)


def _get_guardian_data(address: str, proxy_url: str) -> Union[dict[str, str], None]:
    if not proxy_url:
        return None

    guardian_data = _fetch_guardian_data(address, proxy_url)

    if not bool(guardian_data.get("guarded", "")):
        return None

    active_guardian = guardian_data.get("activeGuardian", {})

    guardian_address = active_guardian.get("address", "")
    service_id = active_guardian.get("serviceUID", "")

    cosigner_service_url = ""

    if service_id == TCS_SERVICE_ID:
        chain_id = _fetch_chain_id(proxy_url)
        cosigner_service_url = get_trusted_cosigner_service_url_by_chain_id(chain_id)

    return {
        "guardian_address": guardian_address,
        "cosigner_service_url": cosigner_service_url,
    }


def _fetch_guardian_data(address: str, proxy_url: str) -> dict[str, Any]:
    network_provider_config = config.get_config_for_network_providers()
    proxy = ProxyNetworkProvider(url=proxy_url, config=network_provider_config)

    response = proxy.do_get_generic(f"/address/{address}/guardian-data").to_dictionary()
    guardian_data: dict[str, Any] = response.get("guardianData", {})
    return guardian_data


def _ask_for_2fa_code(args: Any) -> str:
    code: str = args.guardian_2fa_code
    if not code:
        code = input("Please enter the two factor authentication code: ")
    return code


def get_relayer_address(relayer: Union[IAccount, None], args: Any) -> Union[Address, None]:
    address_from_account = relayer.address if relayer else None
    address_from_args = Address.new_from_bech32(args.relayer) if hasattr(args, "relayer") and args.relayer else None

    if not _is_matching_address(address_from_account, address_from_args):
        raise IncorrectWalletError("Relayer wallet does not match the relayer's address set in the arguments.")

    return address_from_account or address_from_args


def _is_matching_address(account_address: Union[Address, None], args_address: Union[Address, None]) -> bool:
    if account_address and args_address and account_address != args_address:
        return False
    return True


def load_relayer_account(args: Any) -> Union[IAccount, None]:
    hrp = _get_address_hrp(args)

    if args.relayer_pem:
        return Account.new_from_pem(file_path=Path(args.relayer_pem), index=args.relayer_wallet_index, hrp=hrp)
    elif args.relayer_keyfile:
        password = load_relayer_password(args)
        index = args.relayer_wallet_index if args.relayer_wallet_index != 0 else None

        return Account.new_from_keystore(
            file_path=Path(args.relayer_keyfile),
            password=password,
            address_index=index,
            hrp=hrp,
        )
    elif args.relayer_ledger:
        return LedgerAccount(address_index=args.relayer_wallet_index)

    return None


def get_current_nonce_for_address(address: Address, proxy_url: Union[str, None]) -> int:
    if not proxy_url:
        raise ArgumentsNotProvidedError("If `--nonce` is not explicitly provided, `--proxy` must be provided")

    network_provider_config = config.get_config_for_network_providers()
    proxy = ProxyNetworkProvider(url=proxy_url, config=network_provider_config)
    return proxy.get_account(address).nonce


@cache
def get_chain_id(proxy_url: str, chain_id: Optional[str] = None) -> str:
    """We know and have already validated that if chainID is not provided, proxy is provided."""
    if chain_id:
        return chain_id

    return _fetch_chain_id(proxy_url)


@cache
def _fetch_chain_id(proxy_url: str) -> str:
    network_provider_config = config.get_config_for_network_providers()
    proxy = ProxyNetworkProvider(url=proxy_url, config=network_provider_config)
    return proxy.get_network_config().chain_id


def add_broadcast_args(sub: Any, simulate: bool = True):
    sub.add_argument(
        "--send",
        action="store_true",
        default=False,
        help="✓ whether to broadcast the transaction (default: %(default)s)",
    )

    if simulate:
        sub.add_argument(
            "--simulate",
            action="store_true",
            default=False,
            help="whether to simulate the transaction (default: %(default)s)",
        )


def send_or_simulate(tx: Transaction, args: Any, dump_output: bool = True) -> CLIOutputBuilder:
    network_provider_config = config.get_config_for_network_providers()
    proxy = ProxyNetworkProvider(url=args.proxy, config=network_provider_config)

    is_set_wait_result = hasattr(args, "wait_result") and args.wait_result
    is_set_send = hasattr(args, "send") and args.send
    is_set_simulate = hasattr(args, "simulate") and args.simulate

    send_wait_result = is_set_wait_result and is_set_send and not is_set_simulate
    send_only = is_set_send and not (is_set_wait_result or is_set_simulate)
    simulate = is_set_simulate and not (send_only or send_wait_result)

    output_builder = CLIOutputBuilder()
    output_builder.set_emitted_transaction(tx)
    outfile = args.outfile if hasattr(args, "outfile") else None

    hash = b""
    try:
        if send_wait_result:
            _confirm_continuation_if_required(tx)

            transaction_on_network = send_and_wait_for_result(tx, proxy, args.timeout)
            output_builder.set_awaited_transaction(transaction_on_network)
        elif send_only:
            _confirm_continuation_if_required(tx)

            hash = proxy.send_transaction(tx)
            output_builder.set_emitted_transaction_hash(hash.hex())
        elif simulate:
            simulation = Simulator(proxy).run(tx)
            output_builder.set_simulation_results(simulation)
    finally:
        output_transaction = output_builder.build()

        if dump_output:
            utils.dump_out_json(output_transaction, outfile=outfile)

        if send_only and hash:
            cli_config = MxpyEnv.from_active_env()
            log_explorer_transaction(
                chain=output_transaction["emittedTransaction"]["chainID"],
                transaction_hash=output_transaction["emittedTransactionHash"],
                explorer_url=cli_config.explorer_url,
            )

    return output_builder


def _confirm_continuation_if_required(tx: Transaction) -> None:
    env = MxpyEnv.from_active_env()

    if env.ask_confirmation:
        transaction = tx.to_dictionary()

        # decode the data field from base64 if it exists
        data = base64.b64decode(transaction.get("data", "")).decode()
        transaction["data"] = data if data else ""

        utils.dump_out_json(transaction)
        confirm_continuation("You are about to send the above transaction. Do you want to continue?")


def prepare_sender(args: Any):
    """Returns the sender's account.
    If no account was provided, will raise an exception."""
    sender = prepare_account(args)
    sender.nonce = (
        int(args.nonce) if args.nonce is not None else get_current_nonce_for_address(sender.address, args.proxy)
    )
    return sender


def prepare_guardian(args: Any) -> tuple[Union[IAccount, None], Union[Address, None]]:
    """Reurns a tuple containing the guardians's account and the account's address.
    If no account or address were provided, will return (None, None)."""
    guardian = load_guardian_account(args)
    guardian_address = get_guardian_address(guardian, args)
    return guardian, guardian_address


def prepare_relayer(args: Any) -> tuple[Union[IAccount, None], Union[Address, None]]:
    """Reurns a tuple containing the relayer's account and the account's address.
    If no account or address were provided, will return (None, None)."""
    relayer = load_relayer_account(args)
    relayer_address = get_relayer_address(relayer, args)
    return relayer, relayer_address


def prepare_guardian_relayer_data(args: Any) -> GuardianRelayerData:
    guardian, guardian_address = prepare_guardian(args)
    relayer, relayer_address = prepare_relayer(args)
    return GuardianRelayerData(
        guardian=guardian,
        guardian_address=guardian_address,
        relayer=relayer,
        relayer_address=relayer_address,
    )


def prepare_token_transfers(transfers: list[str]) -> list[TokenTransfer]:
    """Converts a list of token transfers as received from the CLI to a list of TokenTransfer objects."""
    token_computer = TokenComputer()
    token_transfers: list[TokenTransfer] = []

    for i in range(0, len(transfers) - 1, 2):
        extended_identifier = transfers[i]
        amount = int(transfers[i + 1])
        nonce = token_computer.extract_nonce_from_extended_identifier(extended_identifier)
        identifier = token_computer.extract_identifier_from_extended_identifier(extended_identifier)

        token = Token(identifier, nonce)
        transfer = TokenTransfer(token, amount)
        token_transfers.append(transfer)

    return token_transfers


def set_proxy_from_config_if_not_provided(args: Any) -> None:
    """This function modifies the `args` object by setting the proxy from the config if not already set. If proxy is not needed (chainID and nonce are provided), the proxy will not be set."""
    if not args.proxy:
        if hasattr(args, "chain") and args.chain and hasattr(args, "nonce") and args.nonce is not None:
            return

        env = MxpyEnv.from_active_env()
        if env.proxy_url:
            logger.info(f"Using proxy URL from config: {env.proxy_url}")
            args.proxy = env.proxy_url
