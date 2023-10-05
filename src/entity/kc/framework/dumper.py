from attrs import define, field
from entity.entity import Entity
from os import path
from util.str import is_valid_string


# 服务于mode,跟踪流程行为级单元的创建上下文．
# *要求*:导出期，子元素之间不能再有依赖关系．依赖关系的解藕需要在模型期处理．(Requirement.__attrs_post_init__及其之前的Trans期)
@define(slots=True)
class Dumper(Entity):
    type: str = field(default="Dumper")
    # 输出相对路径．全路径由res.target(self.dirname)得到．
    dirname: str = field(default="")
    # 相对于target的基础路径．默认是空．页面是'src/routes'.
    basedir: str = field(default="")
    # 当前的需求对象．
    req: "Requirement" = field(default=None)
    # 当前的输出对象．
    res: "Response" = field(default=None)
    # 文件的渲染结果．(文件路径到渲染结果的映射)
    filecnt: "dict[str,str]" = field(factory=dict)

    def full_outpath(self, *args):
        return path.join(self.res.target, self.basedir, self.dirname, *args)

    def gen(self):
        raise ValueError("未实现BHDumper的gen方法．")

    def dump(self):
        self.gen()
        for fname, content in self.filecnt.items():
            if is_valid_string(content):
                print("Dumper.dump fname=", self.full_outpath(fname))
                self.req.store.env.writefile(self.full_outpath(fname), content)
