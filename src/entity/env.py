from attrs import define, field

import util.log as logger
from util.str import is_valid_string

from . import entity
from appdirs import user_data_dir
from os import path


@define(slots=True)
class Env(entity.Entity):
    src: str = ""
    type = "Env"
    verbose: bool = field(default=False)
    strict: bool = field(default=False)
    werrors: "[str]" = field(factory=list)
    debug: bool = field(default=False)
    dump_models: list = field(factory=list)
    log: str = field(default="log")
    loglevel: str = field(default="info")
    logformat: str = field(default="%(asctime)s %(levelname)s %(message)s")
    logdatefmt: str = field(default="%Y-%m-%d %H:%M:%S")
    logfilename: str = field(default="log.txt")
    logutc: bool = field(default=True)
    tolerant: bool = field(default=False)
    output_dir: str = field(default="target")
    kc_dir: str = field(default="")
    force: bool = field(default=False)

    # 支持warn_as_error的warning.
    def warn(self, cate: str, msg: str, warn_ex_msg: str) -> None:
        if cate in self.werrors:
            logger.error(msg)
        elif self.strict and is_valid_string(cate) and cate.startswith("a"):
            logger.error(msg)
        else:
            logger.warn(msg + warn_ex_msg or "")

    # 获取基于知识库中的子库目录．
    def kcd_path(self, *args):
        return path.join(self.kc_dir, *args)

    def init(self) -> str:
        if not is_valid_string(self.kc_dir):
            self.kc_dir = user_data_dir(appname="bot", appauthor=False)
