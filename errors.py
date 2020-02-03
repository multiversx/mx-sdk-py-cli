
class KnownError(Exception):
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
