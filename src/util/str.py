# 字符串是否被引号包围
def hasquote(txt: str) -> bool:
    if type(txt) != str:
        return False
    if (txt.startswith('"') and txt.endswith('"')) or (
        txt.startswith("'") and txt.endswith("'")
    ):
        return True
    return False


# 如果argStr被'或"包围，移除两边的引号
def unquote(txt: str) -> str:
    if hasquote(txt):
        return txt[1:-1]
    return txt

def is_valid_string(s):
    """Check if a variable is a valid string and has length greater than zero."""
    return isinstance(s, str) and len(s) > 0
