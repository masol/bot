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
    type: str = field(default="Entity")
    name: str = field(
        default="",
        # on_setattr=lambda instance, attribute, value: instance._set_name(
        #     attribute, value
        # ),
    )

    # 获取本实体所属的上下文对象.上下文及parent都属于transformer.
    # def getctxobj(self):
    #     if not is_valid_string(self.ctx):
    #         return None
    #     from store import Store

    #     inst: Store = Store.instance()
    #     return inst.getctx(self.ctx)

    # 当实体的名称发生变化时，更新上下文中的索引．
    # 不再自动更新上下文索引，由上层调用者决定．上下文索引属于一个trans.
    # def _set_name(self, attribute, value):
    #     # print("call into _set_name", value, self.name, attribute)
    #     # 不向context中保存未命名实体．
    #     if len(self.ctx) > 0 and (
    #         is_valid_string(value) or is_valid_string(self.name)
    #     ):
    #         from store import Store

    #         inst: Store = Store.instance()
    #         inst.getctx(self.ctx).replace_entity(self.name, value, self)
    #     return value

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


# 由此ProxyEnt替代了EntDict及EntList.保存了dict,list所属的Entity,propname.
@define(slots=True, frozen=False, eq=False)
class ProxyEnt(Entity):
    type: str = field(default="ProxyEnt")
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
