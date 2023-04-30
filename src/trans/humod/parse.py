import esprima
import os
import textwrap
from gettext import gettext as _

import util.log as logger
from entity.entity import Entity, EntList
from util.str import unquote


# 如果node是identify类型,则返回identify的名称,否则返回None
def identify(node: esprima.nodes.Node) -> str or None:
    if node.type == "Identifier":
        return node.name
    return None


# 如果node是literal类型,则返回literal的值,否则返回None
def literal(node: esprima.nodes.Node) -> str or None:
    if node.type == "Literal":
        return node.value
    return None


# 获取node的文本内容，用于在错误信息中显示
def nodestr(node: esprima.nodes.Node, ctx: dict) -> str:  # type: ignore[type-arg]
    content: str = str(ctx.get("content"))
    nodetxt: str = str(content[node.range[0] : node.range[1]])
    showtxt: str = textwrap.shorten(nodetxt, width=10, placeholder="...")
    filename = ctx.get("src")
    lineno = node.loc.start.line
    colno = node.loc.start.column
    msg = _("%s in file %s at line %d, column %d:\n\t") % (
        showtxt,
        filename,
        lineno,
        colno,
    )
    return msg


# 将ast的node转换为value,以赋值给ent的name属性，返回None将不会更新ent的name属性
def ast2value(ent: Entity, name: str, node: esprima.nodes.Node, ctx) -> any:
    if node.type == "Literal":
        if type(node.value) == str:
            return unquote(node.value)
        return node.value
    elif node.type == "ArrayExpression":
        listent = getattr(ent, name, None)
        if not isinstance(listent, EntList):
            # 不是一个EntList对象，则AST数组必须是一个Literal数组．
            litervals = []
            for elenode in node.elements:
                if elenode.type != "Literal":
                    logger.warn(
                        _('expect Literal node, ignore an invalid element node "%s".\n\t%s')
                        % (elenode.type, nodestr(elenode, ctx))
                    )
                    continue
                value = literal(elenode)
                litervals.append(value)
            if len(litervals) > 0:
                return litervals
            return None
        # 遍历node.elements
        for elenode in node.elements:
            if elenode.type != "ObjectExpression":
                logger.warn(
                    _('expect ObjectExpression node, ignore an invalid element node "%s".\n\t%s')
                    % (node.type, nodestr(elenode, ctx))
                )
                continue
            child = listent.createchild()
            assign2ent(child, elenode, ctx)
        return None
    elif node.type == "ObjectExpression":
        child = getattr(ent, name, None)
        if not isinstance(child, Entity):
            logger.warn(
                _('expect Entity node, ignore an invalid node "%s".\n\t%s')
                % (node.type, nodestr(node, ctx))
            )
            return None
        assign2ent(child, node, ctx)
        pass
    else:
        logger.warn(
            'not type "%s" not been supported in ast2value.\n\t%s'
            % (node.type, nodestr(node, ctx))
        )
    return None


def assign2ent(ent: Entity, node: esprima.nodes.ObjectExpression, ctx) -> None:
    # print("getted entity,assign node to it!", ent, node)
    # 遍历node.properties数组,为每个值赋值．
    for propnode in node.properties:
        if propnode.type != "Property":
            logger.warn(
                _('ignore an invalid property node "%s".\n\t%s')
                % (node.type, nodestr(propnode, ctx))
            )
            continue
        # 获取属性名
        name = unquote(literal(propnode.key))
        if not name:
            logger.warn(
                _('ignore an invalid property name "%s".\n\t%s')
                % (node.type, nodestr(propnode, ctx))
            )
            continue
        # 检查属性是否存在
        if not ent.has(name):
            logger.warn(
                _('Entity "%s" has no property named "%s".\n\t%s')
                % (ent.type, name, nodestr(propnode, ctx))
            )
            continue
        # todo: 将AST赋值的实现，转化为attrs的converter.(在micro automatic pipeline支持之后)
        value = ast2value(ent, name, propnode.value, ctx)
        if value not in (None, ""):
            setattr(ent, name, value)


