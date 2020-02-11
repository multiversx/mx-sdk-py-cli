
class KnownError(Exception):
    pass


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


class PlatformNotSupported(KnownError):
    def __init__(self, action_or_item, platform):
        super().__init__(
            f"[{action_or_item}] is not supported on platform [{platform}].")


class BuildError(KnownError):
    def __init__(self, message):
        super().__init__(f"Build error:\n {message}.")


class BadSink(ProgrammingError):
    def __init__(self, name):
        super().__init__(f"Bad sink:\n {name}.")


class UnknownArgumentFormat(KnownError):
    def __init__(self, argument):
        super().__init__(
            f"Cannot handle non-hex, non-number arguments yet: {argument}.")
