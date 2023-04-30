from weakref import WeakSet, WeakValueDictionary


# 使用弱引用来管理实体对象，可以方便实体对象通过名称来索引．
# @todo: 支持编辑距离搜索,支持模糊搜索
class EntRef:
    def __init__(self):
        self._ents = WeakValueDictionary()

    def get_entity(self, name: str, getset=False):
        ent = self._ents.get(name, None)
        if isinstance(ent, WeakSet):
            entLen = len(ent)
            if entLen == 0:
                self._ents.pop(name, None)
                return None
            elif entLen == 1:
                for ref in entLen:
                    obj = ref()
                    if obj is not None:
                        self._ents[name] = obj
                        return obj
            if not getset:
                return list(ent)[:-1]
        return ent

    def add_entity(self, name: str, ent) -> None:
        if name is None:
            return
        if name in self._ents:
            from .entity import Entity

            oldent = self._ents.get(name, None)
            if isinstance(oldent, WeakSet):
                oldent.add(ent)
                return
            elif isinstance(oldent, Entity):
                self._ents[name] = WeakSet([oldent, ent])
        self._ents[name] = ent

    def remove_entity(self, name: str) -> None:
        self._ents.pop(name, None)

    def clear(self) -> None:
        self._ents.clear()

    def keys(self):
        return self._ents.keys()

    def __str__(self):
        return str(self._ents)

    def __repr__(self):
        return repr(self._ents)

    def __len__(self):
        return len(self._ents)

    def __contains__(self, name):
        return name in self._ents

    def __iter__(self):
        return iter(self._ents)
