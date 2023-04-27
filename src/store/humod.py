from typing import Any
from util.decor import singleton


class Env:
    def __init__(self) -> None:
        self._config: dict = {}

    def __getitem__(self, key):
        try:
            return self._config[key]
        except KeyError as e:
            pass
        return None

    def config(self, cfg: dict):
        self._config = cfg


class Entity:
    innerprop = {"name": "", "type": "Entity"}
    def defprop(self) -> dict:
        return {}

    def __init__(self) -> None:
        self._prop: dict = {}

    def __getattr__(self, name: str) -> Any:
        if name.startswith('_'):
            return object.__getattr__(self, name)
        try:
            return self._prop[name]
        except KeyError as e:
            pass
        return {**Entity.innerprop, **self.defprop()}.get(name, None)

    def __setattr__(self, name: str, value: Any) -> None:
        if name.startswith('_'):
            return object.__setattr__(self, name,value)
        self._prop[name] = value

    def __getitem__(self, key: str) -> Any:
        return self.__getattr__(key)

    def __setitem__(self, key: str, value: Any) -> None:
        self.__setattr__(key, value)


class Behave(Entity):
    def defprop(self) -> dict:
        return {"type": "Behave"}


class Workflow(Entity):
    def defprop(self) -> dict:
        return {"type": "Workflow"}


class Workflows(Entity):
    def defprop(self) -> dict:
        return {"type": "Workflows"}


class Dtds(Entity):
    def defprop(self) -> dict:
        return {"type": "Dtds"}


@singleton
class Humod:  # human model(workflow based usage description)
    def __init__(self):
        self._env = Env()
        self._wfs = Workflows()
        self._dtds = Dtds()

    @property
    def env(self):  # readonly property env.
        return self._env

    @property
    def wfs(self):  # readonly property wfs.
        return self._env

    @property
    def dtds(self):  # readonly property _dtds.
        return self._dtds
    
    def entity(self,name): # get entity by name
        if name == '$env':
            return self._env
        elif name == '$wf':
            return self._wfs
        elif name == '$dtd':
            return self._dtds
        return None
