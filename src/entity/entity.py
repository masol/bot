from attrs import define, field

from .entref import EntRef

# @define
# class Meta:
#     type: str = field(default="Entity")  # type name
#     abs: bool = field(default=False)  # is abstract


@define(slots=True)
class Entity:
    # type: str = field(metadata={"desc": ""}, default="Entity")
    type: str = field(default="Entity")
    name: str = field(default="")


# @define(slots=False)
# class EntDyn: #可以动态扩展属性的实体,不推荐使用
# type: str = field(default="EntDyn")
# name: str = field(default="")


@define(slots=True)
class Model(Entity):
    type: str = field(default="Model")
    refs: EntRef = field(default=EntRef())


@define(slots=True)
class EntList(Entity):
    type: str = field(default="EntTree")
    data: list = field(default=[])
    childtype: type = field(default=Entity)

    def createchild(self, **kwargs) -> type or None:
        if not callable(self.childtype):
            return None
        child = self.childtype(**kwargs)
        self.data.append(child)
        return child


@define(slots=True)
class EntDict(Entity):
    type: str = field(default="EntDict")
    data: dict = field(default={})
    childtype: type = field(default=Entity)

    def createchild(self, key, **kwargs) -> type or None:
        if not callable(self.childtype):
            return None
        child = self.childtype(**kwargs)
        child.name = key
        self.data[key] = child
        return child

    def __getitem__(self, key):
        return self.data[key]

    def __setitem__(self, key, value):
        self.data[key] = value

    def __delitem__(self, key):
        del self.data[key]

    def __len__(self):
        return len(self.data)

    def __str__(self):
        return str(self.data)

    def clear(self):
        self.data.clear()

    def fromkeys(self, seq, value=None):
        return self.data.fromkeys(seq, value)

    def get(self, key, default=None):
        return self.data.get(key, default)

    def items(self):
        return self.data.items()

    def keys(self):
        return self.data.keys()

    def pop(self, key, default=None):
        return self.data.pop(key, default)

    def popitem(self):
        return self.data.popitem()

    def setdefault(self, key, default=None):
        return self.data.setdefault(key, default)

    def update(self, *args, **kwargs):
        return self.data.update(*args, **kwargs)

    def values(self):
        return self.data.values()

    def __iter__(self):
        return iter(self.data)

    def __contains__(self, item):
        return item in self.data
