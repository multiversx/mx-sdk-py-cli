import logging
import os
from pathlib import Path
from typing import Any, List

from multiversx_sdk_core import Address, AddressComputer, Transaction
from multiversx_sdk_core.transaction_factories import TransactionsFactoryConfig
from multiversx_sdk_network_providers.proxy_network_provider import \
    ProxyNetworkProvider

from multiversx_sdk_cli import cli_shared, errors, projects, utils
from multiversx_sdk_cli.accounts import Account, LedgerAccount
from multiversx_sdk_cli.cli_output import CLIOutputBuilder
from multiversx_sdk_cli.cli_password import load_password
from multiversx_sdk_cli.constants import NUMBER_OF_SHARDS
from multiversx_sdk_cli.contract_verification import \
    trigger_contract_verification
from multiversx_sdk_cli.contracts import SmartContract, query_contract
from multiversx_sdk_cli.cosign_transaction import cosign_transaction
from multiversx_sdk_cli.docker import is_docker_installed, run_docker
from multiversx_sdk_cli.errors import DockerMissingError, NoWalletProvided
from multiversx_sdk_cli.interfaces import IAddress
from multiversx_sdk_cli.projects.core import get_project_paths_recursively
from multiversx_sdk_cli.projects.templates import Contract
from multiversx_sdk_cli.ux import show_message

logger = logging.getLogger("cli.contracts")


