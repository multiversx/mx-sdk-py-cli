from erdpy.dispatcher.transactions.queue import TransactionQueue
import logging
from typing import Any

from erdpy import cli_shared

logger = logging.getLogger("cli.dispatcher")


def setup_parser(subparsers: Any) -> Any:
    parser = cli_shared.add_group_subparser(subparsers, "dispatcher", "Enqueue transactions, then bulk dispatch them")
    subparsers = parser.add_subparsers()

    sub = cli_shared.add_command_subparser(subparsers, "dispatcher", "enqueue", "Enqueue a transaction")
    cli_shared.add_tx_args(sub, with_nonce=False)
    sub.set_defaults(func=enqueue_transaction)

    sub = cli_shared.add_command_subparser(subparsers, "dispatcher", "dispatch", "Dispatch queued transactions")
    cli_shared.add_proxy_arg(sub)
    cli_shared.add_wallet_args(sub)
    sub.set_defaults(func=dispatch_transactions)

    sub = cli_shared.add_command_subparser(subparsers, "dispatcher", "dispatch-continuously", "Continuously dispatch queued transactions")
    cli_shared.add_proxy_arg(sub)
    cli_shared.add_wallet_args(sub)
    sub.add_argument("--interval", required=True, help="the interval to retrieve transactions from the queue, in seconds")
    sub.set_defaults(func=dispatch_transactions_continuously)

    sub = cli_shared.add_command_subparser(subparsers, "dispatcher", "clean", "Clear queue of transactions")
    sub.set_defaults(func=clean_transactions_queue)

    parser.epilog = cli_shared.build_group_epilog(subparsers)
    return subparsers


def enqueue_transaction(args: Any):
    queue = TransactionQueue()
    queue.enqueue_transaction(args)


def dispatch_transactions(args: Any):
    queue = TransactionQueue()
    queue.dispatch_transactions(args)


def dispatch_transactions_continuously(args: Any):
    queue = TransactionQueue()
    queue.dispatch_transactions_continuously(args)


def clean_transactions_queue():
    queue = TransactionQueue()
    queue.clean_transactions_queue()
