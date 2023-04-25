import click
import copy
from gettext import gettext as _

import store.load as loader
import util


def build(opts: dict) -> None:  # type: ignore[type-arg]
    src: str = opts.get("src")  # type: ignore[assignment]
    opts = copy.deepcopy(opts)
    loader.load(src, opts)
    print(opts.get("output_dir"))
    print(opts.get("src"))
    print(opts.get("verbose"))
    click.echo(_("bot cmd1"))
