from attrs import define, field
from weakref import WeakSet, WeakValueDictionary

from util.str import is_valid_string

# @define
# class Meta:
#     type: str = field(default="Entity")  # type name
#     abs: bool = field(default=False)  # is abstract


@define(slots=True, frozen=False, eq=False)
class Entity:
    # type: str = field(metadata={"desc": ""}, default="Entity")
    type: str = field(default="Entity")
    # 本实体的引用所属的上下文．空字符串不会被加入上下文索引中．
    ctx: str = field(default="")
    # parent = field(default=None) # 父上下文，在Job2中予以支持．
    name: str = field(
        default="",
        on_setattr=lambda instance, attribute, value: instance._set_name(
            attribute, value
        ),
    )

    # 获取本实体所属的上下文对象.
    def getctxobj(self):
        if not is_valid_string(self.ctx):
            return None
        from store import Store

        inst: Store = Store.instance()
        return inst.getctx(self.ctx)

    # 当实体的名称发生变化时，更新上下文中的索引．
    def _set_name(self, attribute, value):
        # print("call into _set_name", value, self.name, attribute)
        # 不向context中保存未命名实体．
        if len(self.ctx) > 0 and (is_valid_string(value) or is_valid_string(self.name)):
            from store import Store

            inst: Store = Store.instance()
            inst.getctx(self.ctx).replace_entity(self.name, value, self)
        return value

    # 本实体是否拥有指定的属性
    def has(self, attr: str) -> bool:
        try:
            getattr(self, attr)
        except AttributeError:
            return False
        return True


# @define(slots=False)
# class EntDyn: #可以动态扩展属性的实体,不推荐使用
# type: str = field(default="EntDyn")
# name: str = field(default="")


# 使用弱引用来管理实体对象，可以方便实体对象通过名称来索引．
# @todo: 支持编辑距离搜索,支持模糊搜索
@define(slots=True, frozen=False, eq=False)
class EntRef(Entity):
    type: str = field(default="EntRef")
    entrefs: WeakValueDictionary[str:Entity] = field(factory=WeakValueDictionary)

    # 当实体名称变化时，移除旧的实体引用，添加新的实体引用．
    def replace_entity(self, old_name: str, new_name: str, ent) -> None:
        if is_valid_string(old_name):
            self.remove_entity(old_name, ent)
        if is_valid_string(new_name):
            self.add_entity(new_name, ent)

    # 获取指定名称的实体对象，mul指示是否返回多个实体，如果为False，返回列表中最后一个实体.
    def get_entity(self, name: str, mul=False):
        ent = self.entrefs.get(name, None)
        if isinstance(ent, WeakSet):
            entLen = len(ent)
            if entLen == 0:
                self.entrefs.pop(name, None)
                return None
            elif entLen == 1:
                for ref in entLen:
                    obj = ref()
                    if obj is not None:
                        self.entrefs[name] = obj
                        return obj
            if not mul:
                return list(ent)[:-1]
        return ent

    # 添加实体引用
    def add_entity(self, name: str, ent) -> None:
        if name is None:
            return
        if name in self.entrefs:
            from .entity import Entity

            oldent = self.entrefs.get(name, None)
            if isinstance(oldent, WeakSet):
                oldent.add(ent)
                return
            elif isinstance(oldent, Entity):
                if oldent == ent:
                    return
                self.entrefs[name] = WeakSet([oldent, ent])
                return
        self.entrefs[name] = ent

    # 删除实体引用
    def remove_entity(self, name: str, ent) -> None:
        oldent = self.entrefs.get(name, None)
        if oldent is None:
            return
        if ent == "all":
            self.entrefs.pop(name, None)
        elif isinstance(oldent, WeakSet):
            oldent.remove(ent)
            if len(oldent) == 0:
                self.entrefs.pop(name, None)
        elif oldent == ent:
            self.entrefs.pop(name, None)

    # 清空全部实体引用
    def clear(self) -> None:
        self.entrefs.clear()

    # 获取全部引用实体的名称
    def keys(self):
        return self.entrefs.keys()


@define(slots=True, frozen=False, eq=False)
class EntList(Entity):
    type: str = field(default="EntList")
    data: list[Entity] = field(factory=list)
    childtype: type = field(default=Entity)

    # 创建子实体并加入data,如果子实体有parent属性,则设置其parent属性为当前实体.
    def createchild(self, **kwargs) -> type or None:
        if not callable(self.childtype):
            return None
        child = self.childtype(**kwargs)
        self.data.append(child)
        if child.has("parent"):
            child.parent = self
        return child


@define(slots=True, frozen=False, eq=False)
class EntDict(Entity):
    type: str = field(default="EntDict")
    data: dict[str:Entity] = field(factory=dict)
    childtype: type = field(default=Entity)

    # 创建子实体并加入data,如果子实体有parent属性,则设置其parent属性为当前实体.
    def createchild(self, key, **kwargs) -> type or None:
        if not callable(self.childtype):
            return None
        child = self.childtype(**kwargs)
        child.name = key
        self.data[key] = child
        if child.has("parent"):
            child.parent = self
        return child

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
