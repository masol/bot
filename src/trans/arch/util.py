from attrs import define, field
from entity.entity import Entity
from entity.humod import Obj as ObjEntity, Dataop as DataopEnt, Behave as BehaveEnt
from util.str import is_valid_string


# 创建页面时,相关fields的上下文．在create_fields_ctx时创建．
@define(slots=True, frozen=False, eq=False)
class FieldsCtx(Entity):
    # fields是否为多级结构．
    multi: bool = field(default=False)
    # 是否与上一行为人相同．
    same_vistor: bool = field(default=False)
    # fields中的主键名称．
    key: str = field(default="")
    # 保存了fields.
    fields: dict = field(factory=dict)
    # 保存了需要搜索的字段．
    search: set = field(factory=set)
    # 需要对图像执行相似搜索的列表．暂未实现．
    imagesearch: set = field(factory=set)
    # 需要排序的字段集合．
    order: set = field(factory=set)
    # 支持分组的条件集合列表．暂未实现．考虑加入已批准分类条件．
    classify: list = field(factory=list)


class ArchUtil:
    @staticmethod
    def get_pagename(rolename, wf, bh_idx):
        return f"{rolename}-{wf.name}-{bh_idx == 0}"

    # valid suffx: q: query, u: update/create: d: delete, c: create.
    @staticmethod
    def get_apiname(table, field, suffix):
        return f"{table}-{field}-{suffix}"

    @staticmethod
    def get_showtype(typestr):
        return typestr.split()[0]

    @staticmethod
    def get_edittype(typestr):
        types = typestr.split()
        # print("types", types)
        if len(types) >= 2:
            return types[1]
        return "Input"

    # 将fieldname标准化，移除可能的开头_,$以及结尾?
    @staticmethod
    def normal_fieldname(fieldname):
        if fieldname.startswith("$"):
            fieldname = fieldname[1:]

        if fieldname.startswith("-"):
            fieldname = fieldname[1:]

        if fieldname.endswith("?"):
            fieldname = fieldname[:-1]

        return fieldname

    @staticmethod
    # 将fields信息划分为多级结构．当前实现不分级．
    def clasify_fields(fields):
        return fields

    # 根据fields中的名称判定其类型．
    @staticmethod
    def fill_types(field_name, fields):
        # print("fill_types=", field_name, fields)
        type_dict = {"名称": "Title", "图片": "Image", "库存": "Prop Slide"}
        return type_dict.get(field_name, "Desc")

    @staticmethod
    def get_fields(arch, bh):
        inthumod = arch.model("inthumod")
        obj = bh.obj
        if isinstance(obj, ObjEntity):
            return inthumod.getdtdfield(obj.table, obj.field)
        return None

    # 返回True,删除本内部字段．如果需要对其变幻，需在这里处理．
    @staticmethod
    def is_rm_field(key, value, ctx):
        return True
    
    # 返回bh对应的field名称．
    @staticmethod
        # 获取行为对应的字段(内部调用bh.fieldname)．如果不存在，返回None. idx为bh所处的索引．
    def getbhfieldname(wf: "Workflow", bh: "Behave"):
        idx = 0
        for b in wf.behaves:
            if b == bh:
                break
            idx += 1
        if idx >= len(wf.behaves):
            raise Exception("Behave not in your workflow!!")
            # return None
        return bh.fieldname(idx)


    # 对需要处理的fields做处理，
    # 1. 补齐类型．
    # 2. 条件式移除内建变量($XXX$)格式．
    @staticmethod
    def proc_fields(fields, ctx):
        removed_keys = set()
        for key, value in fields.items():
            if key.startswith("$") and key.endswith("$"):
                if ArchUtil.is_rm_field(key, value, ctx):
                    removed_keys.add(key)
            if isinstance(value, dict):
                ctx.multi = True
                ArchUtil.proc_fields(value, ctx)
            elif not is_valid_string(value):
                fields[key] = ArchUtil.fill_types(key, fields)
            if fields[key] == "Title" and not is_valid_string(ctx.key):
                ctx.key = key

        for rm_key in removed_keys:
            # del fields[rm_key]
            fields.pop(rm_key, None)

    @staticmethod
    def create_fields_ctx(arch, wf, duty):
        bh = wf.behaves[duty.bhs]
        fields = ArchUtil.get_fields(arch, bh)
        fields = ArchUtil.clasify_fields(fields)
        ctx = FieldsCtx()
        ArchUtil.proc_fields(fields, ctx)
        ctx.fields = fields
        if duty.bhs > 0:
            prebh = wf.behaves[duty.bhs - 1]
            # ctx["same_vistor"]保存了与上一行为是否为相同的访问者．
            ctx.same_vistor = prebh.subj.name = bh.subj.name
        # else:
        #     ctx.same_vistor = False

        return ctx

    # 返回指定的流程制定动作序列(0基)的后续批准动作对象,如果没有，返回None.
    # @param cur_idx: 检查此动作的后续动作(包含此动作)，默认为0.
    @staticmethod
    def get_approve_bh(wf, cur_idx) -> "BehaveEnt":
        approvebh = None
        for idx in range(len(wf.behaves) - cur_idx):
            nextbh = wf.behaves[idx + cur_idx]
            if nextbh.pred.act == DataopEnt.APPROVE:  # 后续有批准动作．
                approvebh = nextbh.obj.field
                break
        return approvebh
