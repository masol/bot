from gettext import gettext as _
from rich import pretty
from sklearn.base import TransformerMixin

import util.log as logger
from util.str import is_valid_string


class Model(TransformerMixin):
    def __init__(self):
        self.omname = ""
        self.ometype = None  # 输出模型的Entity类型.
        self.imname = ""

    def dofit(self, store):
        pass

    def fit(self, store):
        if is_valid_string(self.omname):
            if not store.models.get(self.omname, None) and isinstance(
                self.ometype, type
            ):
                store.models[self.omname] = self.ometype()
        if is_valid_string(self.imname) and not store.models.get(
            self.imname, None
        ):
            logger.error(
                _(
                    "Invalid input model [bold green]%s[/bold green] for transformer [bold sky_blue2]%s[/bold sky_blue2]"
                )
                % (self.imname, self.__class__.__name__)
            )
        isverbose = getattr(store.env, "verbose", False)
        if isverbose:
            logger.info(
                _(
                    "[cyan3]Enter[/cyan3] fit of [bold sky_blue2]%s[/bold sky_blue2]"
                )
                % self.__class__.__name__
            )
        self.dofit(store)
        if isverbose:
            logger.info(
                _(
                    "[cyan]Leave[/cyan] fit of [bold sky_blue2]%s[/bold sky_blue2]"
                )
                % self.__class__.__name__
            )
        return self

    def dotransform(self, store):
        pass

    def transform(self, store):
        isverbose = getattr(store.env, "verbose", False)
        dump_models = getattr(store.env, "dump_models", [])
        if isverbose:
            logger.info(
                _(
                    "[cyan3]Enter[/cyan3] transformer of [bold sky_blue2]%s[/bold sky_blue2]"
                )
                % self.__class__.__name__
            )
        self.dotransform(store)
        if is_valid_string(self.omname):
            if 'all' in dump_models or self.omname in dump_models:
                model = store.models.get(self.omname, None)
                if model:
                    logger.info(pretty.pretty_repr(model))
                else:
                    logger.warn(
                        _("output model %s is not valid in %s transformer")
                        % (self.omname, self.__class__.__name__)
                    )
        if isverbose:
            logger.info(
                _(
                    "[cyan]Leave[/cyan] transformer of [bold sky_blue2]%s[/bold sky_blue2]"
                )
                % self.__class__.__name__
            )
        return store
