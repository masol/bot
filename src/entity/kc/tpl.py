from attrs import define, field
from entity import entity
from entity.env import Env
from os import path
from jinja2 import Environment, FileSystemLoader, Template
from jinja2.meta import find_undeclared_variables
from util.str import is_valid_string
import re
from datetime import datetime


# 为了方便，添加在jinjia2中的一些函数．
# 1. 导出importer:
def render_importer(importer):
    ret = ""
    for lib, eles in importer.items():
        ret += f"import {{ {','.join(eles)} }} from '{lib}';\n"
    return ret


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


# 保存未使用变量的映射结果．
@define(slots=True)
class GatheredVars(entity.Entity):
    vars: "dict" = field(factory=dict)
    # 延迟变量，需要给出依赖信息．
    delay: "dict" = field(factory=dict)

    # 基础收集．vars中的已确定的变量会被移除．
    def gather_base(self, store, undeclared, var_dict=None):
        const_dict = {"compath": "src/components"}
        const_vars = set(const_dict.keys())
        env_vars = {"subdir"}
        to_del = []
        for key in undeclared:
            if key in const_vars:
                self.vars[key] = const_dict[key]
                to_del.append(key)
            elif key in env_vars:
                self.vars[key] = store.env.getattr(key)
                to_del.append(key)
            elif key == "current_year":
                self.vars[key] = datetime.now().year
                to_del.append(key)
            elif key == "project_name":  # @TODO: 在输入文件中定义option.
                self.vars[key] = "client"
                to_del.append(key)
            elif key in var_dict:  # 从给定的字典中获取．
                self.vars[key] = var_dict[key]
                to_del.append(key)
        for key in to_del:
            undeclared.remove(key)

    def chk_undeclared(undeclared, template_name):
        if len(undeclared) > 0:
            raise ValueError(f"无法识别模板{template_name}中定义的变量:{list(undeclared)}")


# 维护知识库中的模板．
@define(slots=True)
class Tplbase(entity.Entity):
    loader = field(default=None)
    env = field(default=None)

    # 组件的loader及模板环境．
    def load(self, basedir):
        self.loader = FileSystemLoader(basedir)
        self.env = Environment(
            loader=self.loader,
            # 默认的注释语法{#，和svelte的语法冲突．
            comment_start_string="{${",
            comment_end_string="=}$}",
        )
        self.env.globals["render_importer"] = render_importer

    # 获取特定名称的模板．
    def get_template(self, name):
        return self.env.get_template(name)

    # 列出全部模板，如果pattern为字符串，则以pattern开头，如果是正则表达式，则匹配之．
    def list_templates(self, pattern=None):
        all_templates = self.env.list_templates()
        if is_valid_string(pattern):
            return [t for t in all_templates if t.startswith(pattern)]
        elif isinstance(pattern, re.Pattern):
            return [t for t in all_templates if re.match(pattern, t) is not None]
        return all_templates

    # 获取模板中未声明的变量．
    def get_undeclared_variables(self, template_source):
        parsed_content = self.env.parse(template_source)
        return find_undeclared_variables(parsed_content)

    # 获取模板的源码
    def get_tpl_source(self, template_name):
        return self.env.loader.get_source(self.env, template_name)[0]

    # 基础收集．返回GatheredVars.extra_gather是一个字典，如果给定，保存了block等额外变量．
    def gather_base(
        self, store, template_source, template_name, var_dict=None
    ) -> GatheredVars:
        undeclared = self.get_undeclared_variables(template_source)
        ret: "GatheredVars" = GatheredVars()
        ret.gather_base(store, undeclared, var_dict)
        GatheredVars.chk_undeclared(undeclared, template_name)
        return ret

    # 获取模板，其路径为features路径的一个子集．返回最长匹配．
    def match_feature(self, features: "list[str]"):
        # 列出所有可能的feature名．
        all_templates = self.env.list_templates()
        possible = set()
        for t in all_templates:
            if t in features:
                possible.add(t)

        if len(possible) == 0:
            return None
        return max(possible, key=len)

    def render_src(self, template_source, render_vars):
        template = self.env.from_string(template_source)
        return template.render(render_vars)

    # 渲染库中的全部模板，输出到output_dir下．对于特定的dump_mode,调用dump_mode_func来处理．
    def render_all(self, store, output_dir, dump_mode_func):
        cfg_env = store.env
        all_templates = self.list_templates()
        for template_name in all_templates:
            # # 加载模板
            # {% set meta_title = "My Page Title" %}
            template = self.get_template(template_name)
            outname = template_name
            dump_mode = None
            gather_info = self.gather_base(
                store, self.get_tpl_source(template_name), template_name
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

            outpath = cfg_env.full_outdir(output_dir, outname)
            if len(gather_info.delay) > 0:
                delay = DelayedTpl(
                    mode=dump_mode,
                    outpath=outpath,
                    render_vars=gather_info.vars,
                    delayed_vars=gather_info.delay,
                )
                self.delay_tpls.append(delay)
            elif not is_valid_string(dump_mode):
                Env.writefile(outpath, template.render(gather_info.vars))
            elif dump_mode == "binary":
                Env.cpbin(cfg_env.app_path("kc", "binary", src_path), outpath)
            else:
                if callable(dump_mode_func):
                    dump_mode_func(dump_mode, store, outpath, gather_info)
                else:
                    raise ValueError(f"模板{template_name}中含有不能处理的渲染模式{dump_mode}")
