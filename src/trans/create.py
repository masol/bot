from gettext import gettext as _
from sklearn.pipeline import Pipeline

import util.log as logger

from .humod.humod import Humod
from .integrity.integrity import Integrity
from .jobduty.jobduty import JobDuty
from .uipage.uipage import UIpage
from .arch.arch import Arch
from .database.database import Database
from .gql.gql import Gql

def createModel(name: str):
    if name == 'humod':
        return Humod()
    elif name == 'jobduty':
        return JobDuty()
    elif name == 'arch':
        return Arch()
    elif name == 'uipage':
        return UIpage()
    elif name == 'integrity':
        return Integrity()
    elif name == 'database':
        return Database()
    elif name == 'gql':
        return Gql()
    else:
        logger.error(_('Unsupported model "%s" were requested') % name)


def createPipe(models: "list[str]"):
    pipes = []
    for modelname in models:
        pipes.append((modelname, createModel(modelname)))
    return Pipeline(pipes)
