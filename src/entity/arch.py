from attrs import define, field

from entity.entity import Entity
from util.str import is_valid_string, convert_to_base36
import copy


@define(slots=True, frozen=False, eq=False)
class Data(Entity):
    type: str = field(default="Data")
    # 在humod中对dtds的索引．
    dtd: str = field(default="")
    write: bool = field(default=False)


# 条件集合,使用ast来取代，通用性表达的实现更简单．
@define(slots=True, frozen=False, eq=False)
class Condition(Entity):
    type: str = field(default="Condition")
    # 一个条件分为field, operator, value三个部分．
    # 一个条件或字符串．
    left: "list[Condition]" = field(default=None)
    op: str = field(default="")
    right: "list[Condition]" = field(default=None)

    # left和right都为空时，name保存了identifier.
    # def left_has_value(self):
    #     return not self.left == None

    # def right_has_value(self):
    #     return not self.right == None

    # def create_logic(self, conds, logicOp="and"):
    #     if isinstance(conds, Condition):
    #         conds = [conds]
    #     if isinstance(conds, list):
    #         return Condition(left=conds, op=logicOp)
    #     return None

    # 需要调用的cond默认是一个逻辑组．其它自行维护．例如根为and或根为or的情况．
    def append(self, condition, def_logic_op="and"):
        if not is_valid_string(self.op):
            self.op = def_logic_op
        # 逻辑条件想等，直接加入．
        if isinstance(condition, Condition):
            condition = [condition]

        if not isinstance(condition, list):
            raise ValueError("WRONG CONDTION VALUE")

        if self.op == def_logic_op:
            if isinstance(self.left, list):
                self.left.extend(condition)
            elif not self.left:
                self.left = condition
            else:
                raise ValueError("WRONG LOGIC CONDITION!!")
        else:
            raise ValueError("假设的根逻辑条件组合错误！！")

    # def addcond(self, left, op, right, logicOP="and"):
    #     if not is_valid_string(self.op):  # 未设置操作符，左右必定有空．
    #         self.op = logicOP
    #         if not self.left_has_value():
    #             self.left = [Condition(left=left, op=op, right=right)]
    #         elif not self.right_has_value():
    #             self.right = [Condition(left=left, op=op, right=right)]
    #         else:
    #             print("ERROR:CONDITION!!")
    #         return self
    #     elif self.op == logicOP and isinstance(self.left, list):  # 如果想等，直接加入左叶子．
    #         self.left.append(Condition(left=left, op=op, right=right))
    #         return self
    #     else:  # 将当前条件当作新条件的孩子．
    #         newcond = Condition(left=left, op=op, right=right)
    #         retcond = Condition(left=[newcond, self], op=logicOP, right=None)
    #         return retcond


@define(slots=True, frozen=False, eq=False)
class Api(Entity):
    type: str = field(default="Api")
    # 前置条件．关键字: "role"
    pre_cond: Condition = field(factory=Condition)
    # 查询参数.key为输入名称，value为q_cond中使用的名称(字段名)．可相同．
    # 名称都以_开头，内建如下几个固定值也包含_: _offset,_limit,_id.以问号?结尾，意味可选．
    q_bind: "dict" = field(factory=dict)
    # 查询条件.维护办法为根是and,第二层开始是自由条件．or或and或其它．
    q_cond: Condition = field(factory=Condition)
    # 排序,key为排序字段．value为绑定名称．desc/asc为固定值．
    order: dict = field(factory=dict)
    # 如果limit变量被绑定，则采用q_bind中传入的limit值，否则采用这里的固定值．
    # 如果limit值被设置为1,则q_bind应传入id，此时自动追加条件id=XX以及pre_cond(id is valid)
    limit: int = field(default=16)
    # 有效值，q: query, u: update/create(当q_cond为空时), c: create, d: delete
    # mode由名称的后缀来判断．
    # mode: str = field(default="q")
    # 对于u/c mode值，客户端允许传递的field,如果为空，所有都被允许．
    valid_fields: "set" = field(factory=set)
    # 查询目标表格.
    table: str = field(default="")
    # 查询的逻辑字段.
    fields: str = field(default="")
    # 本表中的额外字段,例如已批准．
    extra_fields: set = field(factory=set)
    # 后续行为列表.其成员为condition及action.
    # next: "list" = field(factory=list)
    # 由查询引发的indexed需求．key为字段名，value为索引需求(fulltext,hash)
    indexes: dict = field(factory=dict)

    # 根据q_bind的长度，分配下一个自动命名的绑定变量．
    def alloc_bind_var(self):
        next = len(self.q_bind) + 1
        return f"_{convert_to_base36(next)}"

    def mode(self):
        if is_valid_string(self.name):
            return self.name[:-1]
        return "q"


