from attrs import define, field
from typing import Any

from entity.entity import EntDict, Entity, EntList, Model


@define(slots=True)
class Behave(Entity):
    type: str = field(default="Behave")
    parent: Entity = field(default=None)


@define(slots=True)
class Workflow(Entity):
    type: str = field(default="Workflow")
    behaves: EntList = field(default=EntList(childtype=Behave))


@define(slots=True)
class Workflows(EntDict):
    name: str = field(default="wfs")
    type: str = field(default="Workflows")
    childtype: type = field(default=Workflow)


@define(slots=True)
class Dtd(Entity):
    type: str = field(default="Dtd")


@define(slots=True)
class Dtds(EntDict):
    name: str = field(default="dtds")
    type: str = field(default="Dtds")
    childtype: type = field(default=Dtd)


@define(slots=True)
class Humod(Model):
    type: str = field(default="Humod")
    wfs: Workflows = field(default=Workflows())
    dtds: Dtds = field(default=Dtds())

    def __attrs_post_init__(self):
        self.refs.add_entity("wfs", self.wfs)
        self.refs.add_entity("dtds", self.dtds)
