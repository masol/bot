# 获取user_data_dir
def user_data_dir() -> str:
    import appdirs

    return appdirs.user_data_dir("bot", "spolo")
