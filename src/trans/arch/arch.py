from entity.arch import Arch as ArchEntity

from entity.humod import Subjdtrm, Dataop as DataopEnt, Behave as BehaveEnt

from rich import pretty
from ..model import Model
from .util import ArchUtil
from .pred.manage import ManagePred
from .pred.sel import SelPred
from .pred.approve import ApprovePred


class Arch(Model):
    def __init__(self):
        self.imname = "jobduty"
        self.omname = "arch"
        self.ometype = ArchEntity
        pass

    def add_pre_cond(self, bh, api):
        # 默认用户可以通过匿名API访问，因此不添加角色判定．
        if bh.subj.name == self.omodel.anonymous and bh.subj.dtrm == Subjdtrm.ROLE:
            # print("ignore add_pre_cond")
            return
        if bh.subj.dtrm == Subjdtrm.ROLE or bh.subj.dltrm == Subjdtrm.ALLOC:
            api.pre_cond.append(ArchEntity.cond("role", "=", bh.subj.paras["role"]))

    # 返回api名称．
    def ensure_reqrevoke_api(self):
        return ""

    # id: 从哪里获取id: pgroup从当前组有id的祖先组中，name:XXX　从name为XXXX的元素中．空不使用id.
    def ensure_edit_api(self, table, field, bind_fields):
        api_name = ArchUtil.get_apiname(table, field, "u")
        edit_api = self.omodel.ensure_api(api_name)
        edit_api.table = table
        edit_api.fields = field
        edit_api.q_bind["_id?"] = "_id?"
        for fieldname in bind_fields:
            nfname = ArchUtil.normal_fieldname(fieldname)
            edit_api.q_bind[fieldname] = nfname
            edit_api.valid_fields.add(nfname)

        edit_api.q_cond.append(ArchEntity.cond("_id?", "=", "id"))
        # self.add_pre_cond(bh, edit_api)
        return edit_api

    def ensure_del_api(self):
        return ""

    def pred_except(self, arch, duty, page):
        inthumod = self.model("inthumod")
        wf = inthumod.wfs[duty.wfs]
        bh = wf.behaves[duty.bhs]
        print(f"pred exception!!{bh.pred.act}未实现!")

    def proc_pred(self, bh, duty, page):
        pred_dict = {
            DataopEnt.MANAGE: ManagePred.gen,
            DataopEnt.SELONE: SelPred.gen,
            DataopEnt.SELMD: SelPred.genmd,
            DataopEnt.SELMS: SelPred.genms,
            DataopEnt.APPROVE: ApprovePred.gen,
        }
        proc = pred_dict.get(bh.pred.act, self.pred_except)
        return proc(self, duty, page)

    def dotransform(self, store):
        inthumod = self.model("inthumod")
        for rolename, roleinfo in self.imodel.roles.items():
            # 首先遍历，以确定rolehome，home以及navs.
            home_constituency = ""
            for duty in roleinfo.duties:
                wf = inthumod.wfs[duty.wfs]
                bh = wf.behaves[duty.bhs]
                # 获取角色对应的导航．
                pagename = ArchUtil.get_pagename(rolename, wf, duty.bhs)
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

                # 为页面添加所需信息(特殊谓语，添加附加前置行为信息).[是否为列表]
                # 为页面添加行为(Button)及状态．
                # 为页面添加所需导航信息．
                # nav.targets[]
                # print(wf)
                # print(duty)
            # print(rolename, roleinfo)
        # print(self.omodel.pages)
        return store
