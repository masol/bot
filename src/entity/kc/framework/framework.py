from attrs import define, field
from .svelte.svelte import Svelte
from .fastify.fastify import Server
from ..requirement import Requirement

@define(slots=True)
class Framework:
    browser: Svelte = field(default=None)
    fastify: Server = field(default=None)
    req: Requirement = field(default=None)

    def load(self, req: Requirement) -> None:
        self.req = req
        self.browser = Svelte()
        self.browser.load(req)
        self.fastify = Server()
        self.fastify.load(req)

    def dump(self) -> None:
        self.req.on_before_dump()
        self.browser.dump(self.req)
        self.fastify.dump(self.req)
