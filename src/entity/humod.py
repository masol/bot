from attrs import define, field

from entity.entity import Entity


@define(slots=True, frozen=False, eq=False)
class Dtd(Entity):
    type: str = field(default="Dtd")


@define(slots=True, frozen=False, eq=False)
class Submit(Entity):
    type: str = field(default="Submit")
    commit: str = field(default="")
    # parent: Entity = field(default=None)


@define(slots=True, frozen=False, eq=False)
class Subj(Entity):
    type: str = field(default="Subj")
    # 主语筛选器．(buildin: role: 拥有角色的任意 2. wf: 工作流程中前置角色相同. 3. obj: 通过前置行为的宾语关联．)
    mode: str = field(default="")
    # 为主语筛选器提供的参数．(role: 角色名. wf: 索引的工作流程前置角色. obj: 宾语名.)
    paras: dict[str:any] = field(factory=dict)


@define(slots=True, frozen=False, eq=False)
class Pred(Entity):
    type: str = field(default="Pred")
    # 谓语模式(buildin: get: 获取信息 2. put: 提交信息. 3. selone: 从类集中选择一个. 4 selmd: 从类集中选多个(直接模式).5 selms: 从类集中选多个(可缓存模式-例如购物车) 6. act: 执行其它流程．)
    mode: str = field(default="")


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
    # 用户提交信息
    submits: list[str, Submit] = field(factory=list, metadata={"childtype": Submit})


@define(slots=True, frozen=False, eq=False)
class Workflow(Entity):
    type: str = field(default="Workflow")
    dtd: str or Entity = field(default="", metadata={"childtype": Dtd})
    behaves: list[str, Behave] = field(factory=list, metadata={"childtype": Behave})


@define(slots=True, frozen=False, eq=False)
class Humod(Entity):
    type: str = field(default="Humod")
    wfs: dict[str, Workflow] = field(factory=dict, metadata={"childtype": Workflow})
    dtds: dict[str, Dtd] = field(factory=dict, metadata={"childtype": Dtd})

    # def __attrs_post_init__(self):
    #     from store import Store

    #     inst: Store = Store.instance()
    #     ctx = inst.getctx(HUMOD_CTX_NAME)
    #     ctx.add_entity("wfs", self.wfs)
    #     ctx.add_entity("dtds", self.dtds)
