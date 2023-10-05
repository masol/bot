from attrs import define, field
from util.namer import Namer
from util.str import is_valid_string

# from store import Store


@define(slots=True)
class Requirement:
    store: "Store" = field(default=None)
    # 　页面的命名器．
    page_namer: Namer = field(factory=Namer)

    # 这里做提前的变量准备工作．(模型转化)
    def __attrs_post_init__(self):
        print("enter post_init")

    # 在dump前调用，以执行一些初始化动作．例如page_namer.
    def on_before_dump(self):
        model = self.store.models["arch"]
        # 为page_namer设置匿名角色首页．
        anonymous = model.anonymous
        if not anonymous:  # @todo: 未确定默认角色．
            raise ValueError("当前未指定匿名角色．")
        self.page_namer.reserved[model.roles[anonymous].home] = ""
        self.page_namer.suffix = ""

    def get_pages(self):
        model = self.store.models["arch"]
        return model.pages

    def default_role_name(self):
        model = self.store.models["arch"]
        return model.anonymous

    def default_role(self):
        model = self.store.models["arch"]
        return model.roles[model.anonymous].id

    # 工具函数，负责将页面名称转换为文件名．
    def get_pageurl(self, pagename):
        filename = self.page_namer.name(pagename)
        if is_valid_string(self.store.env.subdir):
            url = "/" + self.store.env.subdir
            if is_valid_string(filename):
                if filename[0] == "/":
                    return url + filename
                return url + "/" + filename
            return  url
        return "/" + filename

    def roles(self):
        model = self.store.models["arch"]
        ret = []
        for v in model.roles.values():
            roleinfo = {"id": v.id, "name": v.name, "links": []}
            for pagename in v.nav:
                pageurl = self.get_pageurl(pagename)
                roleinfo["links"].append({"href": pageurl, "name": pagename})
            ret.append(roleinfo)
        return ret
