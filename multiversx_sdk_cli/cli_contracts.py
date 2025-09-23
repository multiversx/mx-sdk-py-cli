import hashlib
import json
import logging
import os
from pathlib import Path
from typing import Any

import requests
from multiversx_sdk import (
    Address,
    AddressComputer,
    Message,
    ProxyNetworkProvider,
    SmartContractController,
    Transaction,
)
from multiversx_sdk.abi import Abi

from multiversx_sdk_cli import cli_shared, utils
from multiversx_sdk_cli.args_converter import convert_args_to_typed_values
from multiversx_sdk_cli.args_validation import (
    validate_broadcast_args,
    validate_chain_id_args,
    validate_proxy_argument,
    validate_transaction_args,
)
from multiversx_sdk_cli.cli_output import CLIOutputBuilder
from multiversx_sdk_cli.config import get_config_for_network_providers
from multiversx_sdk_cli.config_env import MxpyEnv
from multiversx_sdk_cli.constants import NUMBER_OF_SHARDS
from multiversx_sdk_cli.contract_verification import trigger_contract_verification
from multiversx_sdk_cli.docker import is_docker_installed, run_docker
from multiversx_sdk_cli.errors import BadUsage, DockerMissingError, QueryContractError
from multiversx_sdk_cli.ux import show_warning

logger = logging.getLogger("cli.contracts")


