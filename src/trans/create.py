from .humod.humod import Humod
from .jobduty.jobduty import JobDuty
from .uipage.uipage import UIpage
from .integrity.integrity import Integrity
from sklearn.pipeline import Pipeline
from gettext import gettext as _
import util.log as logger

def createModel(name: str):
    if name == 'humod':
        return Humod()
    elif name == 'jobduty':
        return JobDuty()
    elif name == 'uipage':
        return UIpage()
    elif name == 'integrity':
        return Integrity()
    else:
        logger.error(_('Unsupported model "%s" were requested') % name)
    
def createPipe(models: list[str]):
    pipes = []
    for modelname in models:
        pipes.append((modelname, createModel(modelname)))
    return Pipeline(pipes)
