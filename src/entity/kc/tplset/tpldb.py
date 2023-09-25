from attrs import define, field
import os


@define(slots=True)
class Tplitem:
    # 原始的模板名称．
    tpl_name: str = field(default="")
    # 移除后缀的文件名
    name: str = field(default="")
    # 文件名的后缀
    suffix: str = field(default="")
    # 除了文件名和第一级的usage，中间路径使用.来连接．
    path: str = field(default="")
    # 可以处理的数据类型．可以多个，以字符串分割．
    types: list[str] = field(factory=list)
    features: "dict" = field(factory=dict)


@define(slots=True)
class WeightItem:
    weight: int = field(default=0)
    item: Tplitem = field(default=None)


def weight_sorter(witem: WeightItem):
    return witem.weight


# 位于内存中的模板数据库,用于comps模板集的模板查询与选择．
# 所有组装型模板，第一级目录为usage名(例如comp,skel)．根目录下的模板被放入空名称的usage中．
# 文件名为name(可以重复),后缀为suffix,路径为path(路径分割符被替换为.)
# 特性及特性名由
@define(slots=True)
class Tpldb:
    # 用途分类．
    usage: "dict[str,list[Tplitem]]" = field(factory=dict)

    def add_item(self, tpl_name: str, tpl_obj: "Template"):
        nameparts = tpl_name.split("/")
        usage = ""
        suffix = ""
        path = ""
        name = None
        if len(nameparts) > 1:
            usage = nameparts[0]
            nameparts = nameparts[1:]
        if len(nameparts) > 1:
            name = nameparts.pop()
            path = ".".join(nameparts)
            # nameparts = nameparts[:-1]
        else:
            name = nameparts[0]
        extinfo = os.path.splitext(name)
        name = extinfo[0]
        suffix = extinfo[1]

        if not usage in self.usage.keys():
            self.usage[usage] = []
        types = []
        features = {}
        if "types" in tpl_obj.module.__dict__:
            types = tpl_obj.module.__dict__["types"]
            if not isinstance(types, list):
                types = [types]
        if "features" in tpl_obj.module.__dict__:
            features = tpl_obj.module.__dict__["features"]
            if not isinstance(types, dict):
                features = {}

        self.usage[usage].append(
            Tplitem(
                tpl_name=tpl_name,
                name=name,
                suffix=suffix,
                path=path,
                types=types,
                features=features,
            )
        )

    def item_by_name(self, usage, name):
        items = []
        if usage in self.usage.keys():
            for item in self.usage[usage]:
                if item.name == name:
                    items.append(item)
        return items
