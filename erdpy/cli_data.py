import logging
import os
from pathlib import Path
from typing import Any, Dict

from erdpy import cli_shared, errors, utils, workstation

logger = logging.getLogger("cli.data")

DATA_FILENAME = "erdpy.data-storage.json"


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
    sub.add_argument("--partition", default="*", help="the storage partition (default: %(default)s)")
    sub.add_argument("--use-global", action="store_true", default=False, help="use the global storage (default: %(default)s)")
    sub.set_defaults(func=store)

    sub = cli_shared.add_command_subparser(subparsers, "data", "load", "Loads a key-value pair from a storage partition")
    sub.add_argument("--key", required=True, help="the key")
    sub.add_argument("--partition", default="*", help="the storage partition (default: %(default)s)")
    sub.add_argument("--use-global", action="store_true", default=False, help="use the global storage (default: %(default)s)")
    sub.set_defaults(func=load)

    parser.epilog = cli_shared.build_group_epilog(subparsers)
    return subparsers


def parse(args: Any):
    logger.warning("Always review --expression parameters before executing this command!")

    file = Path(args.file).expanduser()
    expression: str = args.expression
    suffix = file.suffix
    data = None

    if suffix == ".json":
        data = utils.read_json_file(str(file))
    else:
        raise errors.BadUsage(f"File isn't parsable: {file}")

    try:
        result = eval(expression, {
            "data": data
        })
    except KeyError:
        result = ""

    print(result)


def store(args: Any):
    logger.warning("Never use this command to store sensitive information! Data is unencrypted.")

    key = args.key
    value = args.value
    partition = args.partition
    use_global = args.use_global

    data = _read_file(use_global)
    if partition not in data:
        data[partition] = dict()

    data_in_partition = data[partition]
    data_in_partition[key] = value
    _write_file(use_global, data)

    logger.info(f"Data has been stored at key = '{key}', in partition = '{partition}'.")


def load(args: Any):
    key = args.key
    partition = args.partition
    use_global = args.use_global

    data = _read_file(use_global)
    data_in_partition = data.get(partition, dict())
    value = data_in_partition.get(key, "")
    print(value)


def _read_file(use_global: bool) -> Dict[str, Any]:
    filename = _get_filename(use_global)

    if not os.path.isfile(filename):
        return dict()
    return utils.read_json_file(filename)


def _write_file(use_global: bool, data: Dict[str, Any]):
    filename = _get_filename(use_global)

    utils.write_json_file(filename, data)


def _get_filename(use_global: bool):
    if use_global:
        return workstation.get_tools_folder() / DATA_FILENAME
    return Path(os.getcwd()) / DATA_FILENAME
