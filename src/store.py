from attrs import define, field
from singleton.singleton import Singleton  # ,ThreadSafeSingleton

from entity.env import Env
from entity.entity import Model


@Singleton
@define(slots=False)
class Store:
    env: Env = field(metadata={"desc": ""}, default=None)
    models: dict[str:Model] = field(default={})

    def init(self, opts: dict) -> None:
        self.env = Env(**opts)
        # print(self.env)
