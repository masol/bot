import colored
import esprima
from click import echo
from gettext import gettext as _


class LoggerExcept(Exception):
    def __init__(self, message):
        self.message = message


def warn(*args) -> None:  # type: ignore[no-untyped-def]
    # 将args拼接成字符串
    message = " ".join(args)
    echo(colored.stylize(_("Warn: ") + message, colored.fg("yellow")))


def error(*args, noExcept=False) -> None:  # type: ignore[no-untyped-def]
    # 将args拼接成字符串
    message = " ".join(args)
    echo(colored.stylize(_("Error: ") + message, colored.fg("red")))
    if not noExcept:
        raise LoggerExcept(message)


def info(*args) -> None:  # type: ignore[no-untyped-def]
    # 将args拼接成字符串
    message = " ".join(args)
    echo(colored.stylize(_("Info: ") + message, colored.fg("white")))
