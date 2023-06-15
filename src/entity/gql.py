from attrs import define, field
from entity.entity import Entity
from jinja2 import Template


@define(slots=True, frozen=False, eq=False)
class QueryType(Entity):
    type: str = field(default="Database")
    name: str = field(default="")
    typename: str= field(default="str")

@define(slots=True, frozen=False, eq=False)
class GqlEntity(Entity):
    type: str = field(default="Gql")
    template: str = ""
    apiQuerys: list = []
    apiMuts: list = []
    queryTypes: "list[QueryType]" = field(factory=list, metadata={"childtype": QueryType})
