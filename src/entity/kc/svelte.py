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

PAGE_SVELTE = "+page.svelte"

GOTO_PAGE_TPL = """
<script>
	// @ts-nocheck
	import { goto } from '$app/navigation';
    import { browser } from '$app/environment'
    
	if (browser) {
		goto('/{{subdir}}');
	}
</script>
"""
DEF_LAYOUT = """
<script>
	import Header from '$lib/components/header.svelte';
	import Footer from '$lib/components/footer.svelte';
</script>

<Header />
<hr />
<section class="bg-white dark:bg-gray-600 min84">
	<slot />
</section>

<Footer />

<style>
	.min84 {
		min-height: 84vh;
	}
</style>
"""


# 部分依赖变量需要其它部分，因此一个输出会被延迟．
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
    loader = field(default=None)
    env = field(default=None)
    compath = field(default="src/components")
    delay_tpls: "list[DelayedTpl]" = field(factory=list)
    page_namer: "Namer" = field(factory=Namer)

    def gather_vars(self, store, template_name):
        # 获取源代码
        template_source = self.env.loader.get_source(self.env, template_name)[0]
        parsed_content = self.env.parse(template_source)
        undeclared = find_undeclared_variables(parsed_content)
        # print(undeclared)
        self_vars = {"compath"}
        env_vars = {"subdir"}
        ret = {"vars": {}, "delay": {}}
        for key in undeclared:
            if key in self_vars:
                ret["vars"][key] = self.getattr(key)
            elif key in env_vars:
                ret["vars"][key] = store.env.getattr(key)
            elif key == "current_year":
                ret["vars"][key] = datetime.now().year
            elif key == "project_name":  # @TODO: 在输入文件中定义option.
                ret["vars"][key] = "client"
            else:
                raise ValueError(f"无法识别模板{template_name}中定义的变量{key}")
        return ret

    # 返回字符串或字典．字典代表了多个文件．key为文件名，如果value为字符串，则为内容．
    def gen_page(self, page, render_vars):
        files = {}
        files[PAGE_SVELTE] = "2222"
        return files

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
                    store.env.writefile(
                        path.join(basepath, "+page.svelte"),
                        Template(GOTO_PAGE_TPL).render(subdir=store.env.subdir),
                    )
                    # 写入固定站点模板．
                    store.env.writefile(
                        path.join(basepath, store.env.subdir, "+layout.svelte"),
                        Template(DEF_LAYOUT).render(),
                    )

            if filename == "index.html":
                dirname = store.env.subdir

            outdir = path.join(basepath, dirname)
            pagecnt = self.gen_page(page, render_vars)
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

        all_templates = self.env.list_templates()
        for template_name in all_templates:
            # # 加载模板
            # {% set meta_title = "My Page Title" %}
            template = self.env.get_template(template_name)
            outname = template_name
            dump_mode = None
            gather_info = self.gather_vars(store, template_name)
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
            if len(gather_info["delay"]) > 0:
                delay = DelayedTpl(
                    mode=dump_mode,
                    outpath=outpath,
                    render_vars=gather_info["vars"],
                    delayed_vars=gather_info["delay"],
                )
                self.delay_tpls.append(delay)
            elif dump_mode == "page":
                self.dump_all_page(store, outpath, gather_info["vars"])
            elif dump_mode == "binary":
                Env.cpbin(cfg_env.app_path("kc", "binary", src_path), outpath)
            else:
                Env.writefile(outpath, template.render(gather_info["vars"]))

        # print(pretty.pretty_repr(model))

    def load(self, env: Env):
        self.loader = FileSystemLoader(env.app_path("kc", "client"))
        self.env = Environment(
            loader=self.loader,
            # 默认的注释语法{#，和svelte的语法冲突．
            comment_start_string="{${",
            comment_end_string="=}$}",
        )

    # @staticmethod
    # def create(type: str,**kwargs) -> "Client":
    #     type_dict = {
    #         "Svelte": Svelte
    #     }
    #     Type = type_dict.get(type, None)
    #     if not Type:
    #         return None
    #     return Type(**kwargs)
