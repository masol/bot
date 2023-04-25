import esprima
import os
import textwrap
from gettext import gettext as _
import util.log as logger
from util.ast import identify


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


def loadAssign(node, ctx) -> None:
    pass


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
        # 如果argStr被'或"包围，移除两边的引号
        if (argStr.startswith('"') and argStr.endswith('"')) or (
            argStr.startswith("'") and argStr.endswith("'")
        ):
            argStr = argStr[1:-1]
        args.append(argStr)
    # 获取ctx.src的目录
    oldbase = ctx.get("base")
    ctx["base"] = os.path.dirname(ctx.get("src"))
    from store.load import load
    for arg in args:
        if not load(arg, ctx):
            logger.error(
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
