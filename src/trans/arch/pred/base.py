from entity.arch import Arch as ArchEntity
from entity.humod import Behave as BehaveEnt, Subjdtrm

from ..util import ArchUtil


class PredBase:
    # 根据bh的方式，来添加额外的api条件．
    @staticmethod
    def add_cond_forsubj(bh, api):
        if bh.subj.dtrm == Subjdtrm.ALLOC:
            api.q_cond.append(ArchEntity.cond("alloc", "=", bh.subj.name))
        elif bh.subj.dtrm == Subjdtrm.PREOBJ:
            api.q_cond.append(ArchEntity.cond("preobj", "=", bh.subj.paras))

    @staticmethod
    def search_from_fields(fields, block, ctx):
        for key, value in fields.items():
            if isinstance(value, dict):
                ArchUtil.search_from_fields(value, block, ctx)
            elif value == "Title" or value == "Desc":  # 对Title/Desc类型添加搜索．
                ctx.search.add(key)
            elif value == "Prop":
                ctx.order.add(key)
            elif value == "Image":
                ctx.imagesearch.add(key)

    @staticmethod
    def init_vars(arch, duty):
        inthumod = arch.model("inthumod")
        wf = inthumod.wfs[duty.wfs]
        bh = wf.behaves[duty.bhs]
        approvebh = ArchUtil.get_approve_bh(wf, duty.bhs)
        # 添加show list page.
        # 获取fieldInfo.
        ctx = ArchUtil.create_fields_ctx(arch, wf, duty)
        return inthumod, wf, bh, approvebh, ctx

    # 添加查询自身表格的api和block.
    @staticmethod
    def create_query_wf(wf, bh, page, arch):
        tablename = wf.tablename()
        fieldname = ArchUtil.getbhfieldname(wf, bh)
        fieldname = bh.obj.field
        # print("fieldname for query=", bh.subj)
        query_apiname = ArchUtil.get_apiname(tablename, fieldname, "q")
        query_api = arch.omodel.ensure_api(query_apiname)
        query_api.table = tablename
        query_api.fields = fieldname
        query_api.extra_fields = bh.obj.field
        PredBase.add_cond_forsubj(bh, query_api)
        query_block = page.ensure("Block", api=query_apiname, tirgger=True)
        return query_api, query_block

    # 添加查询宾语的api和block.
    @staticmethod
    def create_query_block(bh, page, arch):
        query_apiname = ArchUtil.get_apiname(bh.obj.table, bh.obj.field, "q")
        query_api = arch.omodel.ensure_api(query_apiname)
        arch.add_pre_cond(bh, query_api)
        query_api.table = bh.obj.table
        query_api.fields = bh.obj.field
        query_api.q_cond.append(ArchEntity.cond("visitor", "=", bh.subj.name))
        # 列出全部管理对象的block.
        query_block = page.ensure("Block", api=query_apiname, tirgger=True)
        return query_api, query_block

    @staticmethod
    def create_manage_block(ctx, query_api, query_block):
        # 添加fields中对应的管理元素．
        PredBase.search_from_fields(ctx.fields, query_block, ctx)
        bindname = query_api.alloc_bind_var()
        orcond = list()
        for search in ctx.search:
            orcond.append(ArchEntity.cond(search, "like", bindname))
            query_api.q_bind[bindname] = bindname
            query_api.indexes[search] = "fulltext"
        query_api.q_cond.append(ArchEntity.cond(orcond, "or"))
        # 添加操作导航
        manage_block = query_block.ensure("Group", hints="manage")
        # 添加search组件．
        manage_block.ensure("Input", param=bindname, hints="search", cache="session")

        if len(ctx.order) > 0:
            order_group = manage_block.ensure("Group", hints="order")
            for order in ctx.order:
                bindname = query_api.alloc_bind_var()
                query_api.order[order] = bindname
                order_group.ensure(
                    "Switch", param=bindname, hints="order", cache="session"
                )

        return manage_block

    @staticmethod
    def create_card_block(ctx, parent_block):
        # 开始加入卡片．并绑定其变量到返回值字段．其值都为api中的字段名，并附加如下额外变量名: maxpage
        card_block = parent_block.ensure("Group", hints="card", id="id")
        # print("ctx[fields]=",ctx["fields"])
        for field, type in ctx.fields.items():
            card_block.ensure(
                ArchUtil.get_showtype(type), label=field, param=field, cache="none"
            )
        return card_block

    @staticmethod
    def create_edit_block(ctx, parent_block, arch, page, bh):
        edit_but = parent_block.ensure("Button", hints="edit", label="编辑", href="")
        edit_block = edit_but.ensure("Group", hints="edit")
        # 为edit api提供可能的field列表．
        fields = list()
        for field, type in ctx.fields.items():
            fieldname = f"${field}"
            fields.append(fieldname)
            edit_block.ensure(
                ArchUtil.get_edittype(type),
                label=field,
                defval=field,  # todo: generate default value.
                param=fieldname,
                cache="none",
            )

        edit_api = arch.ensure_edit_api(bh.obj.table, bh.obj.field, fields)
        arch.add_pre_cond(bh, edit_api)
        edit_block.ensure(
            "Button",
            href=edit_api.name,
            label="保存",
        )
        edit_block.ensure("Button", href=f"page://{page.name}", label="返回")
        return edit_block

    # 根据是否有后续审批，来决定如何显示删除按钮．
    @staticmethod
    def create_delete_but(approvebh, card_block, arch, query_api):
        # @TODO:卡片中添加已批准的分组条件．
        if isinstance(approvebh, BehaveEnt):
            approvefield = f"{approvebh.obj.field}.$审核$"
            query_api.extra_fields.add(approvefield)
            card_block.ensure("Label", param=approvefield, cache="none")

            # 添加条件组-可以撤销．
            condgroup = card_block.ensure("CondGroup", params=(approvefield))
            condgroup.cond.addcond(approvefield, "==", "True")
            condgroup.ensure("Button", label="撤销", href=arch.ensure_reqrevoke_api())

            # 添加条件组-可以删除．
            noapprove_condgroup = card_block.ensure("CondGroup", params=(approvefield))
            noapprove_condgroup.cond.addcond(approvefield, "==", "False")
            noapprove_condgroup.ensure("Button", label="删除", href=arch.ensure_del_api())
        else:  # 可以直接删除．
            card_block.ensure("Button", label="删除", href=arch.ensure_del_api())

    @staticmethod
    def create_sel_one(ctx, parent_block, arch, page, wf, bh):
        # inthumod = arch.model("inthumod")
        tablename = wf.tablename()
        fieldname = ArchUtil.getbhfieldname(wf, bh)
        # 获取自身要保存的变量．
        # field_val = inthumod.getdtdfield(tablename, fieldname)
        fields = list()
        # print("field_val=", field_val)
        sel_api = arch.ensure_edit_api(tablename, fieldname, fields)
        parent_block.ensure("Button", href=sel_api, label="选择")

    @staticmethod
    def create_approve(ctx, parent_block, arch, page, wf, bh):
        # inthumod = arch.model("inthumod")
        tablename = wf.tablename()
        fieldname = ArchUtil.getbhfieldname(wf, bh)
        # 获取自身要保存的变量．
        # field_val = inthumod.getdtdfield(tablename, fieldname)
        fields = list()
        # print("field_val=", field_val)
        sel_api = arch.ensure_edit_api(tablename, fieldname, fields)
        parent_block.ensure("Button", href=sel_api, label="审核")


    @staticmethod
    def create_get(ctx, parent_block, arch, page, wf, bh):
        # inthumod = arch.model("inthumod")
        tablename = wf.tablename()
        fieldname = ArchUtil.getbhfieldname(wf, bh)
        # 获取自身要保存的变量．
        # field_val = inthumod.getdtdfield(tablename, fieldname)
        fields = list()
        # print("field_val=", field_val)
        sel_api = arch.ensure_edit_api(tablename, fieldname, fields)
        parent_block.ensure("Button", href=sel_api, label="确认")

        
    @staticmethod
    def create_put(ctx, parent_block, arch, page, wf, bh):
        # inthumod = arch.model("inthumod")
        tablename = wf.tablename()
        fieldname = ArchUtil.getbhfieldname(wf, bh)
        # 获取自身要保存的变量．
        # field_val = inthumod.getdtdfield(tablename, fieldname)
        fields = list()
        # print("field_val=", field_val)
        sel_api = arch.ensure_edit_api(tablename, fieldname, fields)
        parent_block.ensure("Button", href=sel_api, label="输入")

