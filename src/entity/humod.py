from attrs import define, field
from enum import Enum, auto

from entity.entity import Entity


@define(slots=True, frozen=False, eq=False)
class Dtd(Entity):
    type: str = field(default="Dtd")


@define(slots=True, frozen=False, eq=False)
class Adv(Entity):
    class Determine(Enum):
        invalid = 0
        TIMEOUT = auto()  # 超时委托系统自动执行(例如自动取消订单)

    type: str = field(default="Adv")
    dtrm: Determine = field(default=0)
    datas: "dict[str:any]" = field(factory=dict)


# Concurrent behave.(可并发行为,相同主语的其它可选动作.)
@define(slots=True, frozen=False, eq=False)
class Cncnt(Entity):
    type: str = field(default="Cncnt")
    # 状语:
    adv: str or Adv = field(default="")
    # 需要执行的动作,与谓语相同
    pred: str = field(default="")
    # 宾语
    obj: str = field(default="")
    # 如果需要提交信息，这里列出需要提交的信息名称及格式
    datas: "dict[str:any]" = field(factory=dict)
    # -1: 下一行为 >=0 为跳转行为序号
    next: int = field(default=-1)


@define(slots=True, frozen=False, eq=False)
class Subj(Entity):
    class Determine(Enum):
        invalid = 0
        ROLE = auto()
        WF = auto()
        PREOBJ = auto()
        MODIF = auto()

    type: str = field(default="Subj")
    # 主语筛选器模式．(buildin: role: 拥有指定角色标志的任意访问者 2. wf: 工作流程中前置角色相同. 3. obj: 通过前置行为的宾语关联．)
    # 通用形式为一个Transformer
    dtrm: Determine = field(default=0)
    # 为主语筛选器提供的参数．(role: 角色名. wf: 索引的工作流程前置角色. obj: 宾语名. modif: 筛选器)
    paras: "dict[str:str]" = field(factory=dict)


@define(slots=True, frozen=False, eq=False)
class Pred(Entity):
    class Determine(Enum):
        invalid = 0
        GET = 0x7528035A93EE69CEDB1DBDDB2F0BFCC8  # 获取信息
        PUT = 0x3E75383A5992A6D15FB81E872E46E256  # 提交信息
        SELONE = 0xE300B17B4A4729788A2C3BD920E8E0EC  # 从类集中选择一个
        SELMD = (
            0x371E624E59DFE59A15B5628286070044  # 从类集中选多个(直接模式),自动将流程拆分为多个流程
        )
        SELMS = 0x902FC3E1087827A338E5C5F403E298F3  # 从类集中选多个(可缓存模式-例如购物车)，自动将流程拆分为多个并行执行．
        MANAGE = 0x92814A387D2FE972E8AA877BC152980C  # 管理信息，要增删改查
        APPROVE = 0xED36B4A24E02A8786F52126DE566CF69  # 审批信息，显示同意，拒绝状态．
        # ACT = auto()  # 执行其它流程

    type: str = field(default="Pred")
    # 谓语(buildin: get:  2. put: 提交信息. 3. selone: 从类集中选择一个. 4 selmd: 从类集中选多个(直接模式).5 selms: 从类集中选多个(可缓存模式-例如购物车) 6. act: 执行其它流程．)
    dtrm: Determine = field(default=0)
    # act: 执行其它流程时，需要执行的流程名．
    act: str = field(default="")


@define(slots=True, frozen=False, eq=False)
class Obj(Entity):
    class Determine(Enum):
        invalid = 0
        MODIF = auto()        

    type: str = field(default="Obj")
    dtrm: Determine = field(default=0)
    datas: "dict[str:str]" = field(factory=dict)


@define(slots=True, frozen=False, eq=False)
class Behave(Entity):
    type: str = field(default="Behave")
    # 是否是一个行为,系统只与行为交换信息，而动作不交换信息，只辅助人类．
    isBehave: bool = field(default=True)
    # 　完整的一句话，描述行为．
    stm: str = field(default="")
    # 主语
    subj: str or Subj = field(default="")
    # 状语:
    adv: str or Adv = field(default="")
    # 谓语
    pred: str or Pred = field(default="")
    # 宾语
    obj: str or Obj = field(default="")
    # 如果需要提交信息，这里列出需要提交的信息名称及格式
    datas: "dict[str:any]" = field(factory=dict)
    # -1: 下一行为 -2: 留在此行为 -3: 结束流程 >=0 为跳转行为序号
    next: int = field(default=-1)
    # 相同主语的附加的其它可选动作.(例如审批，当前行为在同一界面同时存在)
    cncnt: "list[Cncnt]" = field(factory=list, metadata={"childtype": Cncnt})


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
    #     from store import Storew

    #     inst: Store = Store.instance()
    #     ctx = inst.getctx(HUMOD_CTX_NAME)
    #     ctx.add_entity("wfs", self.wfs)
    #     ctx.add_entity("dtds", self.dtds)
