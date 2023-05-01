from attrs import define, field

from entity.entity import Entity


JOBDUTY_CTX_NAME = "jobduty"

@define(slots=True, frozen=False, eq=False)
class Role(Entity):
    type: str = field(default="Role")
    ctx: str = field(default=JOBDUTY_CTX_NAME)


@define(slots=True, frozen=False, eq=False)
class JobDuty(Entity):
    type: str = field(default="JobDuty")
    ctx: str = field(default=JOBDUTY_CTX_NAME)
    roles: dict[str, Role] = field(
        factory=dict, metadata={"childtype": Role}
    )

    def __attrs_post_init__(self):
        from store import Store

        inst: Store = Store.instance()
        # ctx = inst.getctx(JOBDUTY_CTX_NAME)
        # ctx.add_entity("wfs", self.wfs)
        # ctx.add_entity("dtds", self.dtds)
