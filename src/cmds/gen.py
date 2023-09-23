from gettext import gettext as _

from store import Store
from trans import createPipe
from util.log import LoggerExcept

# import util
# import store.load as loader
# from store.humod import Humod


def build(opts: dict) -> None:  # type: ignore[type-arg]
    store: Store = Store.instance()
    if not store.init(opts):
        return
    try:
        # 确定框架及模块．(选择一组模板文件集合) ＃trans.
        # 对每个模板，提取其变量符号．
        # 扫描每个变量符号，构建其从输出到达符号的DAG(调用栈)．
        # pipeline = createPipe(["humod", "integrity"])
        # 使用调用栈，构建pipeline.执行之得到最终源码．
        pipeline = createPipe(["humod", "integrity", "jobduty", "arch"])
        pipeline.fit_transform(store)
        store.kc.dump()

    except LoggerExcept as e:
        pass
