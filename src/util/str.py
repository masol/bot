# 如果argStr被'或"包围，移除两边的引号
def unquote(txt: str) -> str:
    if (txt.startswith('"') and txt.endswith('"')) or (
        txt.startswith("'") and txt.endswith("'")
    ):
        return txt[1:-1]
    return txt
