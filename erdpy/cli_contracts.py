import logging
import os
from pathlib import Path
from typing import Any, Dict, List

from erdpy.contract_verification import trigger_contract_verification
from erdpy import cli_shared, errors, projects, utils
from erdpy.accounts import Account, Address, LedgerAccount
from erdpy.cli_output import CLIOutputBuilder
from erdpy.cli_password import load_password
from erdpy.contracts import CodeMetadata, SmartContract
from erdpy.projects import load_project
from erdpy.projects.core import get_project_paths_recursively
from erdpy.proxy.core import ElrondProxy
from erdpy.transactions import Transaction
from erdpy.docker import is_docker_installed, run_docker
from erdpy.errors import DockerMissingError

logger = logging.getLogger("cli.contracts")


def setup_parser(args: List[str], subparsers: Any) -> Any:
    parser = cli_shared.add_group_subparser(subparsers, "contract", "Build, deploy, upgrade and interact with Smart Contracts")
    subparsers = parser.add_subparsers()

    sub = cli_shared.add_command_subparser(subparsers, "contract", "new",
                                           "Create a new Smart Contract project based on a template.")
    sub.add_argument("name")
    sub.add_argument("--template", required=True, help="the template to use")
    sub.add_argument("--directory", type=str, default=os.getcwd(),
                     help="🗀 the parent directory of the project (default: current directory)")
    sub.set_defaults(func=create)

    sub = cli_shared.add_command_subparser(subparsers, "contract", "templates",
                                           "List the available Smart Contract templates.")
    sub.set_defaults(func=list_templates)

    sub = cli_shared.add_command_subparser(subparsers, "contract", "build",
                                           "Build a Smart Contract project using the appropriate buildchain.")
    _add_project_arg(sub)
    _add_recursive_arg(sub)
    _add_build_options_args(sub)
    sub.set_defaults(func=build)

    sub = cli_shared.add_command_subparser(subparsers, "contract", "clean", "Clean a Smart Contract project.")
    _add_project_arg(sub)
    _add_recursive_arg(sub)
    sub.set_defaults(func=clean)

    sub = cli_shared.add_command_subparser(subparsers, "contract", "test", "Run Mandos tests.")
    _add_project_arg(sub)
    sub.add_argument("--directory", default="mandos",
                     help="🗀 the directory containing the tests (default: %(default)s)")
    sub.add_argument("--wildcard", required=False, help="wildcard to match only specific test files")
    sub.set_defaults(func=run_tests)

    sub = cli_shared.add_command_subparser(subparsers, "contract", "report", "Print a detailed report of the smart contracts.")
    _add_project_arg(sub)
    sub.add_argument("--skip-build", action="store_true", default=False, help="skips the step of building of the wasm contracts")
    sub.add_argument("--skip-twiggy", action="store_true", default=False, help="skips the steps of building the debug wasm files and running twiggy")
    sub.add_argument("--output-format", type=str, default="text-markdown", choices=["github-markdown", "text-markdown", "json"], help="report output format (default: %(default)s)")
    sub.add_argument("--output-file", type=Path, help="if specified, the output is written to a file, otherwise it's written to the standard output")
    sub.add_argument("--compare", type=Path, nargs='+', metavar=("report-1.json", "report-2.json"), help="create a comparison from two or more reports")
    _add_build_options_args(sub)
    sub.set_defaults(func=do_report)

    output_description = CLIOutputBuilder.describe(with_contract=True, with_transaction_on_network=True, with_simulation=True)
    sub = cli_shared.add_command_subparser(subparsers, "contract", "deploy", f"Deploy a Smart Contract.{output_description}")
    _add_project_or_bytecode_arg(sub)
    _add_metadata_arg(sub)
    cli_shared.add_outfile_arg(sub)
    cli_shared.add_wallet_args(args, sub)
    cli_shared.add_proxy_arg(sub)
    cli_shared.add_tx_args(args, sub, with_receiver=False, with_data=False)
    _add_arguments_arg(sub)
    sub.add_argument("--wait-result", action="store_true", default=False,
                     help="signal to wait for the transaction result - only valid if --send is set")
    sub.add_argument("--timeout", default=100, help="max num of seconds to wait for result"
                                                    " - only valid if --wait-result is set")
    cli_shared.add_broadcast_args(sub)

    sub.set_defaults(func=deploy)

    sub = cli_shared.add_command_subparser(subparsers, "contract", "call",
                                           f"Interact with a Smart Contract (execute function).{output_description}")
    _add_contract_arg(sub)
    cli_shared.add_outfile_arg(sub)
    cli_shared.add_wallet_args(args, sub)
    cli_shared.add_proxy_arg(sub)
    cli_shared.add_tx_args(args, sub, with_receiver=False, with_data=False)
    _add_function_arg(sub)
    _add_arguments_arg(sub)
    sub.add_argument("--wait-result", action="store_true", default=False,
                     help="signal to wait for the transaction result - only valid if --send is set")
    sub.add_argument("--timeout", default=100, help="max num of seconds to wait for result"
                                                    " - only valid if --wait-result is set")
    cli_shared.add_broadcast_args(sub, relay=True)

    sub.set_defaults(func=call)

    sub = cli_shared.add_command_subparser(subparsers, "contract", "upgrade",
                                           f"Upgrade a previously-deployed Smart Contract.{output_description}")
    _add_contract_arg(sub)
    cli_shared.add_outfile_arg(sub)
    _add_project_or_bytecode_arg(sub)
    _add_metadata_arg(sub)
    cli_shared.add_wallet_args(args, sub)
    cli_shared.add_proxy_arg(sub)
    cli_shared.add_tx_args(args, sub, with_receiver=False, with_data=False)
    _add_arguments_arg(sub)
    sub.add_argument("--wait-result", action="store_true", default=False,
                     help="signal to wait for the transaction result - only valid if --send is set")
    sub.add_argument("--timeout", default=100, help="max num of seconds to wait for result"
                                                    " - only valid if --wait-result is set")
    cli_shared.add_broadcast_args(sub)

    sub.set_defaults(func=upgrade)

    sub = cli_shared.add_command_subparser(subparsers, "contract", "query",
                                           "Query a Smart Contract (call a pure function)")
    _add_contract_arg(sub)
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

    group = sub.add_mutually_exclusive_group(required=True)
    group.add_argument(
        "--project",
        default=os.getcwd(),
        help="🗀 the project directory (default: current directory)",
    )
    group.add_argument(
        "--packaged-src", help="JSON file containing the source code of the contract"
    )

    _add_contract_arg(sub)
    sub.add_argument(
        "--verifier-url",
        required=True,
        help="the url of the service that validates the contract",
    )
    sub.add_argument("--docker-image", required=True, help="the docker image used for the build (i.e. elrondnetwork/build-contract-rust:v4.0.0)")
    cli_shared.add_wallet_args(args, sub)
    sub.set_defaults(func=verify)

    sub = cli_shared.add_command_subparser(subparsers, "contract", "reproducible-build",
                                            "Build a Smart Contract and get the same output as a previously built Smart Contract")
    _add_project_arg(sub)
    _add_build_options_args(sub)
    sub.add_argument("--docker-image", required=True, type=str,
                        help="the docker image tag used to build the contract")
    sub.add_argument("--contract", type=str, help="relative path of the contract in the project")
    sub.set_defaults(func=do_reproducible_build)

    parser.epilog = cli_shared.build_group_epilog(subparsers)
    return subparsers


