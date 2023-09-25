# 计算两个集合的交集．
def intersection(dict1: dict, dict2: dict) -> dict:
    return {k: dict1[k] for k in dict1 if k in dict2 and dict1[k] == dict2[k]}
