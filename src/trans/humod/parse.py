import esprima
import os
import textwrap
from gettext import gettext as _

import util.log as logger
from entity.entity import Entity
from store import Store
from util.str import unquote


# 如果node是identify类型,则返回identify的名称,否则返回None
def identify(node: esprima.nodes.Node) -> str or None:
    if node.type == "Identifier":
        return node.name
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


def getentity(node, ctx) -> Entity or None:
    if node.type == "Identifier":
        name = identify(node)
        if not name:
            return None
        if name.startswith("$"):
            name = name[1:]
        inst = Store.instance()
        inst.entity(node.name)
        logger.warn(
            _('invalid node type "%s" in root expression.\n\t%s')
            % (node.type, nodestr(node, ctx))
        )
        return None
    pass


def getEntity(node, ctx) -> Entity or None:
    if node.type == "Identifier":
        store = Store.instance()
    pass


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
            _(
                "Only object definitions can be assigned to entity objects:\n\t%s"
            )
            % nodestr(node.right, ctx)
        )
        return
    # 获取左边的变量名
    name = identify(node.left)
    print(node.left)


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
        logger.error(
            _('while compiling file "%s":\n\t') % src + _("not a program")
        )
        return
    for item in ast.body:
        loadbody(item, ctx)

    # print(ast)