def setup_parser(args: List[str], subparsers: Any) -> Any:
    parser = cli_shared.add_group_subparser(subparsers, "contract", "Build, deploy, upgrade and interact with Smart Contracts")
    subparsers = parser.add_subparsers()

    sub = cli_shared.add_command_subparser(subparsers, "contract", "new",
                                           "Create a new Smart Contract project based on a template.")
    sub.add_argument("--name", help="The name of the contract. If missing, the name of the template will be used.")
    sub.add_argument("--template", required=True, help="the template to use")
    sub.add_argument("--tag", help="the framework version on which the contract should be created")
    sub.add_argument("--path", type=str, default=os.getcwd(),
                     help="the parent directory of the project (default: current directory)")
    sub.set_defaults(func=create)

    sub = cli_shared.add_command_subparser(subparsers, "contract", "templates",
                                           "List the available Smart Contract templates.")
    sub.add_argument("--tag", help="the sc-meta framework version referred to")
    sub.set_defaults(func=list_templates)

    sub = cli_shared.add_command_subparser(subparsers, "contract", "build",
                                           "Build a Smart Contract project.")
    _add_build_options_sc_meta(sub)
    sub.set_defaults(func=build)

    sub = cli_shared.add_command_subparser(subparsers, "contract", "clean", "Clean a Smart Contract project.")
    sub.add_argument("--path", default=os.getcwd(), help="the project directory (default: current directory)")
    sub.set_defaults(func=clean)

    sub = cli_shared.add_command_subparser(subparsers, "contract", "test", "Run scenarios (tests).")
    _add_project_arg(sub)
    sub.add_argument("--directory", default="scenarios",
                     help="🗀 the directory containing the tests (default: %(default)s)")
    sub.add_argument("--wildcard", required=False, help="wildcard to match only specific test files")
    _add_recursive_arg(sub)
    sub.set_defaults(func=run_tests)

    sub = cli_shared.add_command_subparser(subparsers, "contract", "report", "Print a detailed report of the smart contracts.")
    sub.add_argument("--skip-build", action="store_true", default=False, help="skips the step of building of the wasm contracts")
    sub.add_argument("--skip-twiggy", action="store_true", default=False, help="skips the steps of building the debug wasm files and running twiggy")
    sub.add_argument("--output-format", type=str, default="text-markdown", choices=["github-markdown", "text-markdown", "json"], help="report output format (default: %(default)s)")
    sub.add_argument("--output-file", type=Path, help="if specified, the output is written to a file, otherwise it's written to the standard output")
    sub.add_argument("--compare", type=Path, nargs='+', metavar=("report-1.json", "report-2.json"), help="create a comparison from two or more reports")
    _add_build_options_sc_meta(sub)
    sub.set_defaults(func=do_report)

    output_description = CLIOutputBuilder.describe(with_contract=True, with_transaction_on_network=True, with_simulation=True)
    sub = cli_shared.add_command_subparser(subparsers, "contract", "deploy", f"Deploy a Smart Contract.{output_description}")
    _add_bytecode_arg(sub)
    _add_metadata_arg(sub)
    cli_shared.add_outfile_arg(sub)
    cli_shared.add_wallet_args(args, sub)
    cli_shared.add_proxy_arg(sub)
    cli_shared.add_tx_args(args, sub, with_receiver=False, with_data=False, with_guardian=True)
    _add_arguments_arg(sub)
    sub.add_argument("--wait-result", action="store_true", default=False,
                     help="signal to wait for the transaction result - only valid if --send is set")
    sub.add_argument("--timeout", default=100, help="max num of seconds to wait for result"
                                                    " - only valid if --wait-result is set")
    cli_shared.add_broadcast_args(sub)
    cli_shared.add_guardian_wallet_args(args, sub)

    sub.set_defaults(func=deploy)

    sub = cli_shared.add_command_subparser(subparsers, "contract", "call",
                                           f"Interact with a Smart Contract (execute function).{output_description}")
    _add_contract_arg(sub)
    cli_shared.add_outfile_arg(sub)
    cli_shared.add_wallet_args(args, sub)
    cli_shared.add_proxy_arg(sub)
    cli_shared.add_tx_args(args, sub, with_receiver=False, with_data=False, with_guardian=True)
    _add_function_arg(sub)
    _add_arguments_arg(sub)
    sub.add_argument("--wait-result", action="store_true", default=False,
                     help="signal to wait for the transaction result - only valid if --send is set")
    sub.add_argument("--timeout", default=100, help="max num of seconds to wait for result"
                                                    " - only valid if --wait-result is set")
    cli_shared.add_broadcast_args(sub, relay=True)
    cli_shared.add_guardian_wallet_args(args, sub)

    sub.set_defaults(func=call)

    sub = cli_shared.add_command_subparser(subparsers, "contract", "upgrade",
                                           f"Upgrade a previously-deployed Smart Contract.{output_description}")
    _add_contract_arg(sub)
    cli_shared.add_outfile_arg(sub)
    _add_bytecode_arg(sub)
    _add_metadata_arg(sub)
    cli_shared.add_wallet_args(args, sub)
    cli_shared.add_proxy_arg(sub)
    cli_shared.add_tx_args(args, sub, with_receiver=False, with_data=False, with_guardian=True)
    _add_arguments_arg(sub)
    sub.add_argument("--wait-result", action="store_true", default=False,
                     help="signal to wait for the transaction result - only valid if --send is set")
    sub.add_argument("--timeout", default=100, help="max num of seconds to wait for result"
                                                    " - only valid if --wait-result is set")
    cli_shared.add_broadcast_args(sub)
    cli_shared.add_guardian_wallet_args(args, sub)

    sub.set_defaults(func=upgrade)

    sub = cli_shared.add_command_subparser(subparsers, "contract", "query",
                                           "Query a Smart Contract (call a pure function)")
    _add_contract_arg(sub)
    cli_shared.add_proxy_arg(sub)
    _add_function_arg(sub)
    _add_arguments_arg(sub)
    sub.set_defaults(func=query)

    sub = cli_shared.add_command_subparser(subparsers, "contract", "verify",
                                           "Verify the authenticity of the code of a deployed Smart Contract",
                                           )

    sub.add_argument(
        "--packaged-src", required=True, help="JSON file containing the source code of the contract"
    )

    _add_contract_arg(sub)
    sub.add_argument(
        "--verifier-url",
        required=True,
        help="the url of the service that validates the contract",
    )
    sub.add_argument("--docker-image", required=True, help="the docker image used for the build")
    sub.add_argument("--contract-variant", required=False, default=None, help="in case of a multicontract, specify the contract variant you want to verify")
    cli_shared.add_wallet_args(args, sub)
    sub.set_defaults(func=verify)

    sub = cli_shared.add_command_subparser(subparsers, "contract", "reproducible-build",
                                           "Build a Smart Contract and get the same output as a previously built Smart Contract")
    _add_project_arg(sub)
    _add_build_options_args(sub)
    sub.add_argument("--docker-image", required=True, type=str,
                     help="the docker image tag used to build the contract")
    sub.add_argument("--contract", type=str, help="relative path of the contract in the project")
    sub.add_argument("--no-docker-interactive", action="store_true", default=False)
    sub.add_argument("--no-docker-tty", action="store_true", default=False)
    sub.add_argument("--no-default-platform", action="store_true", default=False,
                     help="do not set DOCKER_DEFAULT_PLATFORM environment variable to 'linux/amd64'")
    sub.set_defaults(func=do_reproducible_build)

    parser.epilog = cli_shared.build_group_epilog(subparsers)
    return subparsers


