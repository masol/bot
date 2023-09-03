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

    # 返回是否初始化成功．
    def init(self, opts: dict) -> bool:
        self.env = Env(**opts)
        if not self.env.init():
            return False
        self.kc.scan(self.env)
        return True
        # print(self.env)
