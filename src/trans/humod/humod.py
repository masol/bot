import os

from ..model import Model
from rich import pretty
from sklearn.base import TransformerMixin

import util.log as logger

from entity.humod import Humod as HumodEntity
from .load import load


class Humod(Model):
    def __init__(self):
        self.omname = "humod"
        self.imname = ''
        self.ometype = HumodEntity

    def dotransform(self, store):
        src = getattr(store.env, "src", None)
        ctx = {
            "base": getattr(store.env, "base", os.getcwd()),
            "verbose": getattr(store.env, "verbose", False),
            # "imodel": src,
            "omodel": store.models["humod"],
            "store": store,
        }
        load(src, ctx)