def setup_parser(args: list[str], subparsers: Any) -> Any:
    parser = cli_shared.add_group_subparser(
        subparsers,
        "contract",
        "Deploy, upgrade and interact with Smart Contracts",
    )
    subparsers = parser.add_subparsers()

    output_description = CLIOutputBuilder.describe(
        with_contract=True, with_transaction_on_network=True, with_simulation=True
    )

    sub = cli_shared.add_command_subparser(
        subparsers,
        "contract",
        "deploy",
        f"Deploy a Smart Contract.{output_description}",
    )
    _add_bytecode_arg(sub)
    _add_contract_abi_arg(sub)
    cli_shared.add_metadata_arg(sub)
    cli_shared.add_outfile_arg(sub)
    cli_shared.add_wallet_args(args, sub)
    cli_shared.add_proxy_arg(sub)
    cli_shared.add_tx_args(args, sub, with_receiver=False, with_data=False)
    _add_arguments_arg(sub)
    cli_shared.add_wait_result_and_timeout_args(sub)
    cli_shared.add_broadcast_args(sub)
    cli_shared.add_guardian_wallet_args(args, sub)
    cli_shared.add_relayed_v3_wallet_args(args, sub)

    sub.set_defaults(func=deploy)

    sub = cli_shared.add_command_subparser(
        subparsers,
        "contract",
        "call",
        f"Interact with a Smart Contract (execute function).{output_description}",
    )
    _add_contract_arg(sub)
    _add_contract_abi_arg(sub)
    cli_shared.add_outfile_arg(sub)
    cli_shared.add_wallet_args(args, sub)
    cli_shared.add_proxy_arg(sub)
    cli_shared.add_tx_args(args, sub, with_receiver=False, with_data=False)
    _add_function_arg(sub)
    _add_arguments_arg(sub)
    cli_shared.add_token_transfers_args(sub)
    cli_shared.add_wait_result_and_timeout_args(sub)
    cli_shared.add_broadcast_args(sub)
    cli_shared.add_guardian_wallet_args(args, sub)
    cli_shared.add_relayed_v3_wallet_args(args, sub)

    sub.set_defaults(func=call)

    sub = cli_shared.add_command_subparser(
        subparsers,
        "contract",
        "upgrade",
        f"Upgrade a previously-deployed Smart Contract.{output_description}",
    )
    _add_contract_arg(sub)
    _add_contract_abi_arg(sub)
    cli_shared.add_outfile_arg(sub)
    _add_bytecode_arg(sub)
    cli_shared.add_metadata_arg(sub)
    cli_shared.add_wallet_args(args, sub)
    cli_shared.add_proxy_arg(sub)
    cli_shared.add_tx_args(args, sub, with_receiver=False, with_data=False)
    _add_arguments_arg(sub)
    cli_shared.add_wait_result_and_timeout_args(sub)
    cli_shared.add_broadcast_args(sub)
    cli_shared.add_guardian_wallet_args(args, sub)
    cli_shared.add_relayed_v3_wallet_args(args, sub)

    sub.set_defaults(func=upgrade)

    sub = cli_shared.add_command_subparser(
        subparsers, "contract", "query", "Query a Smart Contract (call a pure function)"
    )
    _add_contract_arg(sub)
    _add_contract_abi_arg(sub)
    cli_shared.add_proxy_arg(sub)
    _add_function_arg(sub)
    _add_arguments_arg(sub)
    sub.set_defaults(func=query)

    sub = cli_shared.add_command_subparser(
        subparsers,
        "contract",
        "verify",
        "Verify the authenticity of the code of a deployed Smart Contract",
    )

    sub.add_argument(
        "--packaged-src",
        required=True,
        help="JSON file containing the source code of the contract",
    )

    _add_contract_arg(sub)
    sub.add_argument(
        "--verifier-url",
        required=True,
        help="the url of the service that validates the contract",
    )
    sub.add_argument("--docker-image", required=True, help="the docker image used for the build")
    sub.add_argument(
        "--contract-variant",
        required=False,
        default=None,
        help="in case of a multicontract, specify the contract variant you want to verify",
    )
    cli_shared.add_wallet_args(args, sub)
    sub.add_argument(
        "--skip-confirmation",
        "-y",
        dest="skip_confirmation",
        action="store_true",
        default=False,
        help="can be used to skip the confirmation prompt",
    )
    sub.set_defaults(func=verify)

    sub = cli_shared.add_command_subparser(
        subparsers,
        "contract",
        "unverify",
        "Unverify a previously verified Smart Contract",
    )

    _add_contract_arg(sub)
    sub.add_argument(
        "--code-hash",
        required=True,
        help="the code hash of the contract",
    )
    sub.add_argument(
        "--verifier-url",
        required=True,
        help="the url of the service that validates the contract",
    )
    cli_shared.add_wallet_args(args, sub)
    sub.set_defaults(func=unverify)

    sub = cli_shared.add_command_subparser(
        subparsers,
        "contract",
        "reproducible-build",
        "Build a Smart Contract and get the same output as a previously built Smart Contract",
    )
    _add_project_arg(sub)
    _add_build_options_args(sub)
    sub.add_argument(
        "--docker-image",
        required=True,
        type=str,
        help="the docker image tag used to build the contract",
    )
    sub.add_argument(
        "--contract",
        type=str,
        help="contract to build (contract name, as found in Cargo.toml)",
    )
    sub.add_argument("--no-docker-interactive", action="store_true", default=False)
    sub.add_argument("--no-docker-tty", action="store_true", default=False)
    sub.add_argument(
        "--no-default-platform",
        action="store_true",
        default=False,
        help="do not set DOCKER_DEFAULT_PLATFORM environment variable to 'linux/amd64'",
    )
    sub.set_defaults(func=do_reproducible_build)

    sub = cli_shared.add_command_subparser(
        subparsers, "contract", "build", "Build a Smart Contract project. This command is DISABLED."
    )
    sub.set_defaults(func=build)

    parser.epilog = cli_shared.build_group_epilog(subparsers)
    return subparsers


def _add_project_arg(sub: Any):
    sub.add_argument(
        "project",
        nargs="?",
        default=os.getcwd(),
        help="the project directory (default: current directory)",
    )


def _add_build_options_args(sub: Any):
    sub.add_argument(
        "--debug",
        action="store_true",
        default=False,
        help="set debug flag (default: %(default)s)",
    )
    sub.add_argument(
        "--no-optimization",
        action="store_true",
        default=False,
        help="bypass optimizations (for clang) (default: %(default)s)",
    )
    sub.add_argument(
        "--no-wasm-opt",
        action="store_true",
        default=False,
        help="do not optimize wasm files after the build (default: %(default)s)",
    )
    sub.add_argument(
        "--cargo-target-dir",
        type=str,
        help="for rust projects, forward the parameter to Cargo",
    )
    sub.add_argument(
        "--wasm-symbols",
        action="store_true",
        default=False,
        help="for rust projects, does not strip the symbols from the wasm output. Useful for analysing the bytecode. Creates larger wasm files. Avoid in production (default: %(default)s)",
    )
    sub.add_argument(
        "--wasm-name",
        type=str,
        help="for rust projects, optionally specify the name of the wasm bytecode output file",
    )
    sub.add_argument(
        "--wasm-suffix",
        type=str,
        help="for rust projects, optionally specify the suffix of the wasm bytecode output file",
    )


