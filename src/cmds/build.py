import click
import copy
from gettext import gettext as _
from store.humod import Humod

import store.load as loader
import util


def build(opts: dict) -> None:  # type: ignore[type-arg]
    src: str = opts.get("src")  # type: ignore[assignment]
    opts = copy.deepcopy(opts)
    inst = Humod()
    inst.env.config(copy.deepcopy(opts))
    loader.load(src, opts)
    click.echo(f"inst={inst.env['verbose2']}")
    click.echo(f"opts={opts}")
    click.echo(_("bot cmd1"))
    click.echo(_("bot cmd2"))
