from enum import Enum, auto

from erdpy.projects.report.format.format_options import FormatOptions


class ChangeType(Enum):
    UNKNOWN = auto()
    NONE = auto()
    GOOD = auto()
    BAD = auto()
    MIXED = auto()

    def to_markdown(self, format_options: FormatOptions) -> str:
        if format_options.github_flavor:
            return self.to_github_markdown()
        else:
            return self.to_text_markdown()

    def to_github_markdown(self) -> str:
        switch = {
            ChangeType.UNKNOWN: ':warning:',
            ChangeType.NONE: '',
            ChangeType.GOOD: ':green_circle:',
            ChangeType.BAD: ':red_circle:',
            ChangeType.MIXED: ':yellow_circle:'
        }
        return switch[self]
    
    def to_text_markdown(self) -> str:
        switch = {
            ChangeType.UNKNOWN: '\u26a0\ufe0f ',
            ChangeType.NONE: '',
            ChangeType.GOOD: '\U0001F34F',
            ChangeType.BAD: '\u274C',
            ChangeType.MIXED: '\U0001F536\uFE0F'
        }
        return switch[self]
