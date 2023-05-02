from entity.humod import Humod as Humod

from ..model import Model


class Integrity(Model):
    def __init__(self):
        self.imname = "humod"
        self.omname = "humod"
        pass

    def dofit(self, store):
        # 从store.env中获取配置信息．
        pass

    def dotransform(self, store):
        return store
