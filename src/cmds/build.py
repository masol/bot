from gettext import gettext as _

from store import Store
from trans import createPipe
from util.log import LoggerExcept

# import util
# import store.load as loader
# from store.humod import Humod


def build(opts: dict) -> None:  # type: ignore[type-arg]
    store: Store = Store.instance()
    store.init(opts)
    try:
        pipeline = createPipe(["humod", "integrity", "jobduty", "uipage", "database"])
        pipeline.fit_transform(store)

    except LoggerExcept as e:
        pass
