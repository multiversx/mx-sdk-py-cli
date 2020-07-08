import logging

from erdpy import facade

logger = logging.getLogger("cli.network")


def setup_parser(subparsers):
    parser = subparsers.add_parser("network")
    subparsers = parser.add_subparsers()

    sub = subparsers.add_parser("num-shards")
    sub.add_argument("--proxy", required=True)
    sub.set_defaults(func=get_num_shards)

    sub = subparsers.add_parser("block-nonce")
    sub.add_argument("--proxy", required=True)
    sub.add_argument("--shard", required=True)
    sub.set_defaults(func=get_last_block_nonce)

    sub = subparsers.add_parser("chain")
    sub.add_argument("--proxy", required=True)
    sub.set_defaults(func=get_chain_id)

    sub = subparsers.add_parser("meta-block")
    sub.add_argument("--proxy", required=True)
    sub.add_argument("--nonce", required=True, type=int)
    sub.set_defaults(func=get_meta_block)


def get_num_shards(args):
    facade.get_num_shards(args)


def get_last_block_nonce(args):
    facade.get_last_block_nonce(args)


def get_chain_id(args):
    facade.get_chain_id(args)


def get_meta_block(args):
    facade.get_meta_block(args)
