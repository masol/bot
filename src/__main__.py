import click
import click_completion
import gettext
import os
import rich

import cmds.build as buildImpl
from util.str import is_valid_string

# from cmds.build import build as buildImpl  # type: ignore[attr-defined]

BOT_VERSION = "0.0.1"

click_completion.init()

# 初始化gettext domain
# gettext.bindtextdomain('bot', \
# os.path.join(os.path.dirname(__file__), 'locales'))
# gettext.textdomain('bot')
gettext.install(
    "bot", localedir=os.path.join(os.path.dirname(__file__), "locales")
)
_ = gettext.gettext


class CustomHelp(click.Group):
    def get_usage(self, ctx: click.Context) -> str:
        """Redefine the usage statement for this command."""
        usage = super().get_usage(ctx)
        print(ctx)
        return usage.replace("Usage:", _("Usage:"))

    def format_help(
        self, ctx: click.Context, formatter: click.HelpFormatter
    ) -> None:
        # Print the usage information
        super().format_help(ctx, formatter)
        self.format_commands(ctx, formatter)
        formatter.write_paragraph()
        formatter.write_text("\nDescription.")

    # #重载format_options方法，实现自定义选项列表
    def format_options(
        self, ctx: click.Context, formatter: click.HelpFormatter
    ) -> None:
        """Redefine the option list."""
        # Get the list of options
        opts = []
        for param in self.get_params(ctx):
            rv = param.get_help_record(ctx)
            if rv is not None:
                opts.append(rv)
        # If there are no options, do nothing
        if not opts:
            return
        # Print the list of options
        with formatter.section(_("Options")):
            formatter.write_dl(opts)

    # 重载format_commands方法，实现自定义命令列表
    def format_commands(
        self, ctx: click.Context, formatter: click.HelpFormatter
    ) -> None:
        """Redefine the command list."""
        # Get the list of commands
        commands = self.list_commands(ctx)
        # If there are no commands, do nothing
        if not commands:
            return
        # Print the list of commands
        with formatter.section(_("Commands")):
            formatter.write_dl(
                [(c, self.get_command(ctx, c).__doc__ or "") for c in commands]
            )


@click.group(
    cls=CustomHelp,
    help=_("Tools for behavior-oriented software engineering methodology."),
)
def bot() -> None:
    pass
    # click.echo(os.path.dirname(__file__))


@bot.command(help="generate code from workflow")
@click.option("--verbose", "-v", is_flag=True, help="Enables verbose mode.")
@click.option(
    "--dump-model",
    "-m",
    multiple=True,
    help="Output the model with the specified name.",
)
@click.option(
    "--tolerant",
    "-t",
    is_flag=True,
    help="Tolerate a few cases of syntax errors",
)
@click.option(
    "-o",
    "--output-dir",
    type=click.Path(dir_okay=False),
    help="Directory where output files should be written.Default is target.",
)
@click.argument("src", type=str, metavar="SRC(filepath or URL)")
def build(verbose, dump_model, tolerant, output_dir, src) -> None:  # type: ignore[no-untyped-def]
    dump_models = list()
    for m in dump_model:
        if is_valid_string(m):
            dump_models.extend(m.split(','))
    # 　将参数构建为一个对象．
    opts = {
        "verbose": verbose,
        "tolerant": tolerant,
        "output_dir": output_dir,
        "dump_models": dump_models,
        "src": src,
    }
    # 　调用build模块的build函数
    buildImpl.build(opts)


build.__doc__ = _("generate code from workflow")


@bot.command(help="analysis workflow")
def analysis() -> None:
    click.echo("bot cmd analysis")


analysis.__doc__ = _("""analysis workflow""")


@bot.command(help="print current bot version")
def version() -> None:
    #    click.echo(_("BOT version: %s") % BOT_VERSION)
    rich.print(
        ("[bold]%s[/bold]: [green]%s[/green]")
        % (_("BOT version"), BOT_VERSION)
    )


version.__doc__ = _("""current version""")


if __name__ == "__main__":
    bot()
