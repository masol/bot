import os
import requests
import urllib.parse
from gettext import gettext as _

import util.log as logger

from .parse import parse


def fileorurl(src: str) -> bool:
    if os.path.isfile(src):
        return True
    if urllib.parse.urlparse(src).scheme in ["http", "https"]:
        return True
    return False


def getcontent(src: str) -> str or None:  # type: ignore[valid-type]
    if os.path.isfile(src):
        with open(src, mode="r", encoding="utf-8") as f:
            return f.read()
    elif urllib.parse.urlparse(src).scheme in ["http", "https"]:
        # 拦截异常，报错并返回空字符串．
        try:
            return requests.get(src, timeout=3).text
        except requests.exceptions.RequestException as e:
            logger.error(e)
            return None
    return None


def load(src: str, ctx: dict) -> bool:  # type: ignore[type-arg]
    if not src:
        logger.error(_("src is required."))
        return False

    base = ctx.get("base") or os.getcwd()
    if not ctx.get("loaded", None):
        ctx["loaded"] = {}

    if not os.path.isabs(src):
        # str为url,获取去目录
        if urllib.parse.urlparse(base).scheme in ["http", "https"]:
            src = os.path.join(base, urllib.parse.urlparse(src).netloc)
        else:
            src = os.path.join(base, src)

    if not fileorurl(src):
        logger.error(_("'%s' is neither a URL nor a file.") % src)
        return False

    if src in ctx["loaded"]:
        if ctx["verbose"]:
            logger.info(_('skipping "%s" (already loaded)') % src)
        return True
    else:
        ctx["loaded"][src] = True

    content = getcontent(src)
    # 如果content等于None，说明获取内容失败，直接返回．
    if not content:
        # cotent的类型是字符串,意味着不是因为错误，而是内容为空．
        if isinstance(content, str):
            logger.warn(_('content of "%s" is empty.') % src)
        return True

    ctx["content"] = content
    ctx["src"] = src
    parse(ctx)
    return True