def getentity(node, parent: Entity, ctx) -> Entity or None:
    if node.type == "Identifier":
        # 获取左边的变量名
        name = unquote(identify(node))
        if not name:
            return None
        if name.startswith("$"):
            name = name[1:]
        refs = parent.getctxobj()
        if not refs:
            logger.warn(
                _('when getentity,can not get parent context of "%s" .\n\t%s')
                % (node.type, nodestr(node, ctx))
            )
            return None
        ent = refs.get_entity(name)
        if isinstance(ent, Entity):
            return ent
        # 创建新的实体.
        if not isinstance(parent, Entity):
            logger.warn(
                _('failed to create entity "%s" (no parent entity).\n\t%s')
                % (node.type, nodestr(node, ctx))
            )
            return None
        if (not hasattr(parent, "createchild")) or (not callable(parent.createchild)):
            logger.warn(
                _(
                    'failed to create entity "%s" (parent entity is not a container).\n\t%s'
                )
                % (node.type, nodestr(node, ctx))
            )
            return None
        child = parent.createchild(name)
        if child is None:
            logger.warn(
                _('failed to create child entity "%s".\n\t%s')
                % (name, nodestr(node, ctx))
            )
        refs.add_entity(name, child)
        return child
    elif node.type == "MemberExpression":
        # 获取左边的entity
        obj_ent = getentity(node.object, parent, ctx)
        if not isinstance(obj_ent, Entity):
            return None
        # 获取右边的属性
        return getentity(node.property, obj_ent, ctx)
    else:
        logger.warn(
            _('failed to get entity "%s"(invalid node type).\n\t%s')
            % (node.type, nodestr(node, ctx))
        )
        return None


def loadAssign(node, ctx) -> None:
    operator = unquote(node.operator)
    if operator != "=":
        logger.warn(
            _(
                "Only assignment operations are supported,but with the input of '%s':\n\t%s"
            )
            % (node.operator, nodestr(node, ctx))
        )
        return
    if node.right.type != "ObjectExpression":
        logger.warn(
            _("Only object definitions can be assigned to entity objects:\n\t%s")
            % nodestr(node.right, ctx)
        )
        return
    model: Entity = ctx.get("omodel")
    ent = getentity(node.left, model, ctx)
    if not isinstance(ent, Entity):
        logger.warn(
            _('failed to get entity "%s".\n\t%s') % (node.type, nodestr(node, ctx))
        )
        return
    # TODO: 将此实现改为entity的convert.
    assign2ent(ent, node.right, ctx)


def execFunc(node: esprima.nodes.CallExpression, ctx) -> None:
    callee = identify(node.callee)
    args = []
    for arg in node.arguments:
        argStr = identify(arg)
        if not argStr:
            argStr = str(ctx.get("content"))[arg.range[0] : arg.range[1]]
        # 如果argStr不是一个url
        if not argStr.startswith("http"):
            # 如果当前系统路径分割符不等于/,则将其替换为/
            if os.path.sep != "/":
                argStr = argStr.replace("/", os.path.sep)
        args.append(unquote(argStr))
    # 获取ctx.src的目录
    oldbase = ctx.get("base")
    ctx["base"] = os.path.dirname(ctx.get("src"))
    from .load import load

    for arg in args:
        if not load(arg, ctx):
            logger.warn(
                _('failed to load "%s" in function "%s".\n\t%s')
                % (arg, callee, nodestr(node, ctx))
            )
    ctx["base"] = oldbase


def loadexp(node: esprima.nodes.ExpressionStatement, ctx: dict) -> None:  # type: ignore[type-arg,no-untyped-def]
    expNode = node.expression
    if expNode.type == "AssignmentExpression":
        loadAssign(expNode, ctx)
    elif expNode.type == "CallExpression":
        execFunc(expNode, ctx)
    else:
        logger.error(
            _('invalid node type "%s" in root expression.\n\t%s')
            % (node.type, nodestr(expNode, ctx))
        )


def loadbody(node: esprima.nodes.Node, ctx: dict) -> None:  # type: ignore[type-arg]
    if node.type == "ExpressionStatement":
        loadexp(node, ctx)
    # elif node.type == 'ClassDeclaration'
    #     loadcls(node,ctx)
    else:
        logger.warn(
            _('invalid node type "%s" in the root of program.\n\t%s')
            % (node.type, nodestr(node, ctx))
        )
    pass


def parse(ctx: dict) -> None:  # type: ignore[type-arg]
    content: str = str(ctx.get("content"))
    src = ctx.get("src")
    try:
        # 使用esprima解析content
        ast = esprima.parseScript(
            content,
            {"range": True, "loc": True, "tolerant": ctx.get("tolerant")},
        )
    except esprima.Error as e:
        logger.error(_('while compiling file "%s":\n\t') % src + str(e))
        return

    # 如果ast根节点不是一个Program,则退出.

    if (not ast.type) or (ast.type != "Program") or (not ast.body):
        logger.error(_('while compiling file "%s":\n\t') % src + _("not a program"))
        return
    for item in ast.body:
        loadbody(item, ctx)

    # print(ast)
