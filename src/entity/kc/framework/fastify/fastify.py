from attrs import define, field

from ...requirement import Requirement
from ..project import Project

from os import path


# 做为fastify server的实现．当前尚未实现客户端知识库加载．
@define(slots=True)
class Server(Project):
    type: str = field(default="Server")

    # 项目的模板路径．
    tplpath: str = field(default=path.join("kc", "server"))
    # 项目的代码名称．
    name: str = field(default="server")

    # codeblk_tpl: "Tplbase" = field(factory=Tplbase)

    def dump_mode(self, dump_mode, store, outpath):
        # if dump_mode == "page":
        #     return self.dump_all_page(store, outpath, gather_info.vars)
        raise ValueError(f"fastify中未支持渲染模式{dump_mode}")
