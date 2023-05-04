from attrs import define, field
from enum import Enum, auto

from entity.entity import Entity


@define(slots=True, frozen=False, eq=False)
class Dtd(Entity):
    type: str = field(default="Dtd")


@define(slots=True, frozen=False, eq=False)
class Result(Entity):
    class Determine(Enum):
        ALWAYS = auto()  # 总是执行
        BOOL = auto()  # 布尔值为真执行
        INVBOOL = auto()  # 布尔值为假执行

    type: str = field(default="Result")
    dtrm: Determine = field(default=Determine.ALWAYS)
    # -1: 下一行为,-2: 异常终止, -3: 正常终止 >=0 为跳转行为序号
    next: int = field(default=-1)


@define(slots=True, frozen=False, eq=False)
class Submit(Entity):
    type: str = field(default="Submit")
    # 需要执行的动作,与谓语相同
    pred: str = field(default="")
    # 宾语
    obj: str = field(default="")
    # 如果需要提交信息，这里列出需要提交的信息名称及格式
    datas: "dict[str:any]" = field(factory=dict)


@define(slots=True, frozen=False, eq=False)
class Subj(Entity):
    class Determine(Enum):
        invalid = 0
        ROLE = auto()
        WF = auto()
        PREOBJ = auto()

    type: str = field(default="Subj")
    # 主语筛选器模式．(buildin: role: 拥有角色标志的任意访问者 2. wf: 工作流程中前置角色相同. 3. obj: 通过前置行为的宾语关联．)
    # 通用形式为一个Transformer
    dtrm: Determine = field(default=0)
    # 为主语筛选器提供的参数．(role: 角色名. wf: 索引的工作流程前置角色. obj: 宾语名.)
    paras: "dict[str:any]" = field(factory=dict)


@define(slots=True, frozen=False, eq=False)
class Pred(Entity):
    class Determine(Enum):
        invalid = 0
        GET = auto()  # 获取信息
        PUT = auto()  # 提交信息
        SELONE = auto()  # 从类集中选择一个
        SELMD = auto()  # 从类集中选多个(直接模式)
        SELMS = auto()  # 从类集中选多个(可缓存模式-例如购物车)
        MANAGE = auto()  # 管理信息，要增删改查
        ACT = auto()  # 执行其它流程

    type: str = field(default="Pred")
    # 谓语(buildin: get:  2. put: 提交信息. 3. selone: 从类集中选择一个. 4 selmd: 从类集中选多个(直接模式).5 selms: 从类集中选多个(可缓存模式-例如购物车) 6. act: 执行其它流程．)
    dtrm: Determine = field(default=0)


@define(slots=True, frozen=False, eq=False)
class Obj(Entity):
    class Determine(Enum):
        invalid = 0
        DEPWF = auto()  # 通过依赖流程提交的信息来决定.

    type: str = field(default="Obj")
    dtrm: Determine = field(default=0)
    datas: "dict[str:any]" = field(factory=dict)


@define(slots=True, frozen=False, eq=False)
class Behave(Entity):
    type: str = field(default="Behave")
    # 是否是一个行为,系统只与行为交换信息，而动作不交换信息，只辅助人类．
    isBehave: bool = field(default=True)
    # 主语
    subj: str = field(default="")
    # 谓语
    pred: str = field(default="")
    # 宾语
    obj: str = field(default="")
    # 如果需要提交信息，这里列出需要提交的信息名称及格式
    datas: "dict[str:any]" = field(factory=dict)
    # 结果跳转(分支)
    results: "list[Result]" = field(
        factory=list, metadata={"childtype": Result}
    )
    # 相同主语的其它动作. @todo: 这是合并后结果，可以不予以合并，工作流中允许一个主语相同的序列
    submits: "list[Submit]" = field(
        factory=list, metadata={"childtype": Submit}
    )


@define(slots=True, frozen=False, eq=False)
class Workflow(Entity):
    type: str = field(default="Workflow")
    dtd: str or Entity = field(default="", metadata={"childtype": Dtd})
    behaves: "list[str, Behave]" = field(
        factory=list, metadata={"childtype": Behave}
    )


@define(slots=True, frozen=False, eq=False)
class Role(Entity):
    type: str = field(default="Role")
    # 该角色的工作流程


@define(slots=True, frozen=False, eq=False)
class Humod(Entity):
    type: str = field(default="Humod")
    wfs: "dict[str, Workflow]" = field(
        factory=dict, metadata={"childtype": Workflow}
    )
    dtds: "dict[str, Dtd]" = field(factory=dict, metadata={"childtype": Dtd})
    roles: "dict[str, Role]" = field(
        factory=dict, metadata={"childtype": Role}
    )

    # def __attrs_post_init__(self):
    #     from store import Store

    #     inst: Store = Store.instance()
    #     ctx = inst.getctx(HUMOD_CTX_NAME)
    #     ctx.add_entity("wfs", self.wfs)
    #     ctx.add_entity("dtds", self.dtds)
