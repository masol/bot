from attrs import define, field
# from entity import entity
from entity.env import Env
from os import path
from jinja2 import Environment, FileSystemLoader, TemplateNotFound
from jinja2.meta import find_undeclared_variables
from util.str import is_valid_string
import re
from os import path

from ..framework.project import Project

SETUPTPL_NAME = "config.tpl"


@define(slots=True)
class FakeModule:
    __dict__: dict = field(factory=dict)


# # 保存未使用变量的映射结果．
# @define(slots=True)
# class GatheredVars(entity.Entity):
#     vars: "dict" = field(factory=dict)
#     # 延迟变量，需要给出依赖信息．
#     delay: "dict" = field(factory=dict)
#     # 需要创建的图片文件．
#     images: "list" = field(factory=list)

#     # 基础收集．vars中的已确定的变量会被移除．
#     def gather_base(self, store, undeclared, var_dict=None):
#         const_dict = {"compath": "src/components"}
#         const_vars = set(const_dict.keys())
#         env_vars = {"subdir"}
#         to_del = []
#         for key in undeclared:
#             if key in const_vars:
#                 self.vars[key] = const_dict[key]
#                 to_del.append(key)
#             elif key in env_vars:
#                 self.vars[key] = store.env.getattr(key)
#                 to_del.append(key)
#             elif key == "current_year":
#                 self.vars[key] = datetime.now().year
#                 to_del.append(key)
#             elif key == "project_name":  # @TODO: 在输入文件中定义option.
#                 self.vars[key] = "client"
#                 to_del.append(key)
#             elif isinstance(var_dict, dict) and key in var_dict:  # 从给定的字典中获取．
#                 self.vars[key] = var_dict[key]
#                 to_del.append(key)
#             elif key.startswith("img_"):
#                 # tk is temp key.
#                 tokens = key[len("img_") :].split("__")
#                 w = 256
#                 h = 256
#                 suffix = "jpg"
#                 transparent = False
#                 filename = ""
#                 if len(tokens) > 1:  # 定义了图片尺寸．
#                     size = tokens[0].split("_")
#                     w = int(size[0])
#                     if len(size) > 1:
#                         h = int(size[1])
#                     else:
#                         h = w
#                 fnparts = tokens[-1].split("_")
#                 if fnparts[-1].lower() in image_formats:
#                     suffix = fnparts[-1].lower()
#                     transparent = suffix in transparent_formats
#                     fnparts.pop()
#                 filename = "/".join(fnparts) + "." + suffix
#                 img_info = ImageInfo(
#                     filename=filename, width=w, height=h, transparent=transparent
#                 )
#                 self.images.append(img_info)
#                 self.vars[key] = "{" + "/".join(fnparts) + "}"
#                 to_del.append(key)
#                 # print("img_info=", img_info)
#         for key in to_del:
#             undeclared.remove(key)

#     def chk_undeclared(undeclared, template_name):
#         if len(undeclared) > 0:
#             raise ValueError(f"无法识别模板{template_name}中定义的变量:{list(undeclared)}")

#     def dump_imgs(self, output_dir):
#         if len(self.images) > 0:
#             print("dump_imgs output_dir=", output_dir)
#         for img in self.images:
#             print(img)
#             # 生成随机颜色的像素
#             pixel_data = np.random.randint(
#                 0,
#                 255,
#                 (img.width, img.height, 4 if img.transparent else 3),
#                 dtype=np.uint8,
#             )
#             # 创建一个新的图像
#             imgobj = Image.fromarray(pixel_data)
#             # 保存为PNG格式的图片
#             filepath = path.join(output_dir, img.filename)
#             directory = path.dirname(filepath)
#             Env.mkdirs(directory)
#             imgobj.save(filepath)