def _add_bytecode_arg(sub: Any):
    sub.add_argument(
        "--bytecode",
        type=str,
        required=True,
        help="the file containing the WASM bytecode",
    )


def _add_contract_arg(sub: Any):
    sub.add_argument("contract", type=str, help="🖄 the bech32 address of the Smart Contract")


def _add_contract_abi_arg(sub: Any):
    sub.add_argument("--abi", type=str, help="the ABI file of the Smart Contract")


def _add_function_arg(sub: Any):
    sub.add_argument("--function", required=True, type=str, help="the function to call")


def _add_arguments_arg(sub: Any):
    sub.add_argument(
        "--arguments",
        nargs="+",
        default=[],
        help="arguments for the contract transaction, as [number, bech32-address, ascii string, "
        "boolean] or hex-encoded. E.g. --arguments 42 0x64 1000 0xabba str:TOK-a1c2ef true addr:erd1[..]",
    )
    sub.add_argument(
        "--arguments-file",
        type=str,
        help="a json file containing the arguments. ONLY if abi file is provided. "
        "E.g. [{ 'to': 'erd1...', 'amount': 10000000000 }]",
    )


def build(args: Any):
    message = """This command cannot build smart contracts anymore.

The primary tool for building smart contracts is `sc-meta`.
To install `sc-meta` check out the documentation: https://docs.multiversx.com/sdk-and-tools/troubleshooting/rust-setup.
After installing, use the `sc-meta all build` command. To learn more about `sc-meta`, check out this page: https://docs.multiversx.com/developers/meta/sc-meta-cli/#calling-build."""
    show_warning(message)


def _initialize_controller(args: Any) -> SmartContractController:
    chain_id = cli_shared.get_chain_id(args.proxy, args.chain)
    config = get_config_for_network_providers()
    proxy_url = args.proxy if args.proxy else ""
    proxy = ProxyNetworkProvider(url=proxy_url, config=config)
    abi = Abi.load(Path(args.abi)) if args.abi else None
    gas_estimator = cli_shared.initialize_gas_limit_estimator(args)

    return SmartContractController(
        chain_id=chain_id,
        network_provider=proxy,
        abi=abi,
        gas_limit_estimator=gas_estimator,
    )


def _ensure_args_for_gas_estimation(args: Any):
    if not args.proxy and not args.gas_limit:
        raise BadUsage("To estimate the gas limit, you need to provide `--proxy` or set a value using `--gas-limit`")


def deploy(args: Any):
    logger.debug("deploy")

    validate_transaction_args(args)
    validate_broadcast_args(args)
    validate_chain_id_args(args)

    _ensure_args_for_gas_estimation(args)

    sender = cli_shared.prepare_sender(args)
    guardian_and_relayer_data = cli_shared.get_guardian_and_relayer_data(
        sender=sender.address.to_bech32(),
        args=args,
    )

    arguments, should_prepare_args = _get_contract_arguments(args)
    if should_prepare_args:
        arguments = convert_args_to_typed_values(arguments)

    controller = _initialize_controller(args)
    tx = controller.create_transaction_for_deploy(
        sender=sender,
        nonce=sender.nonce,
        bytecode=Path(args.bytecode),
        arguments=arguments,
        native_transfer_amount=int(args.value),
        is_upgradeable=args.metadata_upgradeable,
        is_readable=args.metadata_readable,
        is_payable=args.metadata_payable,
        is_payable_by_sc=args.metadata_payable_by_sc,
        guardian=guardian_and_relayer_data.guardian.address if guardian_and_relayer_data.guardian else None,
        relayer=guardian_and_relayer_data.relayer.address if guardian_and_relayer_data.relayer else None,
        gas_limit=args.gas_limit,
        gas_price=args.gas_price,
    )

    address_computer = AddressComputer(NUMBER_OF_SHARDS)
    contract_address = address_computer.compute_contract_address(deployer=sender.address, deployment_nonce=tx.nonce)

    logger.info("Contract address: %s", contract_address.to_bech32())

    cli_config = MxpyEnv.from_active_env()
    utils.log_explorer_contract_address(
        chain=cli_shared.get_chain_id(args.proxy, args.chain),
        address=contract_address.to_bech32(),
        explorer_url=cli_config.explorer_url,
    )

    cli_shared.alter_transaction_and_sign_again_if_needed(
        args=args,
        tx=tx,
        sender=sender,
        guardian_and_relayer_data=guardian_and_relayer_data,
    )
    _send_or_simulate(tx, contract_address, args)


