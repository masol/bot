from attrs import define, field

from . import entity


@define(slots=True)
class Env(entity.Entity):
    src: str = ""
    type = "Env"
    verbose: bool = field(default=False)
    debug: bool = field(default=False)
    dump_models: list = field(factory=list)
    log: str = field(default="log")
    loglevel: str = field(default="info")
    logformat: str = field(default="%(asctime)s %(levelname)s %(message)s")
    logdatefmt: str = field(default="%Y-%m-%d %H:%M:%S")
    logfilename: str = field(default="log.txt")
    logutc: bool = field(default=True)
    tolerant: bool = field(default=False)
    output_dir: str = field(default="target")
