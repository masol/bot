from entity.arch import Arch as ArchEntity
from entity.humod import Obj as ObjEntity

from ..model import Model
from entity.humod import Subjdtrm, Dataop as DataopEnt, Behave as BehaveEnt
from util.str import is_valid_string

from rich import pretty


def get_pagename(rolename, wf, bh_idx):
    return f"{rolename}-{wf.name}-{bh_idx == 0}"


# valid suffx: q: query, u: update/create: d: delete, c: create.
def get_apiname(table, field, suffix):
    return f"{table}-{field}-{suffix}"


def get_showtype(typestr):
    return typestr.split()[0]


def get_edittype(typestr):
    types = typestr.split()
    # print("types", types)
    if len(types) >= 2:
        print(types[1])
    return "Input"

# 将fieldname标准化，移除可能的开头_,$以及结尾?
def normal_fieldname(fieldname):
    if fieldname.startswith('$'):
        fieldname = fieldname[1:]
    
    if fieldname.startswith('-'):
        fieldname = fieldname[1:]

    if fieldname.endswith('?'):
        fieldname = fieldname[:-1]

    return fieldname

class Arch(Model):
    def __init__(self):
        self.imname = "jobduty"
        self.omname = "arch"
        self.ometype = ArchEntity
        pass

    # 将fields信息划分为多级结构．当前实现不分级．
    def clasify_fields(self, fields):
        return fields

    # 根据fields中的名称判定其类型．
    def fill_types(self, field_name, fields):
        type_dict = {"名称": "Title", "图片": "Image", "库存": "Prop Slide"}
        return type_dict.get(field_name, "Desc")

    def get_fields(self, bh):
        inthumod = self.model("inthumod")
        obj = bh.obj
        if isinstance(obj, ObjEntity):
            return inthumod.getdtdfield(obj.table, obj.field)
        return None

    def proc_fields(self, fields, ctx):
        for key, value in fields.items():
            if isinstance(value, dict):
                ctx["multi"] = True
                self.proc_fields(value, ctx)
            elif not is_valid_string(value):
                fields[key] = self.fill_types(key, fields)
            if fields[key] == "Title" and not ctx["key"]:
                ctx["key"] = key

    def normal_fields(self, bh):
        fields = self.get_fields(bh)
        fields = self.clasify_fields(fields)
        ctx = dict()
        ctx["multi"] = False
        ctx["key"] = ""
        self.proc_fields(fields, ctx)
        ctx["fields"] = fields
        return ctx

    def scan_manager_fields(self, fields, block, ctx):
        for key, value in fields.items():
            if isinstance(value, dict):
                self.scan_manager_fields(value, block, ctx)
            elif value == "Title" or value == "Desc":  # 对Title/Desc类型添加搜索．
                ctx["search"].add(key)
            elif value == "Prop":
                ctx["order"].add(key)
            elif value == "Image":
                ctx["imagesearch"].add(key)

    def add_pre_cond(self, bh, api):
        if bh.subj.dtrm == Subjdtrm.ROLE or bh.subj.dltrm == Subjdtrm.ALLOC:
            api.pre_cond.append(ArchEntity.cond("role", "=", bh.subj.paras["role"]))

    # 返回api名称．
    def ensure_reqrevoke_api(self):
        return ""

    # id: 从哪里获取id: pgroup从当前组有id的祖先组中，name:XXX　从name为XXXX的元素中．空不使用id.
    def ensure_edit_api(self, table, field, bind_fields):
        api_name = get_apiname(table, field, "u")
        edit_api = self.omodel.ensure_api(api_name)
        edit_api.table = table
        edit_api.fields = field
        edit_api.q_bind["_id?"] = "_id?"
        for fieldname in bind_fields:
            nfname = normal_fieldname(fieldname)
            edit_api.q_bind[fieldname] = nfname
            edit_api.valid_fields.add(nfname)

        edit_api.q_cond.append(ArchEntity.cond("_id?", "=", "id"))
        # self.add_pre_cond(bh, edit_api)
        return edit_api

    def ensure_del_api(self):
        return ""

    def pred_manage(self, duty, page):
        inthumod = self.model("inthumod")
        wf = inthumod.wfs[duty.wfs]
        bh = wf.behaves[duty.bhs]
        approvebh = None
        for idx in range(len(wf.behaves) - duty.bhs):
            nextbh = wf.behaves[idx + duty.bhs]
            if nextbh.pred.act == DataopEnt.APPROVE:  # 后续有批准动作．
                approvebh = nextbh.obj.field
                break

        # 添加show list page.
        # 获取fieldInfo.
        ctx = self.normal_fields(bh)
        query_apiname = get_apiname(bh.obj.table, bh.obj.field, "q")
        query_api = self.omodel.ensure_api(query_apiname)
        self.add_pre_cond(bh, query_api)
        query_api.table = bh.obj.table
        query_api.fields = bh.obj.field
        query_api.q_cond.append(ArchEntity.cond("visitor", "=", bh.subj.name))
        # 列出全部管理对象的block.
        query_block = page.ensure("Block", api=query_apiname, tirgger=True)
        # 添加fields中对应的管理元素．
        # 需要搜索的field列表．
        ctx["search"] = set()
        # 需要对图像执行相似搜索的列表．暂未实现．
        ctx["imagesearch"] = set()
        # 需要排序的field列表．
        ctx["order"] = set()
        # 支持分组的条件集合列表．暂未实现．考虑加入已批准分类条件．
        ctx["classify"] = []
        self.scan_manager_fields(ctx["fields"], query_block, ctx)
        bindname = query_api.alloc_bind_var()
        orcond = list()
        for search in ctx["search"]:
            orcond.append(ArchEntity.cond(search, "like", bindname))
            query_api.q_bind[bindname] = bindname
            query_api.indexes[search] = "fulltext"
        query_api.q_cond.append(ArchEntity.cond(orcond, "or"))
        # 添加search组件．
        query_block.ensure("Input", param=bindname, cache="session")

        for order in ctx["order"]:
            bindname = query_api.alloc_bind_var()
            query_api.order[order] = bindname
            query_block.ensure("Switch", param=bindname, cache="session")

        # 开始加入卡片．并绑定其变量到返回值字段．其值都为api中的字段名，并附加如下额外变量名: maxpage
        card_block = query_block.ensure("Group", id="id")
        for field, type in ctx["fields"].items():
            card_block.ensure(get_showtype(type), param=field, cache="none")

        edit_but = card_block.ensure("Button", label="编辑", href="page")
        edit_block = edit_but.ensure("Group")
        fields = list()
        for field, type in ctx["fields"].items():
            item_block = edit_block.ensure("Group")
            item_block.ensure("Label", defval=field)
            fieldname = f"${field}"
            fields.append(fieldname)
            item_block.ensure(get_edittype(type), param=fieldname, cache="none")
    
        edit_api = self.ensure_edit_api(bh.obj.table, bh.obj.field, fields)
        self.add_pre_cond(bh, edit_api)
        edit_block.ensure(
            "Button",
            href=edit_api.name,
            label="保存",
        )
        edit_block.ensure("Button", href=f"page://{page.name}", label="返回")

        # @TODO:卡片中添加已批准的分组条件．
        if isinstance(approvebh, BehaveEnt):
            approvefield = f"{approvebh.obj.field}.$审核$"
            query_api.extra_fields.add(approvefield)
            card_block.ensure("Label", param=approvefield, cache="none")

            # 添加条件组-可以撤销．
            condgroup = card_block.ensure("CondGroup", params=(approvefield))
            condgroup.cond.addcond(approvefield, "==", "True")
            condgroup.ensure("Button", label="撤销", href=self.ensure_reqrevoke_api())

            # 添加条件组-可以删除．
            noapprove_condgroup = card_block.ensure("CondGroup", params=(approvefield))
            noapprove_condgroup.cond.addcond(approvefield, "==", "False")
            noapprove_condgroup.ensure("Button", label="删除", href=self.ensure_del_api())
        else:  # 可以直接删除．
            card_block.ensure("Button", label="删除", href=self.ensure_del_api())

        query_block.ensure("Pagination")

        print(pretty.pretty_repr(query_api))
        print(pretty.pretty_repr(page))

        # 添加create button.
        # 添加
        # 添加edit page.
        # print(ctx)
        pass

    def pred_except(self, duty, page):
        print("pred exception!!")
        pass

    def proc_pred(self, bh, duty, page):
        pred_dict = {DataopEnt.MANAGE: self.pred_manage}
        proc = pred_dict.get(bh.pred.act, self.pred_except)
        return proc(duty, page)

    def dotransform(self, store):
        inthumod = self.model("inthumod")
        for rolename, roleinfo in self.imodel.roles.items():
            # 首先遍历，以确定rolehome，home以及navs.
            home_constituency = ""
            for duty in roleinfo.duties:
                wf = inthumod.wfs[duty.wfs]
                bh = wf.behaves[duty.bhs]
                # 获取角色对应的导航．
                pagename = get_pagename(rolename, wf, duty.bhs)
                role = self.omodel.ensure_role(rolename)
                if pagename not in role.nav:
                    role.nav.add(pagename)
                # 计算角色的默认页面，如果可以发起，则为默认页面．
                if duty.bhs == 0:
                    if not home_constituency:
                        home_constituency = pagename
                    # 如果是核心流程．则发起角色为默认角色．
                    if wf.core:
                        self.omodel.anonymous = rolename
                        role.home = pagename
                    elif len(wf.dep) > 0:  # 反之，如果流程有依赖
                        home_constituency = pagename
                        # 如果无流程依赖此流程，优先级最高．
                role.home = home_constituency

                # 获取页面对象．
                page = self.omodel.ensure_page(pagename)
                page.role = rolename

                self.proc_pred(bh, duty, page)

                print()
                # 为页面添加所需信息(特殊谓语，添加附加前置行为信息).[是否为列表]
                # 为页面添加行为(Button)及状态．
                # 为页面添加所需导航信息．
                # nav.targets[]
                # print(wf)
                # print(duty)
            # print(rolename, roleinfo)
        print(self.omodel.pages)
        return store
