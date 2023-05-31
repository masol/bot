import copy
from gettext import gettext as _

import util.log as logger
from entity.humod import (
    Behave,
    Dataop,
    Humod,
    Obj,
    Pred,
    Subj,
    Subjdtrm,
    Workflow,
)
from store import Store
from util.str import is_valid_string, md5hash

from ..model import Model

# from .dict import HumodDict


class Integrity(Model):
    def __init__(self):
        self.imname = "humod"
        self.omname = "inthumod"
        self.ometype = Humod
        pass

    def dofit(self, store):
        imodel = self.imodel
        if not imodel or not isinstance(imodel, Humod):
            logger.error(
                _(
                    "Invalid input model [bold green]%s[/bold green] for transformer [bold sky_blue2]%s[/bold sky_blue2]"
                )
                % (self.imname, self.__class__.__name__)
            )
            return store

        print("%x" % md5hash("ACLGRANT"))
        # self.humodict = HumodDict()
        # self.humodict.load(imodel)

    def dtrmobj(self, ctx: dict):
        bh = ctx["bh"]
        wf = ctx["wf"]
        if bh.obj and not isinstance(bh.obj, Obj):
            if not is_valid_string(bh.obj):
                logger.error(
                    _("behave objection '%s' is not a valid string") % (bh.obj)
                )
            name = bh.obj
            # 此宾语引用外部流程表.
            if bh.pred.outobj:
                objinfo = self.imodel.findobj(name)
                if objinfo:
                    # 为方便后续wfcache，这里需要提前处理obj所属工作流
                    depwf = objinfo["wf"]
                    self.loadwf(depwf)
                    # 将dep加入本流程。
                    wf.dep.append(objinfo["wfname"])
                else:
                    # todo: 收集全部relation,rel为数组，而不是一个rel
                    rel = self.imodel.findrel(name)
                    if not rel:
                        logger.error(
                            _(
                                "object '%s' reference outside workflow,but can not found it."
                            )
                            % (name)
                        )
                    notdtrm = ""
                    for input in rel.input:
                        objinfo = self.imodel.findobj(input)
                        if not objinfo:
                            notdtrm = input
                            break
                    if notdtrm:
                        logger.error(
                            _(
                                "can not determine object '%s', input '%s' in relation '%s' can not determine."
                            )
                            % (name, input, rel.name)
                        )
                newobj = Obj(
                    name=name, table=objinfo["table"], field=objinfo["field"]
                )
                bh.obj = newobj

    # 将谓语转换为谓语对象．
    def normpred(self, bh: Behave):
        if bh.pred and not isinstance(bh.pred, Pred):
            if not is_valid_string(bh.pred):
                logger.error(
                    _("behave predict '%s' is not a valid string") % (bh.pred)
                )
            name = bh.pred
            newpred = Dataop.mapbasic(name)
            if not isinstance(newpred, Pred):
                # todo: 这是一个复合谓语，开始检索知识库，以确定谓语对象．并赋值给newpred.
                logger.error(
                    _("compound predict not implement: '%s'") % (name)
                )
                pass
            bh.pred = newpred

    def dtrmpred(self, ctx: dict):
        bh = ctx["bh"]
        wf = ctx["wf"]
        wfcache = ctx["wfcache"]
        self.normpred(bh)
        name = bh.pred.name
        if not is_valid_string(name):
            logger.error(
                _("behave predict '%s' is not a valid string") % (name)
            )

        pred = bh.pred
        # todo: 处理状语．以确定执行时机.
        if pred.writable and pred.filedtype:
            obj = ""
            if is_valid_string(bh.obj):
                obj = bh.obj
            fieldtype = pred.filedtype
            if pred.filedtype == "json":
                if not bh.datas:
                    # todo: 这里检索知识库，以确定dict.
                    Store.instance().env.warn(
                        "a001",
                        _(
                            "Cannot precisely deduce the type of '%s' in workflow '%s'."
                        )
                        % (obj, wf.name),
                        _("Assuming it is an object containing a string"),
                    )
                    fieldtype = {}
                    fieldtype[obj] = "str"
                else:
                    fieldtype = bh.datas
            elif pred.outobj:
                # @todo: 将这里与上面dtrmobj中的获取obj代码合并
                objname = bh.obj
                if isinstance(bh.obj, Obj):
                    objname = bh.obj.name
                objinfo = self.imodel.findobj(objname)
                if not objinfo:
                    logger.warn(
                        _(
                            "object '%s' reference outside workflow,but can not found it."
                        )
                        % (name)
                    )
                else:
                    wfcache[bh.fieldname(ctx["index"])] = objinfo["table"]
                    fieldtype = "$%s:%s.%s" % (
                        fieldtype,
                        objinfo["table"],
                        objinfo["field"],
                    )
                pass
            self.omodel.dtdfield(
                wf.dtd or wf.name,
                bh.fieldname(ctx["index"]),
                fieldtype,
            )

    def dtrmsubj(
        self,
        ctx: """dict[
            "index":int, "notbhcount":int, "bh":Behave, "wf":Workflow, "orig":Workflow
        ]""",
    ):
        bh = ctx["bh"]
        orig = ctx["orig"]
        wf = ctx["wf"]
        wfcache = ctx["wfcache"]
        if bh.subj and not isinstance(bh.subj, Subj):
            if not is_valid_string(bh.subj):
                logger.error(
                    _("behave subject '%s' is not a valid string") % (bh.subj)
                )
            name = bh.subj
            if ctx["index"] - ctx["notbhcount"] == 0:
                bh.subj = Subj(dtrm=Subjdtrm.ROLE, name=name)
                bh.subj.paras["role"] = name
                self.omodel.enumfield("user", "role", name)
                self.omodel.dtdfield(wf.dtd or wf.name, name, "user")
                bh.subj.table = "user"
                # todo: 处理定语．例如拥有蓝标的买家．
            else:  # 不是第一个行为．
                if orig.hasprevsubj(name, ctx["index"]):
                    bh.subj = Subj(dtrm=Subjdtrm.WF, name=name)
                    bh.subj.paras["role"] = name
                    bh.subj.table = orig.name
                else:
                    # @todo: 开始寻找上一个宾语的对应字段．
                    for key, value in wfcache.items():
                        dtd = self.omodel.dtds.get(value, None)
                        if dtd and name in dtd.fields:
                            bh.subj = Subj(
                                dtrm=Subjdtrm.PREOBJ,
                                name=name,
                                paras={
                                    "self": key,
                                    "field": name,
                                    "table": value,
                                },
                            )
                            break
                    if not isinstance(bh.subj, Subj):
                        bh.subj = Subj(dtrm=Subjdtrm.ALLOC, name=name)
                        self.omodel.enumfield("user", "role", name)

            # print("convert subj to object:", bh.subj)

    def loadwf(self, origwf):
        # 已经加载完毕的流程不再加载．
        if origwf.name in self.omodel.wfs:
            return
        wf = copy.copy(origwf)
        # 缓冲可以索引的外部表格及本表字段,key为本表字段，value为索引表格
        wfcache = {}
        notbhcount = 0
        for index, bh in enumerate(wf.behaves):
            ctx = {
                "index": index,
                "notbhcount": notbhcount,
                "bh": bh,
                "wf": wf,
                "orig": origwf,
                "wfcache": wfcache,
            }
            if not bh.isBehave:
                notbhcount += 1
                continue
            self.dtrmsubj(ctx)
            self.dtrmpred(ctx)
            self.dtrmobj(ctx)
        self.omodel.wfs[wf.name] = wf

    def dotransform(self, store):
        for name, wf in self.imodel.wfs.items():
            for index, bh in enumerate(wf.behaves):
                self.normpred(bh)

        self.omodel.rls = copy.copy(self.imodel.rls)
        self.omodel.dtds = copy.copy(self.imodel.dtds)
        for name, wf in self.imodel.wfs.items():
            if not wf.kc:
                self.loadwf(wf)
            # self.humodict.loadWfs(name, wfs)
            pass
        return store
