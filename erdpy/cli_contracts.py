import logging
import os
from typing import Any, List, Union

from pathlib import Path

from erdpy import cli_shared, errors, projects, utils
from erdpy.accounts import Account, Address, LedgerAccount
from erdpy.contracts import CodeMetadata, SmartContract
from erdpy.projects import load_project
from erdpy.projects.core import get_project_paths_recursively
from erdpy.proxy.core import ElrondProxy
from erdpy.transactions import Transaction

logger = logging.getLogger("cli.contracts")


def setup_parser(args: List[str], subparsers: Any) -> Any:
    parser = cli_shared.add_group_subparser(subparsers, "contract", "Build, deploy and interact with Smart Contracts")
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

    sub = cli_shared.add_command_subparser(subparsers, "contract", "report", "Print a detailed report the smart contracts.")
    _add_project_arg(sub)
    _add_flag(sub, "--skip-build", help="skips the step of building of the wasm contracts")
    _add_flag(sub, "--skip-twiggy", help="skips the steps of building the debug wasm files and running twiggy")
    sub.add_argument("--output-format", type=str, default="markdown", choices=["markdown", "json"], help="report output format (default: %(default)s)")
    sub.set_defaults(func=projects.report_cli)

    sub = cli_shared.add_command_subparser(subparsers, "contract", "deploy", "Deploy a Smart Contract.")
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
                                           "Interact with a Smart Contract (execute function).")
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
                                           "Upgrade a previously-deployed Smart Contract")
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

    parser.epilog = cli_shared.build_group_epilog(subparsers)
    return subparsers


def _add_project_arg(sub: Any):
    sub.add_argument("project", nargs='?', default=os.getcwd(),
                     help="🗀 the project directory (default: current directory)")


def _add_recursive_arg(sub: Any):
    sub.add_argument("-r", "--recursive", dest="recursive", action="store_true", help="locate projects recursively")


def _add_flag(sub: Any, flag: str, help: str):
    sub.add_argument(flag, action="store_true", default=False, help=help)


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
                     help="arguments for the contract transaction, as numbers or hex-encoded. E.g. --arguments 42 0x64 1000 0xabba")


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
    options = {
        "debug": args.debug,
        "optimized": not args.no_optimization,
        "no-wasm-opt": args.no_wasm_opt,
        "verbose": args.verbose,
        "cargo_target_dir": args.cargo_target_dir,
        "wasm_symbols": args.wasm_symbols,
        "wasm_name": args.wasm_name
    }

    for project in project_paths:
        projects.build_project(project, options)


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

    result = None
    try:
        result = _send_or_simulate(tx, args)
    finally:
        txdict = tx.to_dump_dict()
        txdict['address'] = contract.address.bech32()
        dump_tx_and_result(txdict, result, args)


def dump_tx_and_result(tx: Any, result: Any, args: Any):
    dump = dict()
    dump['emitted_tx'] = tx

    try:
        returnCode = ''
        returnMessage = ''
        dump['result'] = result['result']
        for scrHash, scr in dump['result']['scResults'].items():
            if scr['receiver'] == tx['tx']['sender']:
                retCode = scr['data'][1:]
                retCode = bytes.fromhex(retCode).decode('ascii')
                returnCode = retCode
                returnMessage = scr['returnMessage']

        dump['result']['returnCode'] = returnCode
        dump['result']['returnMessage'] = returnMessage
    except TypeError:
        pass

    utils.dump_out_json(dump, outfile=args.outfile)


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
    elif args.keyfile and args.passfile:
        sender = Account(key_file=args.keyfile, pass_file=args.passfile)
    else:
        raise errors.NoWalletProvided()

    sender.nonce = args.nonce
    if args.recall_nonce:
        sender.sync_nonce(ElrondProxy(args.proxy))

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
    try:
        result = _send_or_simulate(tx, args)
    finally:
        txdict = tx.to_dump_dict()
        dump_tx_and_result(txdict, result, args)


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
    try:
        result = _send_or_simulate(tx, args)
    finally:
        txdict = tx.to_dump_dict()
        dump_tx_and_result(txdict, result, args)


def query(args: Any):
    logger.debug("query")

    contract_address = args.contract
    function = args.function
    arguments = args.arguments

    contract = SmartContract(contract_address)
    result = contract.query(ElrondProxy(args.proxy), function, arguments)
    utils.dump_out_json(result)


def _send_or_simulate(tx: Transaction, args: Any):
    send_wait_result = args.wait_result and args.send and not args.simulate
    send_only = args.send and not (args.wait_result or args.simulate)
    simulate = args.simulate and not (send_only or send_wait_result)

    if send_wait_result:
        proxy = ElrondProxy(args.proxy)
        response = tx.send_wait_result(proxy, args.timeout)
        return None
    elif send_only:
        tx.send(ElrondProxy(args.proxy))
        return None
    elif simulate:
        response = tx.simulate(ElrondProxy(args.proxy))
        return response
