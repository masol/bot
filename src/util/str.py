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


# 获取字符串的md5 hash值.
# 不采用sha,因为sha的hash值太长了.
def md5hash(txt: str) -> int:
    import hashlib

    hash_object = hashlib.md5(txt.encode())
    return int(hash_object.hexdigest(), 16)


def is_valid_string(s):
    """Check if a variable is a valid string and has length greater than zero."""
    return isinstance(s, str) and len(s) > 0

def convert_to_base36(number):
    chars = "0123456789abcdefghijklmnopqrstuvwxyz"

    if number < 36:
        return chars[number]
    else:
        number, remainder = divmod(number, 36)
        return convert_to_base36(number) + chars[remainder]