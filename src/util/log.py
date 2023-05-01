from click import echo
from gettext import gettext as _
import rich


class LoggerExcept(Exception):
    def __init__(self, message):
        self.message = message


def warn(*args) -> None:  # type: ignore[no-untyped-def]
    # 将args拼接成字符串
    message = " ".join(args)
    prefix = _("Warn:")
    rich.print(f"[bold yellow]{prefix}[/bold yellow] {message}")


def error(*args, noExcept=False) -> None:  # type: ignore[no-untyped-def]
    # 将args拼接成字符串
    message = " ".join(args)
    prefix = _("Error: ")
    rich.print(f"[bold red]{prefix}[/bold red] {message}")    
    if not noExcept:
        raise LoggerExcept(message)


def info(*args) -> None:  # type: ignore[no-untyped-def]
    # 将args拼接成字符串
    message = " ".join(args)
    prefix = _("Info: ")
    rich.print(f"[bold]{prefix}[/bold] {message}")