def _add_project_arg(sub: Any):
    sub.add_argument("project", nargs='?', default=os.getcwd(),
                     help="🗀 the project directory (default: current directory)")


def _add_build_options_sc_meta(sub: Any):
    sub.add_argument("--path", default=os.getcwd(), help="the project directory (default: current directory)")
    sub.add_argument("--no-wasm-opt", action="store_true", default=False,
                     help="do not optimize wasm files after the build (default: %(default)s)")
    sub.add_argument("--wasm-symbols", action="store_true", default=False,
                     help="for rust projects, does not strip the symbols from the wasm output. Useful for analysing the bytecode. Creates larger wasm files. Avoid in production (default: %(default)s)")
    sub.add_argument("--wasm-name", type=str,
                     help="for rust projects, optionally specify the name of the wasm bytecode output file")
    sub.add_argument("--wasm-suffix", type=str,
                     help="for rust projects, optionally specify the suffix of the wasm bytecode output file")
    sub.add_argument("--target-dir", type=str, help="for rust projects, forward the parameter to Cargo")
    sub.add_argument("--wat", action="store_true", help="also generate a WAT file when building", default=False)
    sub.add_argument("--mir", action="store_true", help="also emit MIR files when building", default=False)
    sub.add_argument("--llvm-ir", action="store_true", help="also emit LL (LLVM) files when building", default=False)
    sub.add_argument("--ignore", help="ignore all directories with these names. [default: target]")
    sub.add_argument("--no-imports", action="store_true", default=False, help="skips extracting the EI imports after building the contracts")
    sub.add_argument("--no-abi-git-version", action="store_true", default=False, help="skips loading the Git version into the ABI")
    sub.add_argument("--twiggy-top", action="store_true", default=False, help="generate a twiggy top report after building")
    sub.add_argument("--twiggy-paths", action="store_true", default=False, help="generate a twiggy paths report after building")
    sub.add_argument("--twiggy-monos", action="store_true", default=False, help="generate a twiggy monos report after building")
    sub.add_argument("--twiggy-dominators", action="store_true", default=False, help="generate a twiggy dominators report after building")


def _add_build_options_args(sub: Any):
    sub.add_argument("--debug", action="store_true", default=False, help="set debug flag (default: %(default)s)")
    sub.add_argument("--no-optimization", action="store_true", default=False,
                     help="bypass optimizations (for clang) (default: %(default)s)")
    sub.add_argument("--no-wasm-opt", action="store_true", default=False,
                     help="do not optimize wasm files after the build (default: %(default)s)")
    sub.add_argument("--cargo-target-dir", type=str, help="for rust projects, forward the parameter to Cargo")
    sub.add_argument("--wasm-symbols", action="store_true", default=False,
                     help="for rust projects, does not strip the symbols from the wasm output. Useful for analysing the bytecode. Creates larger wasm files. Avoid in production (default: %(default)s)")
    sub.add_argument("--wasm-name", type=str,
                     help="for rust projects, optionally specify the name of the wasm bytecode output file")
    sub.add_argument("--wasm-suffix", type=str,
                     help="for rust projects, optionally specify the suffix of the wasm bytecode output file")


