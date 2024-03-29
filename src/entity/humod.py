from attrs import define, field
from enum import Enum, auto

from entity.entity import Entity
from util.str import md5hash, is_valid_string


class Subjdtrm(Enum):
    invalid = 0
    ROLE = auto()  # 拥有指定角色标志的任意访问者
    WF = auto()  # 工作流程中前置角色相同
    PREOBJ = auto()  # 通过前置行为的宾语关联．
    ALLOC = auto()  # 随机分配一个对应角色．
    MODIF = auto()  # 筛选器，尚未实现．


class Reldtrm(Enum):
    invalid = ""
    HTTP = "http"  # http第三方调用
    FUNCTION = "func"  # 函数调用
    MATH = "math"  # 数学关系
    ROLEREQ = "rolereq"  # 角色请求 # 例如商家角色申请,内建支持几个常用流程
    ROLEGRANT = "rolegrant"  # 角色授权 # 例如给予商家角色,内建支持几个常用流程
    # 类似Dataop，这里只是basic，可以基于流程抽象并组合


# 基础数据操作
# print("%x" % md5hash("AUDITS"))
class Dataop(Enum):
    invalid = 0
    GET = 0x7528035A93EE69CEDB1DBDDB2F0BFCC8  # 获取信息
    PUT = 0x3E75383A5992A6D15FB81E872E46E256  # 提交信息
    SELONE = 0xE300B17B4A4729788A2C3BD920E8E0EC  # 从类集中选择一个
    SELMD = 0x371E624E59DFE59A15B5628286070044  # 从类集中选多个(直接模式),自动将流程拆分为多个流程
    SELMS = 0x902FC3E1087827A338E5C5F403E298F3  # 从类集中选多个(可缓存模式-例如购物车)，自动将流程拆分为多个并行执行．
    MANAGE = 0x92814A387D2FE972E8AA877BC152980C  # 管理信息，要增删改查
    APPROVE = 0xED36B4A24E02A8786F52126DE566CF69  # 审批信息，显示同意，拒绝状态．
    # AUDITS = 0x2e4ce8fca5806f2d66b1241ef0cd74c5  # 审计信息，与审批不同的是，默认同意．
    ACLREQUEST = 0x3AFE20F637B3B9304DADF9AEDA009BA3  # 申请权限．例如申请商家角色．
    # AGGREGATE = 0x361d91ce0f028b6708f607b76b12a318  # 查看汇总信息，宾语为流程，行为名．

    # pred是否映射一个基础操作．
    @staticmethod
    def mapbasic(pred: str):
        switcher = {
            "获取": Pred(act=Dataop.GET, writable=False, outobj=True),
            "查看": Pred(act=Dataop.GET, writable=False, outobj=True),
            # 申请操作为为提交操作，需写入user table.独立出来可以少一个属性．
            "申请": Pred(act=Dataop.ACLREQUEST, writable=True, filedtype="acl"),
            # 将给予权限的操作映射为提交操作．(通过后缀"XX角色"及"XX权限"判断．)
            "提交": Pred(act=Dataop.PUT, writable=True, filedtype="json"),
            "给予": Pred(act=Dataop.PUT, writable=True, filedtype="json"),
            # "给予": Pred(act=Dataop.ACLGRANT, writable=True, filedtype="acl"),
            "单选": Pred(act=Dataop.SELONE, writable=True, filedtype="id", outobj=True),
            "多选": Pred(act=Dataop.SELMD, writable=True, filedtype="array", outobj=True),
            "选择": Pred(act=Dataop.SELMS, writable=True, filedtype="cache", outobj=True),
            "管理": Pred(act=Dataop.MANAGE, writable=True, filedtype="json"),
            "审核": Pred(
                act=Dataop.APPROVE, writable=True, cloning=True, filedtype="bool"
            ),
            # 汇总流程，行为的信息．
            # "汇总": Pred(act=Dataop.AGGREGATE),
        }
        newpred = switcher.get(pred, Dataop.invalid.value)
        if isinstance(newpred, Pred):
            newpred.name = pred
        return newpred


@define(slots=True, frozen=False, eq=False)
class Dtd(Entity):
    type: str = field(default="Dtd")
    fields: "dict[str:any]" = field(factory=dict, metadata={"childtype": dict})
    # 只能手动更新数据．
    const: bool = field(default=False)
    datas: "list[dict]" = field(factory=list, metadata={"childtype": dict})

    # 内部支持的表格名称列表,key为人读名称，value为系统名称．
    @staticmethod
    def buildins() -> dict:
        return {"用户": "user"}

    @staticmethod
    def buildiname(tablename):
        bins = Dtd.buildins()
        if tablename in bins:
            return bins[tablename]
        return ""

    @staticmethod
    def buildincol(tableName: str) -> dict:
        if tableName == "user" or tableName == "用户":
            return {"角色": "role"}

    @staticmethod
    def isbuildin(obj: str):
        return obj in Dtd.buildins().keys()


