from attrs import define, field

from entity.entity import Entity


@define(slots=True, frozen=False, eq=False)
class Role(Entity):
    type: str = field(default="Role")


@define(slots=True, frozen=False, eq=False)
class JobDuty(Entity):
    type: str = field(default="JobDuty")
    roles: dict[str, Role] = field(factory=dict, metadata={"childtype": Role})

    def __attrs_post_init__(self):
        from store import Store

        inst: Store = Store.instance()
        # ctx = inst.getctx(JOBDUTY_CTX_NAME)
        # ctx.add_entity("wfs", self.wfs)
        # ctx.add_entity("dtds", self.dtds)
