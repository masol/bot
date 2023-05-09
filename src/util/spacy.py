import os
import spacy
from gettext import gettext as _
from singleton.singleton import Singleton

from .fs import user_data_dir
from .log import warn

# Path: src/util/spacy.py


# 获取spacy的模型目录
def spacy_model_dir() -> str:
    return user_data_dir() + "/spacy_model"


def default_model() -> str:
    return "zh_core_web_trf"


def model_version(modelname: str = default_model()) -> str:
    cache = os.path.join(spacy_model_dir(), modelname)
    if not os.path.exists(cache):
        warn(
            _(
                "model not installed,run [green]python -m spacy download %s[/green] to install"
            )
            % (modelname)
        )
        return ""
    nlp = spacy.load(cache, disable=["parser", "ner"])
    return nlp.meta["version"]


@Singleton
class Spacy:
    def __init__(self, modelname: str = default_model()):
        self.modelname = modelname
        self.cachepath = os.path.join(spacy_model_dir(), modelname)
        if not os.path.exists(self.cachepath):
            self.nlp = spacy.load(modelname)
            os.makedirs(self.cachepath)
            self.nlp.to_disk(self.cachepath)
        else:
            self.nlp = spacy.load(self.cachepath)

    def __call__(self, text: str):
        return self.nlp(text)

    def __repr__(self):
        return self.modelname
