from attrs import define, field
from entity import entity
from entity.env import Env

from .tpl import Tplbase


# 做为fastify server的实现．当前尚未实现客户端知识库加载．
@define(slots=True)
class Server(entity.Entity):
    # server的loader及模板环境
    srv_tpl: "Tplbase" = field(factory=Tplbase)
    # codeblk_tpl: "Tplbase" = field(factory=Tplbase)    

    def dump_mode(self, dump_mode, store, outpath, gather_info):
        # if dump_mode == "page":
        #     return self.dump_all_page(store, outpath, gather_info.vars)
        raise ValueError(f"fatify中未支持渲染模式{dump_mode}")

    def dump(self, store):
        self.srv_tpl.render_all(
            store,
            "server",
            self.dump_mode
        )


    def load(self, env: Env):
        self.srv_tpl.load(env.app_path("kc", "server"))
