from ..util import ArchUtil

from .base import PredBase


class SelPred(PredBase):
    # genmod = "": 单选模式．
    # genmod = "MD": 多选谓词．
    # genmod = "MS": 选择谓词．可能单选一个，可能多个，也可以加入购物车(缓冲),需要更灵活的按钮集．
    @staticmethod
    def gen_impl(arch, duty, page, genmode=""):
        inthumod, wf, bh, approvebh, ctx = PredBase.init_vars(arch, duty)
        query_api, query_block = PredBase.create_query_block(bh, page, arch)
        manage_block = PredBase.create_manage_block(ctx, query_api, query_block)
        card_block = PredBase.create_card_block(ctx, query_block)
        # 创建选择按钮．
        if genmode == "MD":
            print("NOT IMPLEMENT")
        elif genmode == "MS":
            print("NOT IMPLEMENT")
        else:
            PredBase.create_sel_one(ctx, card_block, arch, page, wf, bh)

        query_block.ensure("Pagination")

    @staticmethod
    def gen(arch, duty, page):
        return SelPred.gen_impl(arch, duty, page)

    @staticmethod
    def genmd(arch, duty, page):
        return SelPred.gen_impl(arch, duty, page, "MD")

    @staticmethod
    def genms(arch, duty, page):
        return SelPred.gen_impl(arch, duty, page, "MS")
