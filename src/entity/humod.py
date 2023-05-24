from attrs import define, field
from enum import Enum, auto

from entity.entity import Entity
from util.str import md5hash


class Subjdtrm(Enum):
    invalid = 0
    ROLE = auto()  # 拥有指定角色标志的任意访问者
    WF = auto()  # 工作流程中前置角色相同
    PREOBJ = auto()  # 通过前置行为的宾语关联．
    ALLOC = auto()  # 随机分配一个对应角色．
    MODIF = auto()


# 基础数据操作
class Dataop(Enum):
    invalid = 0
    GET = 0x7528035A93EE69CEDB1DBDDB2F0BFCC8  # 获取信息
    PUT = 0x3E75383A5992A6D15FB81E872E46E256  # 提交信息
    SELONE = 0xE300B17B4A4729788A2C3BD920E8E0EC  # 从类集中选择一个
    SELMD = 0x371E624E59DFE59A15B5628286070044  # 从类集中选多个(直接模式),自动将流程拆分为多个流程
    SELMS = 0x902FC3E1087827A338E5C5F403E298F3  # 从类集中选多个(可缓存模式-例如购物车)，自动将流程拆分为多个并行执行．
    MANAGE = 0x92814A387D2FE972E8AA877BC152980C  # 管理信息，要增删改查
    APPROVE = 0xED36B4A24E02A8786F52126DE566CF69  # 审批信息，显示同意，拒绝状态．

    # pred是否映射一个基础操作．
    @staticmethod
    def mapbasic(pred: str):
        switcher = {
            "获取": Pred(act=Dataop.GET, writable=False, outobj=True),
            "查看": Pred(act=Dataop.GET, writable=False, outobj=True),
            "提交": Pred(act=Dataop.PUT, writable=True, filedtype="json"),
            "单选": Pred(act=Dataop.SELONE, writable=True, filedtype="id", outobj=True),
            "多选": Pred(act=Dataop.SELMD, writable=True, filedtype="array", outobj=True),
            "选择": Pred(act=Dataop.SELMS, writable=True, filedtype="cache", outobj=True),
            "管理": Pred(act=Dataop.MANAGE, writable=True, filedtype="json"),
            "审核": Pred(act=Dataop.APPROVE, writable=True, filedtype="bool"),
        }
        newpred = switcher.get(pred, Dataop.invalid.value)
        if isinstance(newpred, Pred):
            newpred.name = pred
        return newpred


@define(slots=True, frozen=False, eq=False)
class Dtd(Entity):
    type: str = field(default="Dtd")
    fields: "dict[str:any]" = field(factory=dict)


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
    behaves: "list[str, Behave]" = field(factory=list, metadata={"childtype": Behave})

    def hasprevsubj(self, name: str, idx: int):
        for index, bh in enumerate(self.behaves):
            if index >= idx:
                break
            if bh.subj == name:
                return True
        return False

    # 本流程表是否包含了指定名词(obj),如果是，返回表名，字段等信息．
    def findobj(self, name: str):
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
                return {"table": self.dtd or self.name, "field": bh.fieldname(index)}
        return None


@define(slots=True, frozen=False, eq=False)
class Role(Entity):
    type: str = field(default="Role")
    # 该角色的工作流程


@define(slots=True, frozen=False, eq=False)
class Humod(Entity):
    type: str = field(default="Humod")
    wfs: "dict[str, Workflow]" = field(factory=dict, metadata={"childtype": Workflow})
    dtds: "dict[str, Dtd]" = field(factory=dict, metadata={"childtype": Dtd})
    roles: "dict[str, Role]" = field(factory=dict, metadata={"childtype": Role})

    # def __attrs_post_init__(self):
    #     from store import Storew

    #     inst: Store = Store.instance()
    #     ctx = inst.getctx(HUMOD_CTX_NAME)
    #     ctx.add_entity("wfs", self.wfs)
    #     ctx.add_entity("dtds", self.dtds)
    def dtdfield(self, tablename, fieldname, typename):
        if not tablename in self.dtds:
            self.dtds[tablename] = Dtd(name=tablename, fields={fieldname: typename})
        else:
            self.dtds[tablename].fields[fieldname] = typename

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
        for wfname,wf in self.wfs.items():
            objinfo = wf.findobj(name)
            if isinstance(objinfo, dict):
                objinfo["wf"] = wf
                return objinfo
        return None
