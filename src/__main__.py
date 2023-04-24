import click


@click.group()
def bot() -> None:
    return None


@bot.command()
def cmd1() -> None:
    '''Command on bot'''
    click.echo('bot cmd1')


@bot.command()
def cmd2() -> None:
    '''Command on bot'''
    click.echo('bot cmd2')


if __name__ == '__main__':
    bot()
