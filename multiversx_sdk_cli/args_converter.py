import logging
from typing import Any

from multiversx_sdk import Address
from multiversx_sdk.abi import (
    AddressValue,
    BigUIntValue,
    BoolValue,
    BytesValue,
    StringValue,
)

from multiversx_sdk_cli.config_env import get_address_hrp
from multiversx_sdk_cli.constants import (
    ADDRESS_PREFIX,
    FALSE_STR_LOWER,
    HEX_PREFIX,
    MAINCHAIN_ADDRESS_HRP,
    STR_PREFIX,
    TRUE_STR_LOWER,
)
from multiversx_sdk_cli.errors import BadUserInput

logger = logging.getLogger("args_converter")


def convert_args_to_typed_values(arguments: list[str]) -> list[Any]:
    args: list[Any] = []

    for arg in arguments:
        if arg.startswith(HEX_PREFIX):
            args.append(BytesValue(_hex_to_bytes(arg)))
        elif arg.isnumeric():
            args.append(BigUIntValue(int(arg)))
        elif arg.startswith(ADDRESS_PREFIX):
            args.append(AddressValue.new_from_address(Address.new_from_bech32(arg[len(ADDRESS_PREFIX) :])))
        elif arg.startswith(MAINCHAIN_ADDRESS_HRP):
            # this flow will be removed in the future
            logger.warning(
                "Address argument has no prefix. This flow will be removed in the future. Please provide each address using the `addr:` prefix. (e.g. --arguments addr:erd1...)"
            )
            args.append(AddressValue.new_from_address(Address.new_from_bech32(arg)))
        elif arg.startswith(get_address_hrp()):
            args.append(AddressValue.new_from_address(Address.new_from_bech32(arg)))
        elif arg.lower() == FALSE_STR_LOWER:
            args.append(BoolValue(False))
        elif arg.lower() == TRUE_STR_LOWER:
            args.append(BoolValue(True))
        elif arg.startswith(STR_PREFIX):
            args.append(StringValue(arg[len(STR_PREFIX) :]))
        else:
            raise BadUserInput(
                f"Unknown argument type for argument: `{arg}`. Use `mxpy contract <sub-command> --help` to check all supported arguments"
            )

    return args


def _hex_to_bytes(arg: str):
    argument = arg[len(HEX_PREFIX) :]
    argument = argument.upper()
    argument = _ensure_even_length(argument)
    return bytes.fromhex(argument)


def _ensure_even_length(string: str) -> str:
    if len(string) % 2 == 1:
        return "0" + string
    return string
