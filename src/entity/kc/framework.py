from attrs import define, field
from entity import entity
from entity.env import Env
from .svelte import Svelte
from .fastify import Server


@define(slots=True)
class Framework(entity.Entity):
    browser: Svelte = field(default=None)
    fastify: Server = field(default=None)

    def load(self, env: Env) -> None:
        self.browser = Svelte()
        self.browser.load(env)
        self.fastify = Server()
        self.fastify.load(env)

    def dump(self, store) -> None:
        self.browser.dump(store)
        self.fastify.dump(store)
