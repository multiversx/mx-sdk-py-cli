from enum import Enum, auto

from multiversx_sdk_cli.projects.report.format.format_options import FormatOptions


class ChangeType(Enum):
    UNKNOWN = auto()
    NONE = auto()
    GOOD = auto()
    BAD = auto()
    MIXED = auto()

    def to_markdown(self, format_options: FormatOptions) -> str:
        if format_options.github_flavor:
            return self._to_github_markdown()
        else:
            return self._to_text_markdown()

    def _to_github_markdown(self) -> str:
        switch = {
            ChangeType.UNKNOWN: ":warning:",
            ChangeType.NONE: "",
            ChangeType.GOOD: ":green_circle:",
            ChangeType.BAD: ":red_circle:",
            ChangeType.MIXED: ":yellow_circle:",
        }
        return switch[self]

    def _to_text_markdown(self) -> str:
        switch = {
            ChangeType.UNKNOWN: "\u26a0\ufe0f ",
            ChangeType.NONE: "",
            ChangeType.GOOD: "\U0001f34f",
            ChangeType.BAD: "\u274c",
            ChangeType.MIXED: "\U0001f536\ufe0f",
        }
        return switch[self]
