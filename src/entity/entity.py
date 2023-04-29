from attrs import define, field

from .entref import EntRef

# @define
# class Meta:
#     type: str = field(default="Entity")  # type name
#     abs: bool = field(default=False)  # is abstract


@define(slots=False)
class Entity:
    # type: str = field(metadata={"desc": ""}, default="Entity")
    type: str = field(default="Entity")
    name: str = field(default="")


@define(slots=False)
class Model:
    type: str = field(default="Model")
    name: str = field(default="")
    refs: EntRef = field(default=EntRef())


@define(slots=False)
class EntDict(Entity):
    data = field(default={})

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
