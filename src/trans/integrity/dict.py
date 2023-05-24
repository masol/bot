import xml.etree.ElementTree as ET

from util.spacy import Spacy


class HumodDict:
    """Dictionary for Humod."""

    def __init__(self):
        """Initialize HumodDict."""
        self._dict = {}

    def loadWfs(self, name, wfs):
        spacy = Spacy.instance()
        print(spacy(name))
        for bh in wfs.behaves:
            print(bh)
            if bh.subj:
                root = spacy.to_xml(bh.subj)
                # xml_string = ET.tostring(root).decode('utf-8')
                # print(xml_string)
                ET.dump(root)
                doc = spacy(bh.subj)
                root = spacy.root(doc)
                print("root=%s", root)
                for child in root.children:
                    print("child=%s", child.text, child.pos_, child.dep_)
                for token in doc:
                    print(token.text, token.dep_)
        print(name)
        print(wfs)
        pass

    # 从humod中加载字典．
    def load(self, humod):
        """Load humod."""
        for name, wfs in humod.wfs.items():
            self.loadWfs(name, wfs)
        self._dict = humod
