import os
import requests
import urllib.parse
from gettext import gettext as _

import store.parse as parser
import util


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
            util.error(e)
            return None
    return None


def load(src: str, opts: dict) -> None:  # type: ignore[type-arg]
    base = opts.get("base") or os.getcwd()
    if not os.path.isabs(src):
        # str为url,获取去目录
        if urllib.parse.urlparse(base).scheme in ["http", "https"]:
            src = os.path.join(base, urllib.parse.urlparse(src).netloc)
        else:
            src = os.path.join(base, src)

    if not fileorurl(src):
        util.error(_("'%s' is neither a URL nor a file.") % src)
        return

    content = getcontent(src)
    # 如果content等于None，说明获取内容失败，直接返回．
    if not content:
        # cotent的类型是字符串,意味着不是因为错误，而是内容为空．
        if isinstance(content, str):
            util.warn(_('content of "%s" is empty.') % src)
        return

    parser.parse(
        content,
        {"src": src, "verbose": opts.get("verbose"), "tolerant": opts.get("tolerant")},
    )
    # 检查src,是一个存在的文件或者一个合法的URL.
    print(opts)
    print(opts.get("output_dir"))
    print(opts.get("src"))
    print(opts.get("verbose"))
