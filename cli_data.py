import logging
import os
from pathlib import Path
from typing import Any, Dict

from erdpy import cli_shared, errors, utils

logger = logging.getLogger("cli.data")

DATA_PATH = os.path.expanduser("~/elrondsdk/erdpy.data-storage.json")


def setup_parser(subparsers: Any) -> Any:
    parser = cli_shared.add_group_subparser(subparsers, "data", "Data manipulation omnitool")
    subparsers = parser.add_subparsers()

    sub = cli_shared.add_command_subparser(subparsers, "data", "parse", "Parses values from a given file")
    sub.add_argument("--file", required=True, help="path of the file to parse")
    sub.add_argument("--expression", required=True, help="the Python-Dictionary expression to evaluate in order to extract the data")
    sub.set_defaults(func=parse)

    sub = cli_shared.add_command_subparser(subparsers, "data", "store", "Stores a key-value pair within a partition")
    sub.add_argument("--key", required=True, help="the key")
    sub.add_argument("--value", required=True, help="the value to save")
    sub.add_argument("--partition", default="global", help="the storage partition (default: %(default)s)")
    sub.set_defaults(func=store)

    sub = cli_shared.add_command_subparser(subparsers, "data", "load", "Loads a key-value pair from a storage partition")
    sub.add_argument("--key", required=True, help="the key")
    sub.add_argument("--partition", default="global", help="the storage partition (default: %(default)s)")
    sub.set_defaults(func=load)

    parser.epilog = cli_shared.build_group_epilog(subparsers)
    return subparsers


def parse(args: Any):
    logger.warning("Always review --expression parameters before executing this command!")

    file: str = Path(args.file).expanduser()
    expression: str = args.expression
    suffix = file.suffix
    data = None

    if suffix == ".json":
        data = utils.read_json_file(file)
    else:
        raise errors.BadUsage(f"File isn't parsable: {file}")

    result = eval(expression, {
        "data": data
    })

    print(result)


def store(args: Any):
    logger.warning("Never use this command to store sensitive information! Data is unencrypted.")

    key = args.key
    value = args.value
    partition = args.partition

    data = _read_file()
    if partition not in data:
        data[partition] = dict()

    data_in_partition = data[partition]
    data_in_partition[key] = value
    _write_file(data)

    logger.info(f"Data has been stored at key = '{key}', in partition = '{partition}'.")


def load(args: Any):
    key = args.key
    partition = args.partition

    data = _read_file()
    data_in_partition = data.get(partition, dict())
    value = data_in_partition.get(key, "")
    print(value)


def _read_file() -> Dict[str, Any]:
    if not os.path.isfile(DATA_PATH):
        return dict()
    return utils.read_json_file(DATA_PATH)


def _write_file(data: Dict[str, Any]):
    utils.write_json_file(DATA_PATH, data)
