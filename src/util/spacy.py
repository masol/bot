import spacy
import xml.etree.cElementTree as ET
from gettext import gettext as _
from singleton.singleton import Singleton

from .log import error

# Path: src/util/spacy.py


def default_model() -> str:
    return "zh_core_web_trf"


def sent_dep(token, xmlnode):
    token_el = ET.SubElement(xmlnode, "token")
    token_el.set("text", token.text)
    token_el.set("lemma", token.lemma_)
    token_el.set("pos", token.pos_)
    token_el.set("tag", token.tag_)
    token_el.set("dep", token.dep_)
    token_el.set("head", str(token.head.i))
    for child in token.children:
        sent_dep(child, token_el)


@Singleton
class Spacy:
    def __init__(self, modelname: str = default_model()):
        self.modelname = modelname
        from simple_spinner.spinner import Spinner

        try:
            with Spinner(desc="load spacy model %s" % (modelname)):
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

    def root(self, doc):
        return [token for token in doc if token.head == token][0]

    def to_xml(self, text):
        doc = self.nlp(text)
        root = ET.Element("sentences")
        for sent in doc.sents:
            sentence_el = ET.SubElement(root, "sentence")
            sent_root = self.root(sent)
            sent_dep(sent_root, sentence_el)
        tree = ET.ElementTree(root)
        return tree
