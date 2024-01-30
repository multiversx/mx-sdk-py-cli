from rich import print
from rich.markup import escape
from rich.panel import Panel


def show_message(message: str):
    print(Panel(f"[green]{escape(message)}"))


def show_critical_error(message: str):
    print(Panel(f"[red]{escape(message)}"))


def show_warning(message: str):
    print(Panel(f"[yellow]{escape(message)}"))


def confirm_continuation(message: str):
    answer = input(message)
    if answer.lower().strip() not in ["y", "yes"]:
        print("Confirmation not given. Stopping...")
        exit(1)
