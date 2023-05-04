from attrs import define, field

from entity.entity import Entity


@define(slots=True, frozen=False, eq=False)
class Page(Entity):
    type: str = field(default="Page")


@define(slots=True, frozen=False, eq=False)
class UIpage(Entity):
    type: str = field(default="JobDuty")
    pages: "dict[str, Page]" = field(
        factory=dict, metadata={"childtype": Page}
    )

    # def __attrs_post_init__(self):
    #     from store import Store

    #     inst: Store = Store.instance()
