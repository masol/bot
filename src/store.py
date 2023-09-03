from attrs import define, field
from singleton.singleton import Singleton  # ,ThreadSafeSingleton

from entity.entity import Entity
from entity.env import Env
from entity.kc import KC


@Singleton
@define(slots=True)
class Store:
    env: Env = field(metadata={"desc": ""}, default=None)
    models: "dict[str:Entity]" = field(default={})
    kc: KC = field(factory=KC)

    def init(self, opts: dict) -> None:
        self.env = Env(**opts)
        self.env.init()
        self.kc.scan(self.env)
        # print(self.env)
