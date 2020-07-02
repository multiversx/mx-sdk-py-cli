
class KnownError(Exception):
    inner = None

    def __init__(self, message, inner=None):
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


class TemplateMissingError(KnownError):
    def __init__(self, template):
        super().__init__(f"Template missing: {template}")


class DownloadError(KnownError):
    pass


class BadUrlError(DownloadError):
    def __init__(self):
        pass


class BadDirectory(KnownError):
    def __init__(self, directory):
        super().__init__(f"Bad directory: {directory}")


class NotSupportedProject(KnownError):
    def __init__(self, directory):
        super().__init__(f"Directory is not a supported project: {directory}")


class PlatformNotSupported(KnownError):
    def __init__(self, action_or_item, platform):
        super().__init__(f"[{action_or_item}] is not supported on platform [{platform}].")


class BuildError(KnownError):
    def __init__(self, message, inner=None):
        super().__init__(f"Build error: {message}.", inner)


class BadSink(ProgrammingError):
    def __init__(self, name):
        super().__init__(f"Bad sink:\n {name}.")


class UnknownArgumentFormat(KnownError):
    def __init__(self, argument):
        super().__init__(f"Cannot handle non-hex, non-number arguments yet: {argument}.")


class ProxyRequestError(KnownError):
    def __init__(self, url, data):
        super().__init__(f"Proxy request error for url [{url}]: {data}")


class BlockAtlasRequestError(KnownError):
    def __init__(self, url, data):
        super().__init__(f"Block Atlas request error for url [{url}]: {data}")


class BadInputError(KnownError):
    def __init__(self, input, message):
        super().__init__(f"Bad input [{input}]: {message}")


class BadAddressFormatError(KnownError):
    def __init__(self, value):
        super().__init__(f"Bad address [{value}].")


class EmptyAddressError(KnownError):
    def __init__(self):
        super().__init__(f"Address is empty.")


class ExternalProcessError(KnownError):
    def __init__(self, command_line, message):
        super().__init__(f"""External process error:
Command line: {command_line}
Output: {message}""")
