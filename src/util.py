import colored
from click import echo
from gettext import gettext as _


def warn(*args) -> None:  # type: ignore[no-untyped-def]
    # 将args拼接成字符串
    message = " ".join(args)
    echo(colored.stylize(_("Warn: ") + message, colored.fg("yellow")))


def error(*args) -> None:  # type: ignore[no-untyped-def]
    # 将args拼接成字符串
    message = " ".join(args)
    echo(colored.stylize(_("Error: ") + message, colored.fg("red")))


def info(*args) -> None:  # type: ignore[no-untyped-def]
    # 将args拼接成字符串
    message = " ".join(args)
    echo(colored.stylize(_("Info: ") + message, colored.fg("white")))
