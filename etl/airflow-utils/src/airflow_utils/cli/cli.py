"""Entry point for CLI command datarobot."""

import click

import airflow_utils
from airflow_utils.cli.utils import get_commands_from_pkg


def print_version(ctx, param, value):
    """
    Output version of library.

    :param ctx:
    :param param:
    :param value:
    :return:
    """
    if not value or ctx.resilient_parsing:
        return

    click.echo("DataRobot CLI")
    click.echo('Version: {}'.format(airflow_utils.__version__))
    ctx.exit()


@click.group(context_settings={'help_option_names': ['-h', '--help']}, help="DataRobot CLI",
             commands=get_commands_from_pkg('airflow_utils.cli.commands'))
@click.option('-v', '--version', is_flag=True, callback=print_version, expose_value=False, is_eager=True,
              help="Output version")
def cli():
    """
    General CLI.

    :return:
    """
