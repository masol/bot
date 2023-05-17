from gettext import gettext as _

import util.log as logger
from entity.humod import Humod as Humod

from ..model import Model
from .dict import HumodDict


class Integrity(Model):
    def __init__(self):
        self.imname = "humod"
        self.omname = "humod"
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
        
        self.humodict = HumodDict()
        self.humodict.load(imodel)

    def dotransform(self, store):
        return store
