import click


@click.group(short_help="dbca CLI.")
def dbca():
    """dbca CLI.
    """
    pass


@dbca.command()
@click.argument("name", default="dbca")
def command(name):
    """Docs.
    """
    click.echo("Hello, {name}!".format(name=name))


def get_commands():
    return [dbca]