def _add_recursive_arg(sub: Any):
    sub.add_argument("-r", "--recursive", dest="recursive", action="store_true", help="locate projects recursively")


def _add_bytecode_arg(sub: Any):
    sub.add_argument("--bytecode", type=str, required=True,
                     help="the file containing the WASM bytecode")


def _add_contract_arg(sub: Any):
    sub.add_argument("contract", help="🖄 the address of the Smart Contract")


def _add_function_arg(sub: Any):
    sub.add_argument("--function", required=True, help="the function to call")


def _add_arguments_arg(sub: Any):
    sub.add_argument("--arguments", nargs='+',
                     help="arguments for the contract transaction, as [number, bech32-address, ascii string, "
                     "boolean] or hex-encoded. E.g. --arguments 42 0x64 1000 0xabba str:TOK-a1c2ef true erd1[..]")


def _add_metadata_arg(sub: Any):
    sub.add_argument("--metadata-not-upgradeable", dest="metadata_upgradeable", action="store_false",
                     help="‼ mark the contract as NOT upgradeable (default: upgradeable)")
    sub.add_argument("--metadata-not-readable", dest="metadata_readable", action="store_false",
                     help="‼ mark the contract as NOT readable (default: readable)")
    sub.add_argument("--metadata-payable", dest="metadata_payable", action="store_true",
                     help="‼ mark the contract as payable (default: not payable)")
    sub.add_argument("--metadata-payable-by-sc", dest="metadata_payable_by_sc", action="store_true",
                     help="‼ mark the contract as payable by SC (default: not payable by SC)")
    sub.set_defaults(metadata_upgradeable=True, metadata_payable=False)


def list_templates(args: Any):
    tag = args.tag
    contract = Contract(tag)
    templates = contract.get_contract_templates()
    show_message(templates)


def create(args: Any):
    name = args.name
    template = args.template
    tag = args.tag
    path = Path(args.path)

    contract = Contract(tag, name, template, path)
    contract.create_from_template()


def get_project_paths(args: Any) -> List[Path]:
    base_path = Path(args.project)
    recursive = bool(args.recursive)
    if recursive:
        return get_project_paths_recursively(base_path)
    return [base_path]


def clean(args: Any):
    project_path = args.path
    projects.clean_project(Path(project_path))


def build(args: Any):
    project_paths = [Path(args.path)]
    arg_list = cli_shared.convert_args_object_to_args_list(args)

    for project in project_paths:
        projects.build_project(project, arg_list)


def do_report(args: Any):
    args_dict = args.__dict__
    projects.do_report(args, args_dict)


def run_tests(args: Any):
    project_paths = get_project_paths(args)
    for project in project_paths:
        projects.run_tests(project, args)


def deploy(args: Any):
    logger.debug("deploy")
    cli_shared.check_guardian_and_options_args(args)
    cli_shared.check_broadcast_args(args)

    sender = _prepare_sender(args)
    cli_shared.prepare_chain_id_in_args(args)

    config = TransactionsFactoryConfig(args.chain)
    contract = SmartContract(config)

    address_computer = AddressComputer(NUMBER_OF_SHARDS)
    contract_address = address_computer.compute_contract_address(deployer=sender.address, deployment_nonce=sender.nonce)

    tx = contract.get_deploy_transaction(sender, args)
    tx = _sign_guarded_tx(args, tx)

    logger.info("Contract address: %s", contract_address.to_bech32())
    utils.log_explorer_contract_address(args.chain, contract_address.to_bech32())

    _send_or_simulate(tx, contract_address, args)


