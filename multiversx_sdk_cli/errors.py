from typing import Any, Union


class KnownError(Exception):
    inner = None

    def __init__(self, message: str, inner: Union[Any, None] = None):
        super().__init__(message)
        self.inner = inner

    def get_pretty(self) -> str:
        if self.inner:
            return f"""{self}
... {self.inner}
"""
        return str(self)


class ProgrammingError(KnownError):
    pass


class DownloadError(KnownError):
    pass


class BadUrlError(DownloadError):
    pass


class UnknownArchiveType(KnownError):
    pass


class DependencyMissing(KnownError):
    def __init__(self, name: str, tag: str):
        super().__init__(f"Dependency missing: {name} {tag}")


class DependenciesMissing(KnownError):
    def __init__(self, dependencies: list[tuple[str, str]]):
        message = "Dependencies missing: \n"

        for dependency in dependencies:
            message += f"{dependency[0]} {dependency[1]}\n"

        super().__init__(message.rstrip("\n"))


class UnknownDependency(KnownError):
    def __init__(self, name: str):
        super().__init__(f"Unknown dependency: {name}")


class BadDependencyResolution(ProgrammingError):
    def __init__(self, dependency: str, resolution: Any):
        super().__init__(f"Bad dependency resolution for {dependency}: {resolution}")


class BadDirectory(KnownError):
    def __init__(self, directory: str):
        super().__init__(f"Bad directory: {directory}")


class PlatformNotSupported(KnownError):
    def __init__(self, action_or_item: str, platform: str):
        super().__init__(f"[{action_or_item}] is not supported on platform [{platform}].")


class BadInputError(KnownError):
    def __init__(self, input: str, message: str):
        super().__init__(f"Bad input [{input}]: {message}")


class ExternalProcessError(KnownError):
    def __init__(self, command_line: str, message: str):
        super().__init__(
            f"""External process error:
Command line: {command_line}
Output: {message}"""
        )


class UnknownConfigurationError(KnownError):
    def __init__(self, name: str):
        super().__init__(f"Configuration entry is not known: {name}.")


class ConfigurationShouldBeUniqueError(KnownError):
    def __init__(self, name: str):
        super().__init__(f"Configuration entry already exists: {name}.")


class ConfigurationProtectedError(KnownError):
    def __init__(self, name: str):
        super().__init__(f"This configuration name is protected: {name}.")


class BadUserInput(KnownError):
    def __init__(self, message: str):
        super().__init__(f"Bad user input: {message}.")


class BadUsage(KnownError):
    def __init__(self, message: str):
        super().__init__(f"Bad usage: {message}.")


class TransactionIsNotSigned(KnownError):
    def __init__(self):
        super().__init__("Transaction is not signed.")


class NoWalletProvided(KnownError):
    def __init__(self):
        super().__init__("No wallet provided.")


class DockerMissingError(KnownError):
    def __init__(self):
        super().__init__("Docker is not installed! Please visit https://docs.docker.com/get-docker/ to install docker.")


class GuardianServiceError(KnownError):
    def __init__(self, message: str):
        super().__init__(message)


class ArgumentsNotProvidedError(KnownError):
    def __init__(self, message: str):
        super().__init__(message)


class WalletGenerationError(KnownError):
    def __init__(self, message: str):
        super().__init__(message)


class QueryContractError(KnownError):
    def __init__(self, message: str, inner: Any = None):
        super().__init__(message, str(inner))


class IncorrectWalletError(KnownError):
    def __init__(self, message: str):
        super().__init__(message)


class InvalidArgumentsError(KnownError):
    def __init__(self, message: str):
        super().__init__(message)


class LedgerError(KnownError):
    def __init__(self, message: str):
        super().__init__(message)


class TransactionSigningError(KnownError):
    def __init__(self, message: str):
        super().__init__(message)


class InvalidConfirmationSettingError(KnownError):
    def __init__(self, value: str):
        super().__init__(
            f"Invalid confirmation setting: {value}. Valid values are: ['true', 'false', 'yes', 'no', '1', '0']."
        )


class InvalidEnvironmentValue(KnownError):
    def __init__(self, message: str):
        super().__init__(message)


class EnvironmentProtectedError(KnownError):
    def __init__(self, name: str):
        super().__init__(f"This environment name is protected: {name}.")


class UnknownEnvironmentError(KnownError):
    def __init__(self, name: str):
        super().__init__(f"Environment entry is not known: {name}.")


class EnvironmentAlreadyExistsError(KnownError):
    def __init__(self, name: str):
        super().__init__(f"Environment entry already exists: {name}.")


class UnknownAddressAliasError(KnownError):
    def __init__(self, name: str):
        super().__init__(f"Alias is not known: {name}.")


class AliasAlreadyExistsError(KnownError):
    def __init__(self, name: str):
        super().__init__(f"Alias already exists: {name}.")


class AliasProtectedError(KnownError):
    def __init__(self, name: str):
        super().__init__(f"This environment name is protected: {name}.")


class InvalidAddressConfigValue(KnownError):
    def __init__(self, message: str):
        super().__init__(message)


class AddressConfigFileError(KnownError):
    def __init__(self, message: str):
        super().__init__(message)


class LogLevelError(KnownError):
    def __init__(self, log_level: str):
        super().__init__(f"Log level not accepted: {log_level}. Choose between ['debug', 'info', 'warning', 'error'].")
