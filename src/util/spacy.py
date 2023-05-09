import os
import spacy
from gettext import gettext as _
from singleton.singleton import Singleton

from .log import error

# Path: src/util/spacy.py


def default_model() -> str:
    return "zh_core_web_trf"


@Singleton
class Spacy:
    def __init__(self, modelname: str = default_model()):
        self.modelname = modelname
        try:
            # self.nlp = spacy.load(modelname, disable=["parser", "ner"])
            self.nlp = spacy.load(modelname)
        except:
            error(
                _(
                    "model not installed,run [green]python -m spacy download %s[/green] to install"
                )
                % (modelname)
            )

    def __call__(self, text: str):
        return self.nlp(text)

    def model_version(self) -> str:
        return self.nlp.meta["version"]

    def __repr__(self):
        return self.modelname
