from rich import print
from rich.panel import Panel


def show_message(message: str):
    print(Panel(f"[green]{message}"))


def show_critical_error(message: str):
    print(Panel(f"[red]{message}"))


def show_deprecation_warning(message: str):
    print(Panel(f"[yellow]{message}"))