def _prepare_sender(args: Any) -> Account:
    sender: Account
    if args.ledger:
        sender = LedgerAccount(account_index=args.ledger_account_index, address_index=args.ledger_address_index)
    elif args.pem:
        sender = Account(pem_file=args.pem, pem_index=args.pem_index)
    elif args.keyfile:
        password = load_password(args)
        sender = Account(key_file=args.keyfile, password=password)
    else:
        raise errors.NoWalletProvided()

    sender.nonce = args.nonce
    if args.recall_nonce:
        sender.sync_nonce(ProxyNetworkProvider(args.proxy))

    return sender


def _prepare_signer(args: Any) -> Account:
    sender: Account
    if args.ledger:
        sender = LedgerAccount(
            account_index=args.ledger_account_index,
            address_index=args.ledger_address_index,
        )
    elif args.pem:
        sender = Account(pem_file=args.pem, pem_index=args.pem_index)
    elif args.keyfile:
        password = load_password(args)
        sender = Account(key_file=args.keyfile, password=password)
    else:
        raise errors.NoWalletProvided()

    return sender


def _sign_guarded_tx(args: Any, tx: Transaction) -> Transaction:
    try:
        guardian_account = cli_shared.prepare_guardian_account(args)
    except NoWalletProvided:
        guardian_account = None

    if guardian_account:
        tx.guardian_signature = bytes.fromhex(guardian_account.sign_transaction(tx))
    elif args.guardian:
        tx = cosign_transaction(tx, args.guardian_service_url, args.guardian_2fa_code)  # type: ignore

    return tx


def call(args: Any):
    logger.debug("call")
    cli_shared.check_guardian_and_options_args(args)
    cli_shared.check_broadcast_args(args)

    cli_shared.prepare_chain_id_in_args(args)
    sender = _prepare_sender(args)

    config = TransactionsFactoryConfig(args.chain)
    contract = SmartContract(config)
    contract_address = Address.new_from_bech32(args.contract)

    tx = contract.get_execute_transaction(sender, args)
    tx = _sign_guarded_tx(args, tx)

    _send_or_simulate(tx, contract_address, args)


def upgrade(args: Any):
    logger.debug("upgrade")
    cli_shared.check_guardian_and_options_args(args)
    cli_shared.check_broadcast_args(args)

    cli_shared.prepare_chain_id_in_args(args)
    sender = _prepare_sender(args)

    config = TransactionsFactoryConfig(args.chain)
    contract = SmartContract(config)
    contract_address = Address.new_from_bech32(args.contract)

    tx = contract.get_upgrade_transaction(sender, args)
    tx = _sign_guarded_tx(args, tx)

    _send_or_simulate(tx, contract_address, args)


def query(args: Any):
    logger.debug("query")

    # workaround so we can use the function bellow
    args.chain = ""
    cli_shared.prepare_chain_id_in_args(args)

    contract_address = Address.new_from_bech32(args.contract)

    proxy = ProxyNetworkProvider(args.proxy)
    function = args.function
    arguments = args.arguments or []

    result = query_contract(contract_address, proxy, function, arguments)
    utils.dump_out_json(result)


def _send_or_simulate(tx: Transaction, contract_address: IAddress, args: Any):
    output_builder = cli_shared.send_or_simulate(tx, args, dump_output=False)
    output_builder.set_contract_address(contract_address)
    utils.dump_out_json(output_builder.build(), outfile=args.outfile)


def verify(args: Any) -> None:
    contract = Address.from_bech32(args.contract)
    verifier_url = args.verifier_url

    packaged_src = Path(args.packaged_src).expanduser().resolve()

    owner = _prepare_signer(args)
    docker_image = args.docker_image
    contract_variant = args.contract_variant

    trigger_contract_verification(
        packaged_src, owner, contract, verifier_url, docker_image, contract_variant
    )
    logger.info("Contract verification request completed!")


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
    run_docker(docker_image, project_path, contract_path, output_path, no_wasm_opt, docker_interactive, docker_tty, no_default_platform)

    logger.info("Docker build ran successfully!")
    logger.info(f"Inspect summary of generated artifacts here: {artifacts_path}")
    logger.info("You can deploy you Smart Contract, then verify it using the mxpy contract verify command")
