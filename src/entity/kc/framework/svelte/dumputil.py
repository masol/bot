


class DumpUtil:
    # 检查指定的bock是否需要切换为新的子页面．
    @staticmethod
    def has_subpage(block):
        if block.type == "Button" and len(block.blocks) > 0:
            return True
        return False

    @staticmethod
    def get_render_vars(block, dumper):
        return {
            "blocks": block.blocks,
            "current": block,
            "pageinfo": dumper.curpage(),
        }

    # 静态类，确定svelte块的内容,选择知识库中的block模板，并渲染之．
    # 调用时，确保子block已经渲染完成(code已有内容)
