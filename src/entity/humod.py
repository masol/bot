from attrs import define, field
from typing import Any

from entity.entity import EntDict, Entity, EntList

HUMOD_CTX_NAME = "humod"


@define(slots=True, frozen=False, eq=False)
class Submit(Entity):
    type: str = field(default="Submit")
    ctx: str = field(default=HUMOD_CTX_NAME)
    commit: str = field(default="")
    # parent: Entity = field(default=None)


@define(slots=True, frozen=False, eq=False)
class Behave(Entity):
    type: str = field(default="Behave")
    ctx: str = field(default=HUMOD_CTX_NAME)
    # parent: Entity = field(default=None)
    # 主语
    subj: str = field(default="")
    # 谓语
    pred: str = field(default="")
    # 宾语
    obj: str = field(default="")
    # 用户提交信息
    submits: EntList = field(default=EntList(childtype=Submit))


@define(slots=True, frozen=False, eq=False)
class Workflow(Entity):
    type: str = field(default="Workflow")
    ctx: str = field(default=HUMOD_CTX_NAME)
    dtd: str or EntDict = field(default="")
    behaves: EntList = field(default=EntList(childtype=Behave))


@define(slots=True, frozen=False, eq=False)
class Workflows(EntDict):
    name: str = field(default="wfs")
    type: str = field(default="Workflows")
    ctx: str = field(default=HUMOD_CTX_NAME)
    childtype: type = field(default=Workflow)


@define(slots=True, frozen=False, eq=False)
class Dtd(Entity):
    type: str = field(default="Dtd")
    ctx: str = field(default=HUMOD_CTX_NAME)
    parent: Entity = field(default=None)


@define(slots=True, frozen=False, eq=False)
class Dtds(EntDict):
    name: str = field(default="dtds")
    type: str = field(default="Dtds")
    ctx: str = field(default=HUMOD_CTX_NAME)
    childtype: type = field(default=Dtd)


@define(slots=True, frozen=False, eq=False)
class Humod(Entity):
    type: str = field(default="Humod")
    ctx: str = field(default=HUMOD_CTX_NAME)
    wfs: Workflows = field(default=Workflows())
    dtds: Dtds = field(default=Dtds())

    def __attrs_post_init__(self):
        from store import Store

        print(Workflows.data)

        inst: Store = Store.instance()
        ctx = inst.getctx(HUMOD_CTX_NAME)
        ctx.add_entity("wfs", self.wfs)
        ctx.add_entity("dtds", self.dtds)
