from attrs import define, field
from entity import entity
from jinja2 import Environment, FileSystemLoader, Template
from jinja2.meta import find_undeclared_variables
from entity.env import Env
from util.str import is_valid_string
from util.namer import Namer
from datetime import datetime
from rich import pretty
from os import path


from .constpl.gotopage import GOTO_PAGE_TPL
from .constpl.layout import DEF_LAYOUT
from .blkrender import render_block
from .tpl import Tplbase

PAGE_SVELTE = "+page.svelte"


@define(slots=True)
class GenpageCtx:
    files: dict = field(factory=dict)
    page: "Page" = field(default=None)
    vars: dict = field(factory=dict)
    store: "Store" = field(default=None)
    path: "list[Block]" = field(factory=list)
    svelte: "Svelte" = field(default=None)


# 部分依赖变量需要其它部分，因此一个输出会被延迟．需要使用asyncio.coroutine来简化依赖处理．
@define(slots=True)
class DelayedTpl(entity.Entity):
    outpath: str = field(default="")
    # 模板对象．
    template = field(default=None)
    # 渲染模式，目前只支持page.
    mode: str = field(default="")
    render_vas: dict = field(default=None)
    delayed_vars: dict = field(default=None)


# 做为svelte的实现．当前尚未实现客户端知识库加载．
@define(slots=True)
class Svelte(entity.Entity):
    # 页面的loader及模板环境
    page_tpl: "Tplbase" = field(factory=Tplbase)
    # 组件的loader及模板环境．
    comp_tpl: "Tplbase" = field(factory=Tplbase)

    # 组件保存地．
    compath = field(default="src/components")
    delay_tpls: "list[DelayedTpl]" = field(factory=list)
    page_namer: "Namer" = field(factory=Namer)

    def enter_block(self, block, ctx):
        pass

    def leave_block(self, block, ctx):
        # 子节点的内容被dump为字符串,并做为参数render本block.
        pass

    # 深度优先，在leave时处理，渲染并将代码保存到对应block.code中．
    def travel_block(self, block, ctx) -> None:
        for sublock in block.blocks:
            ctx.path.append(f"{sublock.type}_{sublock.hints}")
            print("enter:", sublock.type, ctx.path)
            self.travel_block(sublock, ctx)
            render_block(sublock, ctx)
            ctx.path.pop()
            print("leave:", sublock.type)

    # 返回字符串或字典．字典代表了多个文件．key为文件名，如果value为字符串，则为内容．
    def gen_page(self, store, page, render_vars):
        ctx = GenpageCtx(page=page, vars=render_vars, store=store, svelte=self)
        # 深度遍历
        self.travel_block(page, ctx)
        ctx.files[PAGE_SVELTE] = "2222"
        return ctx.files

    def render_tpl(self, store, tpl_source, source_name):
        gathered_vars = self.page_tpl.gather_base(store, tpl_source, source_name)
        render_vars = gathered_vars.vars
        if len(gathered_vars.delay) > 0:
            raise ValueError(f"在渲染{source_name}时，遭遇延迟变量，需要coroute改写创建过程！")
        return Template(tpl_source).render(render_vars)

    def dump_all_page(self, store, basepath, render_vars):
        model = store.models["arch"]
        for pagename, page in model.pages.items():
            # gen_page，生成页面．并确定其输出路径．
            filename = self.page_namer.name(pagename)
            dirname = filename
            if is_valid_string(store.env.subdir):
                dirname = path.join(store.env.subdir, dirname)
                if filename == "index.html":
                    # 写入跳转页面固定文件．
                    filepath = path.join(basepath, "+page.svelte")
                    store.env.writefile(
                        filepath, self.render_tpl(store, GOTO_PAGE_TPL, filepath)
                    )
                    # 写入固定站点模板．
                    filepath = path.join(basepath, store.env.subdir, "+layout.svelte")
                    store.env.writefile(
                        filepath, self.render_tpl(store, DEF_LAYOUT, filepath)
                    )

            if filename == "index.html":
                dirname = store.env.subdir

            outdir = path.join(basepath, dirname)
            pagecnt = self.gen_page(store, page, render_vars)
            for fname, content in pagecnt.items():
                if is_valid_string(content):
                    store.env.writefile(path.join(outdir, fname), content)
        pass

    def dump(self, store):
        model = store.models["arch"]
        anonymous = model.anonymous
        if not anonymous:  # @todo: 未确定默认角色．
            raise ValueError("当前未指定匿名角色．")
        self.page_namer.reserved[model.roles[anonymous].home] = "index.html"
        self.page_namer.suffix = ".html"

        cfg_env = store.env

        all_templates = self.page_tpl.list_templates()
        for template_name in all_templates:
            # # 加载模板
            # {% set meta_title = "My Page Title" %}
            template = self.page_tpl.get_template(template_name)
            outname = template_name
            dump_mode = None
            gather_info = self.page_tpl.gather_base(
                store, self.page_tpl.get_tpl_source(template_name), template_name
            )
            src_path = None

            if "meta" in template.module.__dict__:
                meta = template.module.__dict__["meta"]
                if isinstance(meta, dict):
                    if "mode" in meta:  # 有效的mode: page
                        dump_mode = meta["mode"]
                    # 如果meta中定义了输出文件名．则采用此名称．
                    if "fname" in meta:
                        outname = meta["fname"]
                    if "src" in meta:
                        src_path = meta["src"]

            if path.isabs(outname):
                raise ValueError("给定的路径为全路径！")

            outpath = cfg_env.full_outdir("client", outname)
            if len(gather_info.delay) > 0:
                delay = DelayedTpl(
                    mode=dump_mode,
                    outpath=outpath,
                    render_vars=gather_info.vars,
                    delayed_vars=gather_info.delay,
                )
                self.delay_tpls.append(delay)
            elif dump_mode == "page":
                self.dump_all_page(store, outpath, gather_info.vars)
            elif dump_mode == "binary":
                Env.cpbin(cfg_env.app_path("kc", "binary", src_path), outpath)
            else:
                Env.writefile(outpath, template.render(gather_info.vars))

        # print(pretty.pretty_repr(model))

    def load(self, env: Env):
        self.page_tpl.load(env.app_path("kc", "client"))
        self.comp_tpl.load(env.app_path("kc", "comps"))

    # @staticmethod
    # def create(type: str,**kwargs) -> "Client":
    #     type_dict = {
    #         "Svelte": Svelte
    #     }
    #     Type = type_dict.get(type, None)
    #     if not Type:
    #         return None
    #     return Type(**kwargs)
