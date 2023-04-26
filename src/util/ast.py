import esprima


# 如果node是identify类型,则返回identify的名称,否则返回None
def identify(node: esprima.nodes.Node) -> str or None:
    if node.type == "Identifier":
        return node.name
    return None


# 如果argStr被'或"包围，移除两边的引号
def unquote(txt: str) -> str:
    if (txt.startswith('"') and txt.endswith('"')) or (
        txt.startswith("'") and txt.endswith("'")
    ):
        return txt[1:-1]
    return txt
