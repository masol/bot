from attrs import define, field

from entity.entity import Entity

from jinja2 import Template

@define(slots=True, frozen=False, eq=False)
class Database(Entity):
    type: str = field(default="Database")
    template: Template = ""
    context: "dict[str, list]" = ""