@define(slots=True, frozen=False, eq=False)
class Block(Entity):
    type: str = field(default="Block")
    # 绑定的API. 一个block最多绑定一个api,如需要多个，可以使用多个block.
    # 如果api为空，则使用第一个指定api的祖先block.
    api: str = field(default="")
    # 是否保存历史记录．历史记录以api为单元．只用于录入数据时有效．
    # history: bool = field(default=True)
    # 是否伴随页面自动触发
    tirgger: bool = field(default=False)

    # 下级block
    blocks: "list" = field(factory=list)

    # 如果是block,提示block的作用
    hints: "str" = field(default="")

    # 按钮的标签及帮助．
    label: str = field(default="")

    # 创建代码时使用，用于保存渲染之后的代码文本．
    code: str = field(default="")

    # 如果block不在子节点中，加入之．
    def ensure(self, blockortype, **kwargs):
        ret = blockortype
        if is_valid_string(blockortype):
            ret = self.create(blockortype, **kwargs)
            self.blocks.append(ret)
        elif blockortype not in self.blocks:
            self.blocks.append(blockortype)
        return ret

    # 根据类型名称，创建默认的block，并加入
    def create(self, type: str, **kwargs):
        type_dict = {
            "Block": Block,
            "Group": Group,
            "SingleValue": SingleValue,
            "Input": Input,
            "Button": Button,
            "Stream": Stream,
            "Slide": Slide,
            "Select": Select,
            "Switch": Switch,
            "Page": Page,
            "Title": Title,
            "Desc": Desc,
            "Prop": Prop,
            "Image": Image,
            "Video": Video,
            "Audio": Audio,
            "Pagination": Pagination,
            "Label": Label,
            "CondGroup": CondGroup,
        }
        Type = type_dict.get(type, Block)
        return Type(**kwargs)


# 标题元素
@define(slots=True, frozen=False, eq=False)
class Pagination(Block):
    type: str = field(default="Pagination")
    # 绑定的当前页变量名. (输入参数)
    offset: str = field(default="offset")
    # 绑定的页面数变量名．(返回值中的一个伪字段)
    maxpage: str = field(default="maxpage")
    # 每页数量，如果为空，则由uiPage写死，并写入到对应api中．
    cpp: str = field(default="")


@define(slots=True, frozen=False, eq=False)
class SingleValue(Block):
    type: str = field(default="SingleValue")
    # 绑定的参数名.以_开头的变量为输入变量，否则为输出变量．以$开头的变量为从输出变量中拷贝值,并做为输入变量．
    param: str = field(default="")
    # 默认值
    defval: str = field(default="")
    # 值类型，会自动类型转化．
    valtype: str = field(default="str")
    # 值缓存,可选session,indexedb,memory,none.(none指示此变量由api回应)
    cache: str = field(default="session")


# 组元素，将单一元素组合
@define(slots=True, frozen=False, eq=False)
class Group(Block):
    type: str = field(default="Group")
    # 本组开启一个单元，如果有值的话．并且值为单元的key．
    id: str = field(default="")


# 条件组元素
@define(slots=True, frozen=False, eq=False)
class CondGroup(Group):
    type: str = field(default="CondGroup")
    # 绑定的参数名.以_开头的变量为输入变量，否则为输出变量．以$开头的变量为从输出变量中拷贝值,并做为输入变量．
    params: "set" = field(factory=set)
    cond: Condition = field(factory=Condition)


# 标题元素
@define(slots=True, frozen=False, eq=False)
class Title(SingleValue):
    type: str = field(default="Title")


# 正文元素(desc)
@define(slots=True, frozen=False, eq=False)
class Desc(SingleValue):
    type: str = field(default="Desc")


# 标签元素.
@define(slots=True, frozen=False, eq=False)
class Label(SingleValue):
    type: str = field(default="Label")


# 属性元素(通常显示属性名和属性值,属性值比较短,例如库存．)
@define(slots=True, frozen=False, eq=False)
class Prop(SingleValue):
    type: str = field(default="Prop")


# 图片元素
@define(slots=True, frozen=False, eq=False)
class Image(SingleValue):
    type: str = field(default="Image")


# 视频元素
@define(slots=True, frozen=False, eq=False)
class Video(SingleValue):
    type: str = field(default="Video")


