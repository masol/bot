from attrs import define, field
from util.str import is_valid_string, convert_to_base36
from util.namer import Namer
from rich import pretty
from os import path
from urllib.parse import urlparse

# from ...blkrender import render_block, has_subpage, render_page
from ...tplset import Tplcomp
from ..project import Project
from .bhpagedumper import BHpgDumper
from ...requirement import Requirement
from .dumputil import DumpUtil


# 为了方便，为svelte,添加在jinjia2中的一些函数．
# 1. 导出importer:
def render_importer(importer):
    ret = ""
    for lib, eles in importer.items():
        if isinstance(eles, str):
            ret += f"import { eles } from '{lib}';\n"
        elif isinstance(eles,list):
            eles = list(set(eles))
            ret += f"import {{ {','.join(eles)} }} from '{lib}';\n"
        elif isinstance(eles,dict):
            importstr = []
            for name, alias in eles.items():
                importstr.append(f"{name} as {alias}")
            ret += f"import {{ {','.join(importstr) } }} from '{lib}';\n"
    return ret

# 做为svelte的实现．当前尚未实现客户端知识库加载．
@define(slots=True)
class Svelte(Project):
    type: str = field(default="Svelte")

    # 组件的loader及模板环境．
    comp_tplset: "Tplcomp" = field(factory=Tplcomp)
    # 　页面的命名器．
    # page_namer: Namer = field(factory=Namer)
    # 项目的代码名称．
    name: str = field(default="client")
    # 项目的模板路径．
    tplpath: str = field(default=path.join("kc", "client"))

    def get_imgpath(self, req, filename):
        return self.target_dir("src", "lib", "images", filename)

    def get_imgvalue(self, fnparts: list, imgInfo):
        return "{" + "/".join(fnparts) + "}"

    def render_global(self, req: Requirement, globals: dict):
        globals['render_importer'] = render_importer

    def cvt_href(self, href, dumper):
        store = dumper.req.store
        print("href=", href)
        if is_valid_string(href):
            result = urlparse(href)
            print(result)
            if result.scheme == "page":
                return dumper.req.get_pageurl(result.netloc)
            # elif result.scheme == 'api':
            # else:
            #     raise ValueError("尚未实现的api")
        else:
            return "/" + dumper.dirname + "/" + "/".join(dumper.filepath)
        return "javascript:void(0)"

    # # 深度优先，在leave时处理，渲染并将代码保存到对应block.code中．
    # def travel_block(self, dumper, block) -> None:
    #     # ctx = self.genbhctx
    #     for sublock in block.blocks:
    #         dumper.path.append(f"{sublock.type}_{sublock.hints}")
    #         # 检查block是否需要新建一个子页面．
    #         newsubpage = DumpUtil.has_subpage(sublock)
    #         if newsubpage:
    #             filename = dumper.namer()
    #             dumper.filepath.append(filename)
    #         # print("enter:", sublock.type, ctx.path)
    #         if sublock.type == "Button":
    #             sublock.href = self.cvt_href(sublock.href, ctx)
    #         self.travel_block(sublock)
    #         dumper.render_block(sublock)
    #         dumper.path.pop()
    #         if newsubpage:
    #             dumper.render_page(filename, sublock, dumper)
    #             # 因写入page,清空code,防止父blk组合代码时，意外插入此代码.
    #             # sublock.code = ""
    #             dumper.filepath.pop()
    #             # print("filename=", filename, "code=", sublock.code)
    #         # print("leave:", sublock.type)

    # # 返回字符串或字典．字典代表了多个文件．key为文件名，如果value为字符串，则为内容．
    # def gen_page(self, req, page, render_vars, outdir):
    #     # old_genctx = self.genbhctx
    #     # self.genbhctx = BHpgDumper(page=page, vars=render_vars, outdir=outdir)
    #     genbhctx = BHpgDumper(page=page, vars=render_vars, outdir=outdir)
    #     # 深度遍历
    #     self.travel_block(genbhctx, page)
    #     # 将subblock的code合并到page.code中．
    #     # page.code = "\n".join([block.code for block in page.blocks])
    #     render_page("", page, self)
    #     # filecnt = self.genbhctx.filecnt
    #     filecnt = genbhctx.filecnt
    #     # self.genbhctx = old_genctx
    #     # print(ctx.filecnt)
    #     return filecnt

    # 工具函数，负责将页面名称转换为文件名．
    # def get_pagename(self, store, pagename):
    #     filename = self.page_namer.name(pagename)
    #     if is_valid_string(store.env.subdir):
    #         return "/" + store.env.subdir + "/" + filename
    #     return "/" + filename

    def dump_page(self, req: "Requirement", basepath):
        for pagename, page in req.get_pages().items():
            # gen_page，生成页面．并确定其输出路径．
            filename = req.page_namer.name(pagename)
            dirname = filename
            store = req.store
            if is_valid_string(store.env.subdir):
                dirname = path.join(store.env.subdir, dirname)
                if filename == "index.html":
                    # 写入额外的站点级跳转结构．无需考虑依赖，已在模型期处理了依赖关系．
                    # 写入跳转页面固定文件．
                    filepath = path.join(basepath, "+page.svelte")
                    tpl_name = self.comp_tplset.by_name("skel", "gotopage")
                    store.env.writefile(
                        filepath, self.comp_tplset.render(tpl_name, req, self)
                    )
                    # 写入固定站点模板．
                    filepath = path.join(basepath, store.env.subdir, "+layout.svelte")
                    tpl_name = self.comp_tplset.by_name("skel", "gotolayout")
                    store.env.writefile(
                        filepath, self.comp_tplset.render(tpl_name, req, self)
                    )

            if filename == "index.html":
                dirname = store.env.subdir

            outdir = path.join(basepath, dirname)
            print("outdir=", outdir)
            dumper = BHpgDumper(page=page, dirname=dirname, req=req, res=self)
            # pagecnt = self.gen_page(req, page, render_vars, dirname)
            dumper.dump()

    def dump_mode(self, dump_mode, req, outpath):
        if dump_mode == "page":
            return self.dump_page(req, outpath)
        raise ValueError(f"svelte中未支持渲染模式{dump_mode}")

    def load(self, req: Requirement):
        super().load(req)
        self.comp_tplset.load(req, self, req.store.env.app_path("kc", "comps"))

    # @staticmethod
    # def create(type: str,**kwargs) -> "Client":
    #     type_dict = {
    #         "Svelte": Svelte
    #     }
    #     Type = type_dict.get(type, None)
    #     if not Type:
    #         return None
    #     return Type(**kwargs)
