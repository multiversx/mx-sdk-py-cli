from typing import Any

import pytest

from multiversx_sdk_cli.cli_shared import prepare_chain_id_in_args
from multiversx_sdk_cli.errors import ArgumentsNotProvidedError


class Args:
    pass


def test_prepare_chain_id_in_args() -> None:
    args: Any = Args()
    args.chain = None
    args.proxy = None

    with pytest.raises(ArgumentsNotProvidedError):
        prepare_chain_id_in_args(args)

    args.chain = "I"
    args.proxy = "https://testnet-api.multiversx.com"

    prepare_chain_id_in_args(args)
    assert args.chain == "T"

    args.chain = None
    prepare_chain_id_in_args(args)
    assert args.chain == "T"

    args.chain = "T"
    args.proxy = None
    prepare_chain_id_in_args(args)
    assert args.chain == "T"