# 音频元素
@define(slots=True, frozen=False, eq=False)
class Audio(SingleValue):
    type: str = field(default="Audio")


# 录入框子元素．(时间，数字，文本，日期,文件...)
@define(slots=True, frozen=False, eq=False)
class Input(SingleValue):
    type: str = field(default="Input")
    # 输入的掩码，用于身份证,电话,日期等等的录入．
    mask: str = field(default="")


# 按钮，为触发型而不是trigger.
@define(slots=True, frozen=False, eq=False)
class Button(Block):
    type: str = field(default="Button")
    # 触发地址:　"page://XXX","modal://XXX#act=open|close|toggle","api://XXX"
    # 其中，page,modal无地址时，显示子block.
    href: "str" = field(default="")


# 语音/视频录入,valtype为"video"及"audio"
@define(slots=True, frozen=False, eq=False)
class Stream(SingleValue):
    type: str = field(default="Audio")
    # 最大长度，单位秒．设为0时为流录入,-1无限制
    max: int = field(default=15)


# 数字录入框子元素．
@define(slots=True, frozen=False, eq=False)
class Slide(SingleValue):
    type: str = field(default="Slide")


# 多选一子元素．
@define(slots=True, frozen=False, eq=False)
class Select(SingleValue):
    type: str = field(default="Select")
    # 有效参数值key为显示值,value为值．
    enums: "dict[str, str]" = field(factory=dict)


# 开关元素．
@define(slots=True, frozen=False, eq=False)
class Switch(SingleValue):
    type: str = field(default="Switch")
    # str类型的值为True,False.默认值为False.


@define(slots=True, frozen=False, eq=False)
class Page(Block):
    type: str = field(default="Page")
    # 所属角色，当多个角色时，用来决定"我的"导航菜单中的顺序．
    role: str = field(default="")


@define(slots=True, frozen=False, eq=False)
class Database(Entity):
    type: str = field(default="Database")


# 默认初始化的数据集
@define(slots=True, frozen=False, eq=False)
class Cfg(Entity):
    type: str = field(default="Cfg")


# 角色信息
@define(slots=True, frozen=False, eq=False)
class Role(Entity):
    type: str = field(default="Role")
    # 角色首页．
    home: str = field(default="")
    # value: 跳转的目标页面名称．
    nav: "set[str]" = field(factory=set, metadata={"childtype": str})
    # 角色对赢的id数字.
    id: int = field(default=-1)


# 资源信息
@define(slots=True, frozen=False, eq=False)
class Res(Entity):
    type: str = field(default="Res")


@define(slots=True, frozen=False, eq=False)
class Arch(Entity):
    type: str = field(default="JobDuty")
    pages: "dict[str, Page]" = field(factory=dict, metadata={"childtype": Page})
    # api的名称为"页面名_act",act为get,或由谓语衍生的多个动词,如upd.
    apis: "dict[str, Api]" = field(factory=dict, metadata={"childtype": Api})
    # 角色信息．当前版本只支持"我的"这样一种导航方式,需要知识库来细化更多导航(例如条目多时的自动二级分类)
    roles: "dict[str, Role]" = field(factory=dict, metadata={"childtype": Role})
    # 资源信息．系统中各个页面需要处理的资源．
    reses: "dict[str, Res]" = field(factory=dict, metadata={"childtype": Res})
    # 数据库的导出，要根据apis中的需求，来删除未使用的字段．
    database: "dict[str, Database]" = field(
        factory=dict, metadata={"childtype": Database}
    )
    cfg: "dict[str, Cfg]" = field(factory=dict, metadata={"childtype": Cfg})
    # 默认角色．
    anonymous: str = field(default="")

    def ensure(self, attr_name, child_name):
        attr: dict = self.getattr(attr_name)
        if child_name in attr:
            return attr[child_name]
        return self.newchild(attr_name, key=child_name)

    # 页面名为＂角色-流程-是否发起＂(行为做为状态来控制)，如果被设置为首页，则为index.html
    def ensure_page(self, pagename):
        return self.ensure("pages", pagename)

    def ensure_role(self, rolename):
        return self.ensure("roles", rolename)

    def ensure_api(self, apiname):
        return self.ensure("apis", apiname)

    @staticmethod
    def cond(left, op, right=None):
        return Condition(left=left, op=op, right=right)

    @staticmethod
    def logic_cond(left, op):
        if not isinstance(left, list):
            left = [left]
        return Condition(left=left, op=op)
