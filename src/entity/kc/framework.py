from attrs import define, field
from entity import entity
from entity.env import Env
from .svelte import Svelte


@define(slots=True)
class Framework(entity.Entity):
    client: Svelte = field(default=None)
    # server: Server = field(default=None)

    def load(self, env: Env) -> None:
        self.client = Svelte()
        self.client.load(env)

    def dump(self, store) -> None:
        self.client.dump(store)
        pass
