import logging
from typing import Any, Dict

from multiversx_sdk_cli.errors import UnknownConfigurationError

logger = logging.getLogger("localnet")


class ConfigPart:
    def __init__(self):
        pass

    def get_name(self) -> str:
        raise NotImplementedError()

    def override(self, other: Dict[str, Any]):
        self._validate_overriding_entries(other)
        self._do_override(other)

    def _validate_overriding_entries(self, overriding: Dict[str, Any]) -> None:
        allowed_entries = set(self.__dict__.keys())
        overriding_entries = set(overriding.keys())
        unknown_entries = overriding_entries - allowed_entries

        if unknown_entries:
            logger.error(
                f"""\
Unknown localnet configuration entries: {unknown_entries}.
Please check the configuration of the localnet.
For "{self.get_name()}", the allowed entries are: {allowed_entries}."""
            )
            raise UnknownConfigurationError(f"Unknown localnet configuration entries: {unknown_entries}")

    def _do_override(self, other: Dict[str, Any]) -> None:
        raise NotImplementedError()

    def to_dictionary(self) -> Dict[str, Any]:
        return self.__dict__
