import click
import gettext
import os

# 初始化gettext domain
# gettext.bindtextdomain('bot', \
# os.path.join(os.path.dirname(__file__), 'locales'))
# gettext.textdomain('bot')
gettext.install(
    'bot', localedir=os.path.join(os.path.dirname(__file__), 'locales')
)
_ = gettext.gettext


@click.group()
def bot() -> None:
    click.echo(os.path.dirname(__file__))


@bot.command()
def cmd1() -> None:
    '''Command on bot'''
    click.echo(_('bot cmd1'))


@bot.command()
def cmd2() -> None:
    '''Command on bot'''
    click.echo('bot cmd2')


if __name__ == '__main__':
    bot()
