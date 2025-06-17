from typing import Any

from multiversx_sdk_cli.errors import InvalidArgumentsError


def validate_transaction_args(args: Any):
    validate_nonce_args(args)
    validate_receiver_args(args)
    validate_gas_limit_args(args)


def validate_nonce_args(args: Any):
    """If nonce is not provided, ensure that proxy is provided."""
    if hasattr(args, "nonce") and args.nonce is None:

        if hasattr(args, "proxy") and not args.proxy:
            raise InvalidArgumentsError("--proxy must be provided if --nonce is not provided")


def validate_receiver_args(args: Any):
    """Ensure that receiver is provided."""
    if hasattr(args, "receiver") and not args.receiver:
        raise InvalidArgumentsError("--receiver must be provided")


def validate_gas_limit_args(args: Any):
    """Ensure that gas_limit is provided."""
    if hasattr(args, "gas_limit") and not args.gas_limit:
        raise InvalidArgumentsError("--gas-limit must be provided")


def ensure_relayer_wallet_args_are_provided(args: Any):
    signing_methods = [args.relayer_pem, args.relayer_keyfile, args.relayer_ledger]

    if all(signing_methods):
        raise InvalidArgumentsError(
            "Only one of --relayer-pem, --relayer-keyfile, or --relayer-ledger must be provided"
        )

    if not any(signing_methods):
        raise InvalidArgumentsError("One of --relayer-pem, --relayer-keyfile, or --relayer-ledger must be provided")


def validate_broadcast_args(args: Any):
    if args.send and args.simulate:
        raise InvalidArgumentsError("Cannot both 'simulate' and 'send' a transaction")

    if args.send or args.simulate:
        validate_proxy_argument(args)


def validate_chain_id_args(args: Any):
    if not args.chain and not args.proxy:
        raise InvalidArgumentsError("Either --chain or --proxy must be provided")


def validate_proxy_argument(args: Any):
    if not args.proxy:
        raise InvalidArgumentsError("--proxy must be provided")
