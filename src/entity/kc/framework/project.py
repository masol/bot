from attrs import define, field

# from ..tplset import Tplset
from ..requirement import Requirement

from .response import Response


@define(slots=True)
class Project(Response):
    # 项目的模板集．
    tplset: "Tplset" = field(default=None)
    # 项目的代码名称．
    name: str = field(default=None)
    # 项目的模板路径．
    tplpath: str = field(default=None)

    # self is response.
    def dump_mode(self, modename, req: Requirement, render_vars: dict, outpath: str):
        # if dump_mode == "page":
        #     return self.dump_all_page(store, outpath, gather_info.vars)
        raise ValueError("进入基类纯虚函数dump_mode..")

    # self is response.
    def dump(self, req: Requirement):
        self.tplset.render_all(req, self)

    def load(self, req: Requirement):
        from ..tplset import Tplset

        if not self.tplset:
            self.tplset = Tplset()
        self.tplset.load(req.store.env.app_path(self.tplpath))
        self.target = req.store.env.full_outdir(self.name)