def _add_project_arg(sub: Any):
    sub.add_argument("project", nargs='?', default=os.getcwd(),
                     help="🗀 the project directory (default: current directory)")


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

    sub.add_argument("--eei-checks", action="store_true", default=False, help="run EEI compatibility checks (default: %(default)s)")
    # Flags are kept in order to avoid breaking changes, for the moment - we might completely remove them in the future.
    sub.add_argument("--skip-eei-checks", action="store_true", default=True, help="deprecated flag")
    sub.add_argument("--ignore-eei-checks", action="store_true", default=True, help="deprecated flag")


def _add_recursive_arg(sub: Any):
    sub.add_argument("-r", "--recursive", dest="recursive", action="store_true", help="locate projects recursively")


def _add_project_or_bytecode_arg(sub: Any):
    group = sub.add_mutually_exclusive_group(required=True)
    group.add_argument("--project", default=os.getcwd(),
                       help="🗀 the project directory (default: current directory)")
    group.add_argument("--bytecode", type=str,
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
    projects.list_project_templates()


def create(args: Any):
    name = args.name
    template = args.template
    directory = Path(args.directory)

    projects.create_from_template(name, template, directory)


def get_project_paths(args: Any) -> List[Path]:
    base_path = Path(args.project)
    recursive = bool(args.recursive)
    if recursive:
        return get_project_paths_recursively(base_path)
    return [base_path]


def clean(args: Any):
    project_paths = get_project_paths(args)
    for project in project_paths:
        projects.clean_project(project)


def build(args: Any):
    project_paths = get_project_paths(args)
    options: Dict[str, Any] = _prepare_build_options(args)

    for project in project_paths:
        projects.build_project(project, options)


def _prepare_build_options(args: Any) -> Dict[str, Any]:
    return {
        "debug": args.debug,
        "optimized": not args.no_optimization,
        "no-wasm-opt": args.no_wasm_opt,
        "verbose": args.verbose,
        "cargo-target-dir": args.cargo_target_dir,
        "wasm-symbols": args.wasm_symbols,
        "wasm-name": args.wasm_name,
        "wasm-suffix": args.wasm_suffix,
        "eei-checks": args.eei_checks,
        # TODO: Remove this, in the future
        "skip-eei-checks": args.skip_eei_checks,
        # TODO: Remove this, in the future
        "ignore-eei-checks": args.ignore_eei_checks
    }


def do_report(args: Any):
    build_options: Dict[str, Any] = _prepare_build_options(args)
    projects.do_report(args, build_options)


def run_tests(args: Any):
    projects.run_tests(args)


def deploy(args: Any):
    logger.debug("deploy")
    cli_shared.check_broadcast_args(args)

    arguments = args.arguments
    gas_price = args.gas_price
    gas_limit = args.gas_limit
    value = args.value
    chain = args.chain
    version = args.version

    contract = _prepare_contract(args)
    sender = _prepare_sender(args)

    tx = contract.deploy(sender, arguments, gas_price, gas_limit, value, chain, version)
    logger.info("Contract address: %s", contract.address)
    utils.log_explorer_contract_address(chain, contract.address)

    _send_or_simulate(tx, contract, args)


def _prepare_contract(args: Any) -> SmartContract:
    if args.bytecode and len(args.bytecode):
        bytecode = utils.read_binary_file(Path(args.bytecode)).hex()
    else:
        project_path = Path(args.project)
        project = load_project(project_path)
        bytecode = project.get_bytecode()

    metadata = CodeMetadata(upgradeable=args.metadata_upgradeable, readable=args.metadata_readable,
                            payable=args.metadata_payable, payable_by_sc=args.metadata_payable_by_sc)
    contract = SmartContract(bytecode=bytecode, metadata=metadata)
    return contract


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
        sender.sync_nonce(ElrondProxy(args.proxy))

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


def call(args: Any):
    logger.debug("call")
    cli_shared.check_broadcast_args(args)

    contract_address = args.contract
    function = args.function
    arguments = args.arguments
    gas_price = args.gas_price
    gas_limit = args.gas_limit
    value = args.value
    chain = args.chain
    version = args.version

    contract = SmartContract(contract_address)
    sender = _prepare_sender(args)

    tx = contract.execute(sender, function, arguments, gas_price, gas_limit, value, chain, version)
    _send_or_simulate(tx, contract, args)


def upgrade(args: Any):
    logger.debug("upgrade")
    cli_shared.check_broadcast_args(args)

    contract_address = args.contract
    arguments = args.arguments
    gas_price = args.gas_price
    gas_limit = args.gas_limit
    value = args.value
    chain = args.chain
    version = args.version

    contract = _prepare_contract(args)
    contract.address = Address(contract_address)
    sender = _prepare_sender(args)

    tx = contract.upgrade(sender, arguments, gas_price, gas_limit, value, chain, version)
    _send_or_simulate(tx, contract, args)


def query(args: Any):
    logger.debug("query")

    contract_address = args.contract
    function = args.function
    arguments = args.arguments

    contract = SmartContract(contract_address)
    result = contract.query(ElrondProxy(args.proxy), function, arguments)
    utils.dump_out_json(result)


def _send_or_simulate(tx: Transaction, contract: SmartContract, args: Any):
    output_builder = cli_shared.send_or_simulate(tx, args, dump_output=False)
    output_builder.set_contract_address(contract.address)
    utils.dump_out_json(output_builder.build(), outfile=args.outfile)


def verify(args: Any) -> None:
    contract = Address(args.contract)
    verifier_url = args.verifier_url

    packaged_src = Path(args.packaged_src)
    project_directory = Path(args.project)

    owner = _prepare_signer(args)
    docker_image = args.docker_image

    response = trigger_contract_verification(
        packaged_src, project_directory, owner, contract, verifier_url, docker_image
    )
    utils.dump_out_json(response.json())


def do_reproducible_build(args: Any):
    project_path = args.project
    docker_image = args.docker_image
    contract_path = args.contract
    output_path = Path(project_path) / "output-docker"
    utils.ensure_folder(output_path)

    options = _prepare_build_options(args)
    no_wasm_opt = options.get("no-wasm-opt", True)

    if is_docker_installed():
        logger.info("Starting the docker run...")
        return_code = run_docker(docker_image, project_path, contract_path, output_path, no_wasm_opt)
        logger.info("Docker build ran successfully!")
        logger.info("You can deploy you Smart Contract, then verify it using the erdpy contract verify command")
    else:
        raise DockerMissingError()

    return return_code
