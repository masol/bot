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

    store: Store = Store.instance()
    store.init(opts)
    try:
        pipeline.fit_transform(store)

        # click.echo(f"result={result}")
        refskeys = " ".join(store.getctx('humod').keys())
        click.echo(f"refskeys={refskeys}")
    except LoggerExcept as e:
        pass
