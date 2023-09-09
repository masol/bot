# from attrs import define, field
from util.str import is_valid_string
from .constpl.sveltepage import SVELTE_PAGE_TPL

from os import path
PAGE_SVELTE = "+page.svelte"


def get_render_vars(block, ctx):
    return {
        "blocks": block.blocks,
        "current": block,
        "pageinfo": ctx.curpage(),
    }


# 当前block渲染完毕时，如果是一个页面/子页面，将ctx中的页面对象生成．
def render_page(filename, block, ctx) -> None:
    comp_tpl = ctx.svelte.comp_tpl
    undeclared_vars = comp_tpl.gather_base(
        ctx.store, SVELTE_PAGE_TPL, filename, get_render_vars(block, ctx)
    )
    ctx.filecnt[path.join(filename,PAGE_SVELTE)] = comp_tpl.render_src(SVELTE_PAGE_TPL, undeclared_vars.vars)


# 静态类，确定svelte块的内容,选择知识库中的block模板，并渲染之．
# 调用时，确保子block已经渲染完成(code已有内容)
def render_block(block, ctx) -> bool:
    # 从ctx获取模板(comp_tpl)．
    comp_tpl = ctx.svelte.comp_tpl
    # 从block中获取模板名称．@TODO:这里需要综合利用子节点数量，label等信息，结合数据库来筛选．
    # 此处的实现为极简，功能有限，等待改进．
    # features = [block.type]
    tplname = block.type
    features = [f"{tplname}.svelte"]
    if block.hints:
        tplname += f"/{block.hints}"
        features.append(f"{tplname}.svelte")
    if block.label:
        tplname += f"/{block.label}"
        features.append(f"{tplname}.svelte")

    template_name = comp_tpl.match_feature(features)
    print(features, template_name)
    if not is_valid_string(template_name):
        template_name = f"default.svelte"
        # raise ValueError(f"无法加载{block.type}的基础模板")

    # 获取模板．
    template = comp_tpl.get_template(template_name)
    # 获取meta信息，并将importer等内容加入到page中．
    if "meta" in template.module.__dict__:
        meta = template.module.__dict__["meta"]
        print("test", ctx.curpage())
        if isinstance(meta, dict):
            if "import" in meta:  # 定义了import,加入当前页面
                curpage = ctx.curpage()
                for lib, eles in meta["import"].items():
                    if curpage.importer.get(lib) is None:
                        curpage.importer[lib] = set(eles)
                    else:
                        curpage.importer[lib].update(eles)

    # 获取undeclared_vars．
    undeclared_vars = comp_tpl.gather_base(
        ctx.store,
        comp_tpl.get_tpl_source(template_name),
        template_name,
        get_render_vars(block, ctx),
    )
    # 如果在card中，无需skelte处理．card来处理之．
    block.code = template.render(undeclared_vars.vars)
    return True


# 检查指定的bock是否需要切换为新的子页面．
def has_subpage(block):
    if block.type == "Button" and len(block.blocks) > 0:
        return True
    return False
