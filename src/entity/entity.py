from attrs import define, field, fields
from gettext import gettext as _

import util.log as logger
from util.str import is_valid_string

# from weakref import WeakSet, WeakValueDictionary


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
    def hasattr(self, attr: str) -> bool:
        try:
            getattr(self, attr)
        except AttributeError:
            return False
        return True

    # 　将child赋给指定的属性,如果属性为list,dict,weakset,则将child添加到集合中．
    def addchild(self, prop: str, child, key: str) -> bool:
        attr = getattr(self, prop, None)
        if isinstance(attr, list):
            attr.append(child)
        elif isinstance(attr, dict):
            if is_valid_string(key):
                attr[key] = child
            else:
                logger.warn(
                    _(
                        "adding empty key '%s' of entity(dict type),factory should be list?"
                    )
                    % (prop)
                )
            return False
        # elif isinstance(attr, WeakSet):
        elif isinstance(attr, set) or isinstance(attr, list):
            attr.add(child)
        else:
            setattr(self, prop, child)
        return True

    # 为指定的属性创建子实体．
    # kwargs默认可以传入add参数(默认为True)，用于指定是否将新创建的实体添加到父实体的属性中．
    # kwargs默认可以传入key参数(默认为空)，用于指定新创建的实体的名称．此时父实体的对应属性必须是一个字典．
    def newchild(self, prop: str, **kwargs):
        try:
            meta = getattr(fields(type(self)), prop, None)
            if not meta is None:
                # metadata = getattr(meta,'metadata',None)
                metadata = meta.metadata["childtype"]
                if isinstance(metadata, type):
                    # 收集可能传入的key和add参数
                    key = kwargs.pop("key", None)
                    add = kwargs.pop("add", True)
                    child = metadata(**kwargs)
                    if isinstance(child, Entity):
                        child.ctx = self.ctx
                        if is_valid_string(key):
                            child.name = key
                        elif is_valid_string(child.name):
                            key = child.name
                    if add:
                        self.addchild(prop, child, key)
                    return child
        except AttributeError:
            pass
        return None


# 由此compEnt替代了EntDict及EntList.保存了dict,list所属的Entity,propname.
@define(slots=True, frozen=False, eq=False)
class CompEnt(Entity):
    type: str = field(default="CompEnt")
    entity: Entity = field(default=None)
    propname: str = field(default="")

    def addchild(self, prop: str, child, key: str) -> bool:
        if isinstance(self.entity, Entity):
            return self.entity.addchild(prop, child, key)
        return False

    def newchild(self, prop: str, **kwargs):
        if isinstance(self.entity, Entity):
            if is_valid_string(prop):
                kwargs["key"] = prop
            return self.entity.newchild(self.propname, **kwargs)
        return None


# @define(slots=False)
# class EntDyn: #可以动态扩展属性的实体,不推荐使用
# type: str = field(default="EntDyn")
# name: str = field(default="")


# 使用弱引用来管理实体对象，可以方便实体对象通过名称来索引．
# @todo: 支持编辑距离搜索,支持模糊搜索
@define(slots=True, frozen=False, eq=False)
class EntRef(Entity):
    type: str = field(default="EntRef")
    # entrefs: WeakValueDictionary[str:Entity] = field(
    #     factory=WeakValueDictionary
    # )
    entrefs: dict[str:Entity] = field(factory=dict)

    # 当实体名称变化时，移除旧的实体引用，添加新的实体引用．
    def replace_entity(self, old_name: str, new_name: str, ent) -> None:
        if is_valid_string(old_name):
            self.remove_entity(old_name, ent)
        if is_valid_string(new_name):
            self.add_entity(new_name, ent)

    # 获取指定名称的实体对象，mul指示是否返回多个实体，如果为False，返回列表中最后一个实体.
    def get_entity(self, name: str, mul=False):
        ent = self.entrefs.get(name, None)
        if isinstance(ent, list):  # WeakSet):
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
            if isinstance(oldent, list):
                oldent.add(ent)
                return
            elif isinstance(oldent, Entity):
                if oldent == ent:
                    return
                self.entrefs[name] = list([oldent, ent])
                return
        self.entrefs[name] = ent

    # 删除实体引用
    def remove_entity(self, name: str, ent) -> None:
        oldent = self.entrefs.get(name, None)
        if oldent is None:
            return
        if ent == "all":
            self.entrefs.pop(name, None)
        elif isinstance(oldent, list):
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

    # 获取全部引用实体
    def values(self):
        return self.entrefs.values()

    # 获取全部引用实体及其名称对
    def items(self):
        return self.entrefs.items()

    # # 获取全部引用实体的数量
    # def __len__(self):
    #     return len(self.entrefs)
