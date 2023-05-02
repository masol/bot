from entity.uipage import UIpage as UIpageEntity

from ..model import Model


class UIpage(Model):
    def __init__(self):
        self.imname = 'jobduty'
        self.omname = 'uipage'
        self.ometype = UIpageEntity
        pass

    def dotransform(self, store):
        return store
