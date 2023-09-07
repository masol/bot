from attrs import define, field
from entity import entity
from jinja2 import Environment, FileSystemLoader, Template
from jinja2.meta import find_undeclared_variables
from util.str import is_valid_string
import re
from datetime import datetime


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
    def gather_base(self, store, undeclared):
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
        for key in to_del:
            undeclared.remove(key)

    def chk_undeclared(undeclared, template_name):
        if len(undeclared) > 0:
            raise ValueError(f"无法识别模板{template_name}中定义的变量:{list(undeclared.keys())}")


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

    # 基础收集．返回GatheredVars.
    def gather_base(self, store, template_source, template_name) -> GatheredVars:
        undeclared = self.get_undeclared_variables(template_source)
        ret: "GatheredVars" = GatheredVars()
        ret.gather_base(store, undeclared)
        GatheredVars.chk_undeclared(undeclared, template_name)
        return ret