@define(slots=True, frozen=False, eq=False)
class Adv(Entity):
    class Determine(Enum):
        invalid = 0
        TIMEOUT = auto()  # 超时委托系统自动执行(例如自动取消订单)

    type: str = field(default="Adv")
    dtrm: Determine = field(default=0)
    datas: "dict[str:any]" = field(factory=dict)


@define(slots=True, frozen=False, eq=False)
class Subj(Entity):
    type: str = field(default="Subj")
    # 主语筛选器模式．(buildin: role: 拥有指定角色标志的任意访问者 2. wf: 工作流程中前置角色相同. 3. obj: 通过前置行为的宾语关联．)
    # 通用形式为一个Transformer
    dtrm: Subjdtrm = field(default=Subjdtrm.invalid.value)
    # 为主语筛选器提供的参数．(role: 角色名. wf: 索引的工作流程前置角色. obj: 宾语名. modif: 筛选器)
    paras: "dict[str:str]" = field(factory=dict)
    # 表格名称．
    table: str = field(default="")


@define(slots=True, frozen=False, eq=False)
class Pred(Entity):
    type: str = field(default="Pred")
    # action: 谓语需要执行的数据操作动作
    act: int = field(default=Dataop.invalid.value)
    # 对工作流数据表的操作请求,如果需要写入，则工作流表有一个字段"_bhidx_predname".用于保存这里提交的数据．
    writable: bool = field(default=False)
    # 宾语是否引用外部流程表．
    outobj: bool = field(default=False)
    # 此行为在当前工作流表中维护字段的类型．
    filedtype: any = field(default=None)
    # 此谓语是否需要将宾语对象复制出来．
    cloning: bool = field(default=False)


@define(slots=True, frozen=False, eq=False)
class Obj(Entity):
    type: str = field(default="Obj")
    # 表格名称．空字符串表示当前工作流表．
    table: str = field(default="")
    # 字段名称．
    field: str = field(default="")
    # 需要显示的字段及其transformer名称．(空字符串表示直接显示字段值)
    # trans: "dict[str:str]" = field(factory=dict, metadata={"childtype": dict})
    # 筛选器．
    # modif: "dict[str:str]" = field(factory=dict, metadata={"childtype": dict})


# Concurrent behave.(可并发行为,相同主语的其它可选动作.)
@define(slots=True, frozen=False, eq=False)
class Cncnt(Entity):
    type: str = field(default="Cncnt")
    # 状语:
    adv: str or Adv = field(default="", metadata={"childtype": Adv})
    # 需要执行的动作,与谓语相同
    pred: str or Pred = field(default="", metadata={"childtype": Pred})
    # 宾语
    obj: str or Obj = field(default="", metadata={"childtype": Obj})
    # 如果需要提交信息，这里列出需要提交的信息名称及格式
    datas: "dict[str:any]" = field(factory=dict)
    # -1: 下一行为 >=0 为跳转行为序号
    next: int = field(default=-1)


@define(slots=True, frozen=False, eq=False)
class Behave(Entity):
    type: str = field(default="Behave")
    # 是否是一个行为,系统只与行为交换信息，而动作不交换信息，只辅助人类．
    isBehave: bool = field(default=True)
    # 　完整的一句话，描述行为．
    stm: str = field(default="")
    # 主语
    subj: str or Subj = field(default="", metadata={"childtype": Subj})
    # 状语:
    adv: str or Adv = field(default="", metadata={"childtype": Adv})
    # 谓语
    pred: str or Pred = field(default="", metadata={"childtype": Pred})
    # 宾语
    obj: str or Obj = field(default="", metadata={"childtype": Obj})
    # 如果需要提交信息，这里列出需要提交的信息名称及格式
    datas: "dict[str:any]" = field(factory=dict, metadata={"childtype": dict})
    # -1: 下一行为 -2: 留在此行为 -3: 结束流程 >=0 为跳转行为序号
    next: int = field(default=-1)
    # 相同主语的附加的其它可选动作.(例如审批，当前行为在同一界面同时存在)
    cncnt: "list[Cncnt]" = field(factory=list, metadata={"childtype": Cncnt})

    # 获取field字段自身的字段名称．
    def fieldname(self, index: int) -> str:
        predname = self.pred
        if isinstance(self.pred, Pred):
            predname = self.pred.name
        objname = self.obj
        if isinstance(self.obj, Obj):
            objname = self.obj.name
        return ("_%d_%s_%s") % (index, predname, objname)