def call(args: Any):
    logger.debug("call")

    validate_transaction_args(args)
    validate_broadcast_args(args)
    validate_chain_id_args(args)

    _ensure_args_for_gas_estimation(args)

    sender = cli_shared.prepare_sender(args)
    guardian_and_relayer_data = cli_shared.get_guardian_and_relayer_data(
        sender=sender.address.to_bech32(),
        args=args,
    )

    arguments, should_prepare_args = _get_contract_arguments(args)
    if should_prepare_args:
        arguments = convert_args_to_typed_values(arguments)

    token_transfers = []
    if args.token_transfers:
        token_transfers = cli_shared.prepare_token_transfers(args.token_transfers)

    contract_address = Address.new_from_bech32(args.contract)
    controller = _initialize_controller(args)

    tx = controller.create_transaction_for_execute(
        sender=sender,
        nonce=sender.nonce,
        contract=contract_address,
        function=args.function,
        arguments=arguments,
        native_transfer_amount=int(args.value),
        token_transfers=token_transfers,
        guardian=guardian_and_relayer_data.guardian.address if guardian_and_relayer_data.guardian else None,
        relayer=guardian_and_relayer_data.relayer.address if guardian_and_relayer_data.relayer else None,
        gas_limit=args.gas_limit,
        gas_price=args.gas_price,
    )

    cli_shared.alter_transaction_and_sign_again_if_needed(
        args=args,
        tx=tx,
        sender=sender,
        guardian_and_relayer_data=guardian_and_relayer_data,
    )
    _send_or_simulate(tx, contract_address, args)


def upgrade(args: Any):
    logger.debug("upgrade")

    validate_transaction_args(args)
    validate_broadcast_args(args)
    validate_chain_id_args(args)

    _ensure_args_for_gas_estimation(args)

    sender = cli_shared.prepare_sender(args)
    guardian_and_relayer_data = cli_shared.get_guardian_and_relayer_data(
        sender=sender.address.to_bech32(),
        args=args,
    )

    arguments, should_prepare_args = _get_contract_arguments(args)
    if should_prepare_args:
        arguments = convert_args_to_typed_values(arguments)

    contract_address = Address.new_from_bech32(args.contract)
    controller = _initialize_controller(args)

    tx = controller.create_transaction_for_upgrade(
        sender=sender,
        nonce=sender.nonce,
        contract=contract_address,
        bytecode=Path(args.bytecode),
        arguments=arguments,
        native_transfer_amount=int(args.value),
        is_upgradeable=args.metadata_upgradeable,
        is_readable=args.metadata_readable,
        is_payable=args.metadata_payable,
        is_payable_by_sc=args.metadata_payable_by_sc,
        guardian=guardian_and_relayer_data.guardian.address if guardian_and_relayer_data.guardian else None,
        relayer=guardian_and_relayer_data.relayer.address if guardian_and_relayer_data.relayer else None,
        gas_limit=args.gas_limit,
        gas_price=args.gas_price,
    )

    cli_shared.alter_transaction_and_sign_again_if_needed(
        args=args,
        tx=tx,
        sender=sender,
        guardian_and_relayer_data=guardian_and_relayer_data,
    )
    _send_or_simulate(tx, contract_address, args)


