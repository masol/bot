from ..util import ArchUtil

from .base import PredBase


class PutPred(PredBase):
    @staticmethod
    def gen(arch, duty, page):
        inthumod, wf, bh, approvebh, ctx = PredBase.init_vars(arch, duty)
        query_api, query_block = PredBase.create_query_wf(wf, bh, page, arch)
        PredBase.create_manage_block(ctx, query_api, query_block)
        # @TODO: 这里需要为init_vars添加一个参数，用于指定是哪个fields．
        card_block = PredBase.create_card_block(ctx, query_block)
        approve_block = PredBase.create_get(ctx, card_block, arch, page, wf, bh)
        query_block.ensure("Pagination")
