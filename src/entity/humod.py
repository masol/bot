from attrs import define, field
from typing import Any

from entity.entity import EntDict, Entity, Model


@define(slots=False)
class Behave(Entity):
    type: str = field(default="Behave")
    parent: Entity = field(default=None)


@define(slots=False)
class Workflow(Entity):
    type: str = field(default="Workflow")


@define(slots=False)
class Workflows(EntDict):
    name: str = field(default="wfs")
    type: str = field(default="Workflows")


@define(slots=False)
class Dtd(Entity):
    type: str = field(default="Dtd")


@define(slots=False)
class Dtds(EntDict):
    name: str = field(default="dtds")
    type: str = field(default="Dtds")


@define(slots=False)
class Humod(Model):
    type: str = field(default="Humod")
    wfs: Workflows = field(default=Workflows())
    dtds: Dtds = field(default=Dtds())

    def __post_init__(self):
        self.refs = EntDict()
        self.refs["wfs"] = self.wfs
        self.refs["dtds"] = self.dtds
