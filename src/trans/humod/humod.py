import os
from sklearn.base import TransformerMixin

from entity.humod import Humod as HumodEntity

from .load import load


class Humod(TransformerMixin):
    def __init__(self):
        pass

    def fit(self, store):
        if not store.models.get("humod", None):
            store.models["humod"] = HumodEntity()
            
        return self

    def transform(self, store):
        print("enter humod transformer")
        src = getattr(store.env, "src", None)
        ctx = {
            "base": getattr(store.env, "base", os.getcwd()),
            "verbose": getattr(store.env, "verbose", False),
            # "imodel": src,
            "omodel": store.models["humod"],
            "store": store,
        }
        load(src, ctx)

        return store
