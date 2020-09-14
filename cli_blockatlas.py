from erdpy import utils
from erdpy.blockatlas.core import BlockAtlas
from erdpy import cli_shared
import logging
from typing import Any


logger = logging.getLogger("cli.blockatlas")


def setup_parser(subparsers: Any) -> Any:
    parser = cli_shared.add_group_subparser(subparsers, "blockatlas", "Interact with an Block Atlas instance")
    subparsers = parser.add_subparsers()

    parser.add_argument("--url", required=True, help="🖧 URL of Block Atlas instance")
    parser.add_argument("--coin", required=True, help="coin identifier (e.g. erd, bnb)")

    sub = cli_shared.add_command_subparser(subparsers, "blockatlas", "current-block-number", "Get latest notarized metablock (number / nonce)")
    sub.set_defaults(func=blockatlas_get_current_block_number)

    sub = cli_shared.add_command_subparser(subparsers, "blockatlas", "block-by-number", "Get block by number (nonce)")
    sub.add_argument("--number", required=True, help="the number (nonce)")
    sub.set_defaults(func=blockatlas_get_block_by_number)

    sub = cli_shared.add_command_subparser(subparsers, "blockatlas", "transactions", "Get transactions by address")
    sub.add_argument("--address", required=True, help="🖄 the address to query")
    cli_shared.add_outfile_arg(sub)
    sub.set_defaults(func=blockatlas_get_txs_by_address)

    parser.epilog = cli_shared.build_group_epilog(subparsers)
    return subparsers


def blockatlas_get_current_block_number(args: Any) -> Any:
    client = BlockAtlas(args.url, args.coin)
    number = client.get_current_block_number()
    print(number)
    return number


def blockatlas_get_block_by_number(args: Any) -> Any:
    client = BlockAtlas(args.url, args.coin)
    block = client.get_block_by_number(args.number)
    print(block)
    return block


def blockatlas_get_txs_by_address(args: Any) -> Any:
    client = BlockAtlas(args.url, args.coin)
    transactions = client.get_txs_by_address(args.address)
    utils.dump_out_json(transactions, args.outfile)
    return transactions
