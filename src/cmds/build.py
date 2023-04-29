import click
from gettext import gettext as _
from sklearn.pipeline import Pipeline

from store import Store
from trans import Humod, JobDuty
from util.log import LoggerExcept

# import util
# import store.load as loader
# from store.humod import Humod


def build(opts: dict) -> None:  # type: ignore[type-arg]
    pipeline = Pipeline([("load", Humod()), ("jobduty", JobDuty())])

    store = Store.instance()
    store.init(opts)
    try:
        result = pipeline.fit_transform(store)
        click.echo(f"result={result}")
    except LoggerExcept as e:
        pass

    # opts = copy.deepcopy(opts)
    # inst = Humod.instance()
    # inst.env.config(copy.deepcopy(opts))
    # loader.load(src, opts)
    # click.echo(f"inst={inst.env['verbose2']}")
    # click.echo(f"opts={opts}")
    # click.echo(_("bot cmd1"))
    # click.echo(_("bot cmd2"))
