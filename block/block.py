import json
from typing import Any

from erdpy.proxy import ElrondProxy


# UPDATE WHEN PROXY WILL HAVE API ROUTES FOR BLOCK (use also shard ID)
def get_block(args: Any) -> Any:
    if args.nonce:
        return _get_block_by_nonce(args)
    else:
        return _get_block_by_hash(args)


def _get_block_by_nonce(args: Any) -> Any:
    proxy_url = args.proxy
    proxy = ElrondProxy(proxy_url)
    block = proxy.get_block_by_nonce(args.nonce, args.with_txs)
    print(json.dumps(block, indent=2, sort_keys=True))


def _get_block_by_hash(args: Any) -> Any:
    proxy_url = args.proxy
    proxy = ElrondProxy(proxy_url)
    block = proxy.get_block_by_hash(args.hash, args.with_txs)
    print(json.dumps(block, indent=2, sort_keys=False))
