from attrs import define, field

# from store import Store


@define(slots=True)
class Requirement:
    store: "Store" = field(default=None)

    # 这里做提前的变量准备工作．(模型转化)
    def __attrs_post_init__(self):
        print("enter post_init")
        pass

    def get_pages(self):
        model = self.store.models["arch"]
        return model.pages
