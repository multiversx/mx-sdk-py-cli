from erdpy import cli_shared
import logging
from typing import Any

from erdpy import facade

logger = logging.getLogger("cli.blockatlas")


def setup_parser(subparsers: Any) -> Any:
    parser = cli_shared.add_group_subparser(subparsers, "blockatlas", "Interact with an Block Atlas instance")
    subparsers = parser.add_subparsers()

    parser.add_argument("--url", required=True, help="🖧 URL of Block Atlas instance")
    parser.add_argument("--coin", required=True, help="coin identifier (e.g. erd, bnb)")

    sub = cli_shared.add_command_subparser(subparsers, "blockatlas", "current-block-number", "Get latest notarized metablock (number / nonce)")
    sub.set_defaults(func=facade.blockatlas_get_current_block_number)

    sub = cli_shared.add_command_subparser(subparsers, "blockatlas", "block-by-number", "Get block by number (nonce)")
    sub.add_argument("--number", required=True, help="the number (nonce)")
    sub.set_defaults(func=facade.blockatlas_get_block_by_number)

    sub = cli_shared.add_command_subparser(subparsers, "blockatlas", "transactions", "Get transactions by address")
    sub.add_argument("--address", required=True, help="🖄 the address to query")
    cli_shared.add_outfile_arg(sub)
    sub.set_defaults(func=facade.blockatlas_get_txs_by_address)

    parser.epilog = cli_shared.build_group_epilog(subparsers)
    return subparsers
