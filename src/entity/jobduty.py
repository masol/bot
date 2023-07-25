from attrs import define, field

from entity.entity import Entity



@define(slots=True, frozen=False, eq=False)
class Duty(Entity):
    type: str = field(default="Duty")
    wfs: str= field(default="")
    bhs: int= field(default=-1)

    

@define(slots=True, frozen=False, eq=False)
class Role(Entity):
    type: str = field(default="Role")
    duties:"list[Duty]" = field(factory=list, metadata={"childtype": Duty})
    
    def append(self,wf,idx):
        duty=Duty(wfs=wf,bhs=idx)
        self.duties.append(duty)



@define(slots=True, frozen=False, eq=False)
class JobDuty(Entity):
    type: str = field(default="JobDuty")
    roles: "dict[str, Role]" = field(factory=dict, metadata={"childtype": Role})

    def ensure(self,rolename):
        if rolename in self.roles:
          return self.roles[rolename]
 
        role=Role()
        self.roles[rolename]=role
        return role 




# @define(slots=True, frozen=False, eq=False)
# class JobDuty(Entity):
#     type: str = field(default="JobDuty")
#     roles: "dict[str, Role]" = field(
#         factory=dict, metadata={"childtype": Role}
#     )

    def __attrs_post_init__(self):
        from store import Store

        inst: Store = Store.instance()
        # ctx = inst.getctx(JOBDUTY_CTX_NAME)
        # ctx.add_entity("wfs", self.wfs)
        # ctx.add_entity("dtds", self.dtds)