@define(slots=True, frozen=False, eq=False)
class Workflow(Entity):
    type: str = field(default="Workflow")
    dtd: str = field(default="")
    # 本流程是否是一个知识库条目．知识库条目只有被依赖时才引入系统．
    kc: bool = field(default=False)
    # 是否将本页面设置为首页(默认页面).当前实现，只检查此标志，如无首页，首页为登录页．
    core: bool = field(default=False)
    behaves: "list[str, Behave]" = field(factory=list, metadata={"childtype": Behave})
    dep: "list[str]" = field(factory=list)

    # 寻找本流程中指定index之前是否有对应主语
    def hasprevsubj(self, name: str, idx: int):
        for index, bh in enumerate(self.behaves):
            if index >= idx:
                break
            subjname = bh.subj
            if isinstance(bh.subj, Subj):
                subjname = bh.subj.name
            if subjname == name:
                return True
        return False

    # 　寻找本流程内，指定index之前的最后一个相同宾语．
    def findprevobj(self, name: str, idx: int):
        retbh = False
        for index, bh in enumerate(self.behaves):
            if index >= idx:
                break
            objname = bh.obj
            if isinstance(bh.obj, Obj):
                objname = bh.obj.name
            if objname == name:
                retbh = bh
        return retbh

    # 本流程表是否包含了指定名词(obj),如果是，返回表名，字段等信息．(返回最后一个)
    def findobj(self, name: str):
        ret = None
        for index, bh in enumerate(self.behaves):
            # 宾语引用了外部表．
            if bh.pred.outobj:
                continue
            objequal = False
            if isinstance(bh.obj, Obj):
                objequal = bh.obj.name == name
            else:
                objequal = bh.obj == name
            if objequal:
                ret = {
                    "table": self.dtd or self.name,
                    "field": bh.fieldname(index),
                }
        return ret

    def tablename(self):
        return self.dtd or self.name


@define(slots=True, frozen=False, eq=False)
class Role(Entity):
    type: str = field(default="Role")
    # 该角色的工作流程


# 直接定义关系通常是不需要的，而是使用流程描述关系。
@define(slots=True, frozen=False, eq=False)
class Relation(Entity):
    type: str = field(default="Relation")
    dtrm: str = field(default=Reldtrm.invalid.value)
    output: str = field(default="")
    input: "list[str]" = field(factory=list, metadata={"childtype": str})


@define(slots=True, frozen=False, eq=False)
class Humod(Entity):
    type: str = field(default="Humod")
    wfs: "dict[str, Workflow]" = field(factory=dict, metadata={"childtype": Workflow})
    dtds: "dict[str, Dtd]" = field(factory=dict, metadata={"childtype": Dtd})
    rls: "dict[str,Relation]" = field(factory=dict, metadata={"childtype": Relation})
    roles: "dict[str, Role]" = field(factory=dict, metadata={"childtype": Role})

    # def __attrs_post_init__(self):
    #     from store import Storew

    #     inst: Store = Store.instance()
    #     ctx = inst.getctx(HUMOD_CTX_NAME)
    #     ctx.add_entity("wfs", self.wfs)
    #     ctx.add_entity("dtds", self.dtds)
    # 获取dtd字段类型
    def getdtdfield(self, tablename: str, fieldname: str):
        if tablename in self.dtds:
            fields = self.dtds[tablename].fields
            if is_valid_string(fieldname):
                if fieldname in fields:
                    return fields[fieldname]
            else:
                return fields
        return None

    # 设置dtd字段类型
    def dtdfield(self, tablename, fieldname, typename):
        if not tablename in self.dtds:
            self.dtds[tablename] = Dtd(name=tablename, fields={fieldname: typename})
        else:
            self.dtds[tablename].fields[fieldname] = typename

    # 设置枚举型字段
    def enumfield(self, tablename, fieldname, enumval):
        if not tablename in self.dtds:
            self.dtds[tablename] = Dtd(name=tablename, fields={fieldname: [enumval]})
        else:
            if fieldname in self.dtds[tablename].fields:
                if enumval not in self.dtds[tablename].fields[fieldname]:
                    self.dtds[tablename].fields[fieldname].append(enumval)
            else:
                self.dtds[tablename].fields[fieldname] = [enumval]

    # 在wfs中查找名词name
    def findobj(self, name: str):
        for wfname, wf in self.wfs.items():
            objinfo = wf.findobj(name)
            if isinstance(objinfo, dict):
                objinfo["wf"] = wf
                objinfo["wfname"] = wf.name
                return objinfo
        return None

    # 在relation中寻找指定输出所对应的relation entity.
    def findrel(self, name: str):
        for rlname, rel in self.rls.items():
            # relation name.
            outputname = rel.output or rel.name
            if outputname == name:
                return rel
        return None
