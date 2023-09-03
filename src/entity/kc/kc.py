from attrs import define, field

from entity import entity
from entity.env import Env
from os import path


@define(slots=True)
class Framework(entity.Entity):
    pass

@define(slots=True)
class KC(entity.Entity):
    __loaded: bool = field(default=False)
    __framework: bool = field(default=None)

    # 在api,ds,pages确定之后．开始加载依赖的kc.当前版本这里不予以选择．直接默认一个．
    @property
    def framework(self) -> None:
        if not self.__loaded:
            # 并不执行真正的检查trans中models并加载合适知识实例的
            self.__loaded = True
            # self._framework
        # 这里直接返回固定的实例对象．
        return self.__framework

    # 扫描kc,并收集全部的kc信息．
    def scan(self, env: Env) -> None:
        # 如果kc_dir存在．扫描并加载其中的知识库．通过配置文件来给出知识库内容．
        kcpath = env.kcd_path("kc")
        # print(kcpath)
        if path.isdir(kcpath):
            print("has kc dir,enter scan")
        # 加载本地的知识库．
        # print("load local kc")
        pass
