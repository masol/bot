from entity.arch import Arch as ArchEntity
from entity.humod import Behave as BehaveEnt

from ..util import ArchUtil
from .base import PredBase


class ManagePred(PredBase):
    @staticmethod
    def gen(arch, duty, page):
        inthumod, wf, bh, approvebh, ctx = PredBase.init_vars(arch, duty)
        query_api, query_block = PredBase.create_query_block(bh, page, arch)
        manage_block = PredBase.create_manage_block(ctx, query_api, query_block)
        card_block = PredBase.create_card_block(ctx, query_block)
        edit_block = PredBase.create_edit_block(ctx, card_block, arch, page, bh)
        del_block = PredBase.create_delete_but(approvebh, card_block, arch, query_api)

        query_block.ensure("Pagination")
