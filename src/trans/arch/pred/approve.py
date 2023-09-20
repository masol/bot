from ..util import ArchUtil

from .base import PredBase


class ApprovePred(PredBase):
    @staticmethod
    def gen(arch, duty, page):
        inthumod, wf, bh, approvebh, ctx = PredBase.init_vars(arch, duty)
        query_api, query_block = PredBase.create_query_wf(wf, bh, page, arch)
        pass
