import esprima
from gettext import gettext as _

import util


def parse(content: str, ctx: dict) -> None:  # type: ignore[type-arg]
    src = ctx.get("src")
    try:
        # 使用esprima解析content
        ast = esprima.parseScript(
            content, {"range": True, "loc": True, "tolerant": ctx.get("tolerant")}
        )
    except esprima.Error as e:
        util.error(_('while compiling file "%s":\n\t') % src + str(e))
        return

    print(ast)
