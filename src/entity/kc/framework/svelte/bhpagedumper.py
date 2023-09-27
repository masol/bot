from attrs import define, field
from util.str import convert_to_base36, is_valid_string
from os import path
from ..dumper import Dumper
from .dumputil import DumpUtil


PAGE_SVELTE = "+page.svelte"


# 结构化页面，对应一个真实的svelte文件夹(可能映射多个文件，如layout,svelte等后缀)，
# 用于结构化保存页面的代码,importer以及style等信息．
@define(slots=True)
class StPage:
    # 代码区，此部分放在block中自行保存．
    # code: str = field(default="")
    # importer部分．key为库名称，value为导入的内容．
    importer: "dict[str,list]" = field(factory=dict)


# 页面上下文，用于跟踪一组流程页面(在wf.behaves中出现的页面，可能包含多个子页面)的信息．
@define(slots=True)
class BHpgDumper(Dumper):
    type: str = field(default="BHpgDumper")
    # 保存的文件对象．(文件路径到PageSt的映射)
    files: "dict[str,StPage]" = field(factory=dict)
    # 根页面，也是block树的根．
    page: "Page" = field(default=None)
    # 当前处理的block路径．
    path: "list[Block]" = field(factory=list)
    # 当前的子文件路径．在enter_block时处理．写入完毕后，pop之．全部连接起来，就是files中的key.
    filepath: "list" = field(default=[])
    # 为了简化子页面的命名，全部层级的路径共享一个计数器．
    count: int = field(default=0)
    # 当前主页面的输出目录,是URL绝对目录，不是文件路径．
    # outdir: str = field(default="")
    basedir: str = field(default="src/routes")

    # 获取当前页面对象．模板中的名称为"pageinfo".
    def curpage(self):
        curpath = "/".join(self.filepath)
        if curpath not in self.files:
            self.files[curpath] = StPage()
        return self.files[curpath]

    # 创建一个ctx唯一的名称，用做子页面名．
    def namer(self):
        name = convert_to_base36(self.count)
        self.count += 1
        return name

    # 将加载到的模板中的结构化信息(例如importer)，加入到当前页面中．
    def load_meta(self, module):
        if "meta" in module.__dict__:
            meta = module.__dict__["meta"]
            # print("test", ctx.curpage())
            if isinstance(meta, dict):
                if "import" in meta:  # 定义了import,加入当前页面
                    curpage = self.curpage()
                    for lib, eles in meta["import"].items():
                        if curpage.importer.get(lib) is None:
                            curpage.importer[lib] = eles
                        elif isinstance(curpage.importer[lib], list):
                            if isinstance(eles, list):
                                curpage.importer[lib].extend(eles)
                            elif isinstance(eles, str):
                                curpage.importer[lib].append(eles)
                            elif isinstance(eles, dict):
                                dict1 = {}
                                for old in curpage.importer[lib]:
                                    dict1[old] = old
                                curpage.importer[lib] = {**old, **eles}
                        elif isinstance(curpage.importer[lib], dict):
                            if isinstance(eles, dict):
                                curpage.importer[lib] = {
                                    **curpage.importer[lib],
                                    **eles,
                                }
                            elif isinstance(eles, list):
                                for ele in eles:
                                    curpage.importer[lib][ele] = ele
                            elif isinstance(eles, str):
                                curpage.importer[lib][eles] = eles
                        elif isinstance(curpage.importer[lib], str):
                            raise ValueError("不应该出现的情况:old importer为str")

    def render_block(self, block) -> bool:
        # 从ctx获取模板(comp_tpl)．
        comp_tpl = self.res.comp_tplset
        # 从block中获取模板名称．@TODO:这里需要综合利用子节点数量，label等信息，结合数据库来筛选．
        # 此处的实现为极简，功能有限，等待改进．
        # features = [block.type]
        tplname = block.type
        features = {}
        # features = [f"{tplname}.svelte"]
        if block.hints:
            features["hints"] = block.hints
            # tplname += f"/{block.hints}"
            # features.append(f"{tplname}.svelte")
        if block.label:
            features["label"] = block.label
            # tplname += f"/{block.label}"
            # features.append(f"{tplname}.svelte")

        template_name = comp_tpl.match_feature("comp", tplname, features)
        if not is_valid_string(template_name):
            print("缺少知识:", features, tplname)
            # print(comp_tpl.db)
            template_name = comp_tpl.by_name("comp", "default")
            # raise ValueError(f"无法加载{block.type}的基础模板")

        # 加载并处理模块附加信息
        self.load_meta(comp_tpl.module(template_name))
        # module =
        # # template = comp_tpl.get_template(template_name)
        # # 获取meta信息，并将importer等内容加入到page中．
        # if "meta" in module.__dict__:
        #     meta = module.__dict__["meta"]
        #     # print("test", ctx.curpage())
        #     if isinstance(meta, dict):
        #         if "import" in meta:  # 定义了import,加入当前页面
        #             curpage = self.curpage()
        #             for lib, eles in meta["import"].items():
        #                 if curpage.importer.get(lib) is None:
        #                     curpage.importer[lib] = set(eles)
        #                 else:
        #                     curpage.importer[lib].update(eles)

        # 获取undeclared_vars．
        # undeclared_vars = comp_tpl.gather_base(
        #     ctx.store,
        #     comp_tpl.get_tpl_source(template_name),
        #     template_name,
        #     get_render_vars(block, ctx),
        # )
        # 如果在card中，无需skelte处理．card来处理之．
        block.code = comp_tpl.render(
            template_name, self.req, self.res, DumpUtil.get_render_vars(block, self)
        )
        # block.code = template.render(undeclared_vars.vars)
        return True

    # 当前block渲染完毕时，如果是一个页面/子页面，将ctx中的页面对象生成．
    def render_page(self, filename, block) -> None:
        comp_tpl = self.res.comp_tplset
        # vars_info = comp_tpl.gather_base(
        #     ctx.store, SVELTE_PAGE_TPL, filename, get_render_vars(block, ctx)
        # )
        # vars_info.dump_imgs(ctx)
        tpl_name = comp_tpl.by_name("skel", "page")
        # self.filecnt[path.join(filename, PAGE_SVELTE)] = comp_tpl.render_src(
        #     SVELTE_PAGE_TPL, vars_info.vars
        # )
        self.filecnt[path.join(filename, PAGE_SVELTE)] = comp_tpl.render(
            tpl_name, self.req, self.res, DumpUtil.get_render_vars(block, self)
        )

    def gen(self):
        self.travel_block(self.page)
        # 将subblock的code合并到page.code中．
        # page.code = "\n".join([block.code for block in page.blocks])
        self.render_page("", self.page)

    # 深度优先，在leave时处理，渲染并将代码保存到对应block.code中．
    def travel_block(self, block) -> None:
        # ctx = self.genbhctx
        for sublock in block.blocks:
            self.path.append(f"{sublock.type}_{sublock.hints}")
            # 检查block是否需要新建一个子页面．
            newsubpage = DumpUtil.has_subpage(sublock)
            if newsubpage:
                filename = self.namer()
                self.filepath.append(filename)
            # print("enter:", sublock.type, ctx.path)
            if sublock.type == "Button":
                sublock.href = self.res.cvt_href(sublock.href, self)
            self.travel_block(sublock)
            self.render_block(sublock)
            self.path.pop()
            if newsubpage:
                self.render_page(filename, sublock)
                # 因写入page,清空code,防止父blk组合代码时，意外插入此代码.
                # sublock.code = ""
                self.filepath.pop()
                # print("filename=", filename, "code=", sublock.code)
            # print("leave:", sublock.type)
