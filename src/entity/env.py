from attrs import define, field

import util.log as logger
from util.str import is_valid_string

from . import entity
from appdirs import user_data_dir
from os import path, getcwd, listdir, remove, makedirs
import shutil


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
    subdir: str = field(default="site")
    app_base: str = field(default="")

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

    def app_path(self, *args):
        if not is_valid_string(self.app_base):
            self.app_base = path.normpath(
                path.join(path.abspath(__file__), "..", "..", "..")
            )
        # print("self.app_base=", self.app_base)
        return path.join(self.app_base, *args)

    def full_outdir(self, *args):
        if path.isabs(self.output_dir):
            return self.output_dir
        return path.join(getcwd(), self.output_dir, *args)

    # 返回初始化是否成功．
    def init(self) -> bool:
        if not is_valid_string(self.kc_dir):
            self.kc_dir = user_data_dir(appname="bot", appauthor=False)
        if not is_valid_string(self.output_dir):
            self.output_dir = "target"
        target = self.full_outdir()
        if path.exists(target):
            if path.isdir(target):
                if self.force:
                    if self.verbose:
                        logger.info(f"输出目录'{target}'不为空，但是指定了--force参数，覆盖之.\n\t您可以在调用命令前自行删除．")
                    # shutil.rmtree(target)
                elif not Env.is_directory_empty(target):
                    logger.error(f"输出目录'{target}'已经存在并且不为空，如需要覆盖，请添加--force命令行参数．")
                    return False
            else:
                if self.force:
                    if self.verbose:
                        logger.info(f"输出目录'{target}'是一个文件，删除之.")
                    remove(target)
                else:
                    logger.error(f"指定的输出目录'{target}'已经存在同名文件．")
                    return False
        if not path.exists(target):
            Env.mkdirs(target)
        return True

    @staticmethod
    def mkdirs(path):
        try:
            makedirs(path)
        except FileExistsError:
            # directory already exists
            pass

    @staticmethod
    def is_directory_empty(dir_path):
        return not bool(listdir(dir_path))

    @staticmethod
    def writefile(filepath, content):
        directory = path.dirname(filepath)
        Env.mkdirs(directory)
        with open(filepath, "w") as file:
            file.write(content)

    def cpbin(srcpath,destpath):
        directory = path.dirname(destpath)
        Env.mkdirs(directory)
        shutil.copyfile(srcpath, destpath)