def query(args: Any):
    logger.debug("query")

    validate_proxy_argument(args)

    abi = Abi.load(Path(args.abi)) if args.abi else None
    contract_address = Address.new_from_bech32(args.contract)
    function = args.function

    arguments, should_prepare_args = _get_contract_arguments(args)
    if should_prepare_args:
        arguments = convert_args_to_typed_values(arguments)

    network_provider_config = get_config_for_network_providers()
    proxy = ProxyNetworkProvider(url=args.proxy, config=network_provider_config)

    controller = SmartContractController(
        chain_id="",
        network_provider=proxy,
        abi=abi,
    )

    try:
        result = controller.query(
            contract=contract_address,
            function=function,
            arguments=arguments,
        )
    except Exception as e:
        raise QueryContractError("Couldn't query contract: ", e)

    utils.dump_out_json(result)


def _get_contract_arguments(args: Any) -> tuple[list[Any], bool]:
    json_args = json.loads(Path(args.arguments_file).expanduser().read_text()) if args.arguments_file else None

    if json_args and args.arguments:
        raise Exception("Provide either '--arguments' or '--arguments-file'.")

    if json_args:
        if not args.abi:
            raise Exception("Can't use '--arguments-file' without providing the Abi file.")

        return json_args, False
    else:
        return args.arguments, True


def _send_or_simulate(tx: Transaction, contract_address: Address, args: Any):
    output_builder = cli_shared.send_or_simulate(tx, args, dump_output=False)
    output_builder.set_contract_address(contract_address)
    utils.dump_out_json(output_builder.build(), outfile=args.outfile)


def verify(args: Any) -> None:
    if not args.skip_confirmation:
        response = input(
            "Are you sure you want to verify the contract? This will publish the contract's source code, which will be displayed on the MultiversX Explorer (y/n): "
        )
        if response.lower() != "y":
            logger.info("Contract verification cancelled.")
            return

    contract = Address.new_from_bech32(args.contract)
    verifier_url = args.verifier_url

    packaged_src = Path(args.packaged_src).expanduser().resolve()

    owner = cli_shared.prepare_account(args)
    docker_image = args.docker_image
    contract_variant = args.contract_variant

    trigger_contract_verification(packaged_src, owner, contract, verifier_url, docker_image, contract_variant)
    logger.info("Contract verification request completed!")


def unverify(args: Any) -> None:
    account = cli_shared.prepare_account(args)
    contract: str = args.contract
    code_hash: str = args.code_hash
    verifier_url: str = f"{args.verifier_url}/verifier"

    payload = {
        "contract": contract,
        "codeHash": code_hash,
    }

    serialized_payload = json.dumps(payload, separators=(",", ":")).encode("utf-8")
    hash = hashlib.sha256(serialized_payload).hexdigest()
    message_to_sign = (contract + hash).encode("utf-8")

    signature = account.sign_message(Message(message_to_sign))

    request_payload = {
        "signature": signature.hex(),
        "payload": payload,
    }

    headers = {"Content-type": "application/json"}
    response = requests.delete(verifier_url, json=request_payload, headers=headers)
    logger.info(f"Your request to unverify contract {contract} was submitted.")
    print(response.json().get("message"))


def do_reproducible_build(args: Any):
    project_path = args.project
    docker_image = args.docker_image
    contract_path = args.contract
    docker_interactive = not args.no_docker_interactive
    docker_tty = not args.no_docker_tty
    no_default_platform = args.no_default_platform

    project_path = Path(project_path).expanduser().resolve()
    output_path = project_path / "output-docker"
    artifacts_path = output_path / "artifacts.json"

    utils.ensure_folder(output_path)

    options = args.__dict__
    no_wasm_opt = options.get("no_wasm_opt", False)

    if not is_docker_installed():
        raise DockerMissingError()

    logger.info("Starting the docker run...")
    run_docker(
        docker_image,
        project_path,
        contract_path,
        output_path,
        no_wasm_opt,
        docker_interactive,
        docker_tty,
        no_default_platform,
    )

    logger.info("Docker build ran successfully!")
    logger.info(f"Inspect summary of generated artifacts here: {artifacts_path}")
    logger.info("You can deploy you Smart Contract, then verify it using the mxpy contract verify command")
