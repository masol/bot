from attrs import define, field
from entity import entity

from os import path

from .framework import Framework
from .requirement import Requirement


@define(slots=True)
class KC(entity.Entity):
    __framework: Framework = field(default=None)

    # 在api,ds,pages确定之后．开始加载依赖的kc.当前版本这里不予以选择．直接默认一个．
    @property
    def framework(self) -> None:
        # 这里直接返回初始化时确定的实例对象．
        return self.__framework

    # 将store中的模型，dump为代码．
    def dump(self) -> None:
        return self.__framework.dump()

    # 扫描kc,并收集全部的kc信息．
    def scan(self, store: "Store") -> None:
        # 如果kc_dir存在．扫描并加载其中的知识库．通过配置文件来给出知识库内容．
        env = store.env
        kcpath = env.kcd_path("kc")
        # print(kcpath)
        if path.isdir(kcpath):
            print("has kc dir,enter scan")
        
        if not self.__framework:
            self.__framework = Framework()
            req: Requirement = Requirement(store)
            self.__framework.load(req)
        # print(env.app_path())
        # 加载本地的知识库．
        # print("load local kc")
        # pass