# 模板集基类，提供了渲染，获取源码等方法．
@define(slots=True)
class Tplset:
    loader = field(default=None)
    env = field(default=None)

    # 组件的loader及模板环境．
    def load(self, req, res, basedir):
        self.loader = FileSystemLoader(basedir)
        self.env = Environment(
            loader=self.loader,
            # 默认的注释语法{#，和svelte的语法冲突．
            comment_start_string="{${",
            comment_end_string="=}$}",
        )
        res.render_global(req, self.env.globals)
        # self.env.globals["render_importer"] = render_importer

    # 获取特定名称的模板．
    def _get_template(self, name):
        try:
            # print("get_template_name=", name)
            template = self.env.get_template(name)
        except TemplateNotFound:
            template = None
        return template

    # 列出全部模板，如果pattern为字符串，则以pattern开头，如果是正则表达式，则匹配之．
    def list_templates(self, pattern=None):
        all_templates = self.env.list_templates()
        if is_valid_string(pattern):
            return [t for t in all_templates if t.startswith(pattern)]
        elif isinstance(pattern, re.Pattern):
            return [t for t in all_templates if re.match(pattern, t) is not None]
        return all_templates

    # 获取模板中未声明的变量．
    def _get_undeclared_variables(self, template_source):
        parsed_content = self.env.parse(template_source)
        return find_undeclared_variables(parsed_content)

    # 获取模板的源码
    def _get_tpl_source(self, template_name):
        return self.env.loader.get_source(self.env, template_name)[0]

    # 基础收集．返回GatheredVars.extra_gather是一个字典，如果给定，保存了block等额外变量．
    # def gather_base(
    #     self, store, template_source, template_name, var_dict=None
    # ) -> GatheredVars:
    #     undeclared = self._get_undeclared_variables(template_source)
    #     ret: "GatheredVars" = GatheredVars()
    #     ret.gather_base(store, undeclared, var_dict)
    #     GatheredVars.chk_undeclared(undeclared, template_name)
    #     return ret

    # 获取模板，其路径为features路径的一个子集．返回最长匹配．
    # def match_feature(self, features: "list[str]"):
    #     # 列出所有可能的feature名．
    #     all_templates = self.env.list_templates()
    #     possible = set()
    #     for t in all_templates:
    #         if t in features:
    #             possible.add(t)

    #     if len(possible) == 0:
    #         return None
    #     return max(possible, key=len)

    # def render_src(self, template_source, render_vars):
    #     template = self.env.from_string(template_source)
    #     return template.render(render_vars)

    def render(self, template_name, req, res: Project, base_vars=None) -> str:
        template = self._get_template(template_name)
        if not template:
            return ""
        undeclared = self._get_undeclared_variables(self._get_tpl_source(template_name))
        render_vars = res.get_vars(req, undeclared, template_name, base_vars)
        return template.render(render_vars)

    def module(self, template_name) -> dict:
        template = self._get_template(template_name)
        if not template:
            print("not found template:", template_name)
            return FakeModule()
            # return {"__dict__": {}}
        return template.module

    def dump(self, template_name, req, res: Project, base_vars=None):
        cfg_env = req.store.env
        # template = self._get_template(template_name)
        module = self.module(template_name)
        if isinstance(module, FakeModule):
            return
        outname = template_name
        mode_name = None
        # undeclared = self._get_undeclared_variables(
        #     self._get_tpl_source(template_name), base_vars
        # )
        # render_vars = res.get_vars(req, undeclared, template_name, base_vars)
        # gather_info = self.gather_base(
        #     req.store, self.get_tpl_source(template_name), template_name
        # )
        src_path = None
        norender = False

        if "meta" in module.__dict__:
            meta = module.__dict__["meta"]
            if isinstance(meta, dict):
                if "mode" in meta:  # 有效的mode: page
                    mode_name = meta["mode"]
                # 如果meta中定义了输出文件名．则采用此名称．
                if "fname" in meta:
                    outname = meta["fname"]
                if "src" in meta:
                    src_path = meta["src"]
                if "norender" in meta:
                    norender = meta["norender"]

        if norender:
            return

        if path.isabs(outname):
            raise ValueError(f"模板中给定的路径{outname}为全路径！")

        outpath = res.target_dir(outname)
        if not is_valid_string(mode_name):
            Env.writefile(outpath, self.render(template_name, req, res, base_vars))
        elif mode_name == "binary":
            Env.cpbin(cfg_env.app_path("kc", "binary", src_path), outpath)
        else:
            res.dump_mode(mode_name, req, outpath)

    # 渲染库中的全部模板，输出到output_dir下．对于特定的dump_mode,调用dump_mode_func来处理．
    def dump_all(self, req, res: Project):
        # 加载模板组中的配置项．
        try:
            self.dump(SETUPTPL_NAME, req, res)
        except TemplateNotFound:
            pass
        all_templates = self.list_templates()
        for template_name in all_templates:
            self.dump(template_name, req, res)
            # # 加载模板
            # {% set meta_title = "My Page Title" %}
