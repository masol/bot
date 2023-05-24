import copy
from gettext import gettext as _

import util.log as logger
from entity.humod import Behave
from entity.humod import Humod, Subj, Subjdtrm, Workflow, Pred, Dataop, Obj
from util.str import is_valid_string

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
                if not objinfo:
                    logger.error(
                        _(
                            "object '%s' reference outside workflow,but can not found it."
                        )
                        % (name)
                    )
                newobj = Obj(name=name, table=objinfo["table"], field=objinfo["field"])
                bh.obj = newobj

    # 将谓语转换为谓语对象．
    def normpred(self, bh: Behave):
        if bh.pred and not isinstance(bh.pred, Pred):
            if not is_valid_string(bh.pred):
                logger.error(_("behave predict '%s' is not a valid string") % (bh.pred))
            name = bh.pred
            newpred = Dataop.mapbasic(name)
            if not isinstance(newpred, Pred):
                # todo: 这是一个复合谓语，开始检索知识库，以确定谓语对象．并赋值给newpred.
                logger.error(_("compound predict not implement: '%s'") % (name))
                pass
            bh.pred = newpred

    def dtrmpred(self, ctx: dict):
        bh = ctx["bh"]
        wf = ctx["wf"]
        self.normpred(bh)
        name = bh.pred.name
        if not is_valid_string(name):
            logger.error(_("behave predict '%s' is not a valid string") % (name))

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
                    logger.warn(
                        _("can not found type define of '%s', assume it's a string")
                        % (obj)
                    )
                    fieldtype = {}
                    fieldtype[obj] = "str"
                else:
                    fieldtype = bh.datas
            self.omodel.dtdfield(
                wf.dtd or wf.name,
                bh.fieldname(ctx["index"]),
                fieldtype,
            )

    def dtrmsubj(
        self,
        ctx: dict[
            "index":int, "notbhcount":int, "bh":Behave, "wf":Workflow, "orig":Workflow
        ],
    ):
        bh = ctx["bh"]
        orig = ctx["orig"]
        wf = ctx["wf"]
        if bh.subj and not isinstance(bh.subj, Subj):
            if not is_valid_string(bh.subj):
                logger.error(_("behave subject '%s' is not a valid string") % (bh.subj))
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
                else:  # 开始寻找上一个宾语的对应字段．
                    bh.subj = Subj(dtrm=Subjdtrm.PREOBJ, name=name)

            print("convert subj to object:", bh.subj)

    def loadwf(self, origwf):
        # 已经加载完毕的流程不再加载．
        if origwf.name in self.omodel.wfs:
            return
        wf = copy.copy(origwf)
        notbhcount = 0
        for index, bh in enumerate(wf.behaves):
            ctx = {
                "index": index,
                "notbhcount": notbhcount,
                "bh": bh,
                "wf": wf,
                "orig": origwf,
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

        for name, wf in self.imodel.wfs.items():
            if not wf.kc:
                self.loadwf(wf)
            # self.humodict.loadWfs(name, wfs)
            pass
        return store
