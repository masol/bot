from attrs import define, field
from .tplset import Tplset
from .tpldb import Tpldb, WeightItem, weight_sorter
from util.dict import intersection


# Tplcomp不同于Tplset，它是一个组件集，用于渲染组件．因此通常不会调用dump_all等方法．
# 提供了加载时获取组件特性，并构建内存数据库以供查询．
# 组件的key默认为模板名称，可以通过设置key来修改．
# 组件的特性，可以通过feature来修改．注意,feature是一个列表，可以有多个特性．
@define(slots=True)
class Tplcomp(Tplset):
    db: Tpldb = field(factory=Tpldb)

    def load(self, req, res, basedir):
        super().load(req, res, basedir)
        # 扫描以初始化组件的内存数据库．
        templates = self.list_templates()
        for tpl_name in templates:
            tpl_obj = self._get_template(tpl_name)
            self.db.add_item(tpl_name, tpl_obj)
        # print(self.db)

    def by_name(self, usage, name):
        items = self.db.item_by_name(usage, name)
        if len(items) > 0:
            return items[0].tpl_name
        return None

    # 查找特定特性的模板．其中name必须满足．
    def match_feature(self, usage: str, name: str, features: "dict[str,str]"):
        # 列出所有可能的feature名．
        items = self.db.usage[usage]
        weight_items: list[WeightItem] = list()
        for dbitem in items:
            if dbitem.name == name or dbitem.path == name:
                item = WeightItem(item=dbitem)
                item.weight = len(intersection(dbitem.features, features))
                weight_items.append(item)
        count = len(weight_items)
        if count == 1:
            return weight_items[0].item.tpl_name
        elif count == 0:
            return None
        weight_items.sort(reverse=True, key=weight_sorter)
        return weight_items[0].item.tpl_name
