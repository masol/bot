from attrs import define, field
from entity import entity
from entity.env import Env
from util.str import is_valid_string, convert_to_base36
from util.namer import Namer
from rich import pretty
from os import path


from .constpl.gotopage import GOTO_PAGE_TPL
from .constpl.layout import DEF_LAYOUT
from .blkrender import render_block, has_subpage, render_page
from .tpl import Tplbase, DelayedTpl


@define(slots=True)
class PageSt:
    # 代码区，此部分放在block中自行保存．
    # code: str = field(default="")
    # importer部分．key为库名称，value为导入的内容．
    importer: "dict[str,list]" = field(factory=dict)


@define(slots=True)
class GenpageCtx:
    # 保存的文件对象．
    files: "dict[str,PageSt]" = field(factory=dict)
    # 文件的渲染结果．
    filecnt: "dict[str,str]" = field(factory=dict)
    # 根页面，也是block树的根．
    page: "Page" = field(default=None)
    # 根页面收集到的渲染用变量．(考虑废弃)
    vars: dict = field(factory=dict)
    # 全局store对象．
    store: "Store" = field(default=None)
    # 当前处理的block路径．
    path: "list[Block]" = field(factory=list)
    # 所属svelte对象．
    svelte: "Svelte" = field(default=None)
    # 当前的子文件路径．在enter_block时处理．写入完毕后，pop之．全部连接起来，就是files中的key.
    filepath: "list" = field(default=[])
    # 为了简化名称命名，全部层级的路径共享一个计数器．
    count: int = field(default=0)
    # 当前主页面的输出目录．
    outdir: str = field(default="")

    # 获取当前页面对象．模板中的名称为"pageinfo".
    def curpage(self):
        curpath = "/".join(self.filepath)
        if curpath not in self.files:
            self.files[curpath] = PageSt()
        return self.files[curpath]

    # 创建一个ctx唯一的名称，用做子页面名．
    def namer(self):
        name = convert_to_base36(self.count)
        self.count += 1
        return name


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
            # 检查block是否需要新建一个子页面．
            newsubpage = has_subpage(sublock)
            if newsubpage:
                filename = ctx.namer()
                ctx.filepath.append(filename)
                if sublock.type == "Button":
                    sublock.href = ctx.outdir + '/' + "/".join(ctx.filepath)
            # print("enter:", sublock.type, ctx.path)
            self.travel_block(sublock, ctx)
            render_block(sublock, ctx)
            ctx.path.pop()
            if newsubpage:
                render_page(filename, sublock, ctx)
                # 因写入page,清空code,防止父blk组合代码时，意外插入此代码.
                # sublock.code = ""
                ctx.filepath.pop()
                # print("filename=", filename, "code=", sublock.code)
            # print("leave:", sublock.type)

    # 返回字符串或字典．字典代表了多个文件．key为文件名，如果value为字符串，则为内容．
    def gen_page(self, store, page, render_vars, outdir):
        ctx = GenpageCtx(
            page=page, vars=render_vars, store=store, svelte=self, outdir=outdir
        )
        # 深度遍历
        self.travel_block(page, ctx)
        # 将subblock的code合并到page.code中．
        # page.code = "\n".join([block.code for block in page.blocks])
        render_page("", page, ctx)
        # print(ctx.filecnt)
        return ctx.filecnt

    def render_tpl(self, store, tpl_source, source_name):
        gathered_vars = self.page_tpl.gather_base(store, tpl_source, source_name)
        render_vars = gathered_vars.vars
        if len(gathered_vars.delay) > 0:
            raise ValueError(f"在渲染{source_name}时，遭遇延迟变量，需要coroute改写创建过程！")
        return self.page_tpl.render_src(tpl_source, render_vars)

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
            pagecnt = self.gen_page(store, page, render_vars, outdir)
            for fname, content in pagecnt.items():
                if is_valid_string(content):
                    store.env.writefile(path.join(outdir, fname), content)

    def dump(self, store):
        model = store.models["arch"]
        anonymous = model.anonymous
        if not anonymous:  # @todo: 未确定默认角色．
            raise ValueError("当前未指定匿名角色．")
        self.page_namer.reserved[model.roles[anonymous].home] = "index.html"
        self.page_namer.suffix = ""

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
