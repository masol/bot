from attrs import define, field, fields
from .str import convert_to_base36


# 将一组名称映射为范围内的短名称(可用)．
@define(slots=True, frozen=False, eq=False)
class Namer:
    # 默认前缀
    prefix: str = field(default="")
    # 默认后缀
    suffix: str = field(default="")
    # 已使用名称的字典
    names: dict = field(factory=dict)
    # 保留名称的列表
    reserved: dict = field(factory=dict)
    # 计数器，如果设置为-1,使用names的长度做为自动计数器．
    count: int = field(default=-1)

    def name(self,name):
        if name in self.reserved:
            return self.reserved[name]
        if name in self.names:
            return self.names[name]
        count = self.count
        if self.count == -1:
            count = len(self.names)
        newname = self.prefix + convert_to_base36(count) + self.suffix
        if self.count != -1:
            self.count += 1
        self.names[name] = newname
        return newname
