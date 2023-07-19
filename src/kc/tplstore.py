from attrs import define, field
from entity.entity import Entity


@define(slots=True)
class Tplstore(Entity):
    def withdir(self, dir):
        pass
