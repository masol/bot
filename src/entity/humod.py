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
class Behave(Entity):
    type: str = field(default="Behave")
    # 主语
    subj: str = field(default="")
    # 谓语
    pred: str = field(default="")
    # 宾语
    obj: str = field(default="")
    # 用户提交信息
    submits: list[str, Submit] = field(
        factory=list, metadata={"childtype": Submit}
    )


@define(slots=True, frozen=False, eq=False)
class Workflow(Entity):
    type: str = field(default="Workflow")
    dtd: str or Entity = field(default="", metadata={"childtype": Dtd})
    behaves: list[str, Behave] = field(
        factory=list, metadata={"childtype": Behave}
    )


@define(slots=True, frozen=False, eq=False)
class Humod(Entity):
    type: str = field(default="Humod")
    wfs: dict[str, Workflow] = field(
        factory=dict, metadata={"childtype": Workflow}
    )
    dtds: dict[str, Dtd] = field(factory=dict, metadata={"childtype": Dtd})

    # def __attrs_post_init__(self):
    #     from store import Store

    #     inst: Store = Store.instance()
    #     ctx = inst.getctx(HUMOD_CTX_NAME)
    #     ctx.add_entity("wfs", self.wfs)
    #     ctx.add_entity("dtds", self.dtds)
