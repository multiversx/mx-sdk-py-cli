import logging
from typing import Any

from erdpy import facade

logger = logging.getLogger("cli.blockatlas")


def setup_parser(subparsers: Any) -> Any:
    parser = subparsers.add_parser("blockatlas", description="Interact with an Block Atlas instance")
    subparsers = parser.add_subparsers()

    parser.add_argument("--url", required=True)
    parser.add_argument("--coin", required=True)

    sub = subparsers.add_parser("current-block-number")
    sub.set_defaults(func=facade.blockatlas_get_current_block_number)

    sub = subparsers.add_parser("block-by-number")
    sub.add_argument("--number", required=True)
    sub.set_defaults(func=facade.blockatlas_get_block_by_number)

    sub = subparsers.add_parser("transactions")
    sub.add_argument("--address", required=True)
    sub.set_defaults(func=facade.blockatlas_get_txs_by_address)

    return subparsers
