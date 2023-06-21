from attrs import define, field

from entity.entity import Entity

from jinja2 import Template

@define(slots=True, frozen=False, eq=False)
class Database(Entity):
    type: str = field(default="Database")
    template: str = ""
    tables: list = []

@define(slots=True, frozen=False, eq=False)
class Table(Entity):
    type: str = field(default="Table")
    name: str = ""
    correspondence: str = ""
    strings: list = []
    booleans: list = []

@define(slots=True, frozen=False, eq=False)
class String(Entity):
    type: str = field(default="String")
    name: str = ""
    correspondence: str = ""
    length: int = 0

@define(slots=True, frozen=False, eq=False)
class Boolean(Entity):
    type: str = field(default="Boolean")
    name: str = ""
    correspondence: str = ""
