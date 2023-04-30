from attrs import define, field
from singleton.singleton import Singleton  # ,ThreadSafeSingleton

from entity.entity import Entity, EntRef
from entity.env import Env


@Singleton
@define(slots=True)
class Store:
    env: Env = field(metadata={"desc": ""}, default=None)
    models: dict[str:Entity] = field(default={})
    # 记录了上下文．当前的上下文对象是以Model来划分的．知识库是一种可持久化的上下文．Job2的实现中,上下文需要是一个实体．
    context: dict[str:EntRef] = field(default={"": EntRef()})

    def init(self, opts: dict) -> None:
        self.env = Env(**opts)
        # print(self.env)

    def hasctx(self, name: str) -> bool:
        return name in self.context

    def rmctx(self, name: str) -> None:
        if name in self.context:
            del self.context[name]

    def getctx(self, name: str) -> EntRef:
        if name not in self.context:
            self.context[name] = EntRef()
        return self.context[name]
