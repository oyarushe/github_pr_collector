"""CLI general utils."""

import importlib
import os.path
import pkgutil

import click


def get_commands_from_pkg(pkg) -> dict:
    """
    Get Click commands from specified package.

    :param pkg: path to packages with commands
    :return:
    """
    pkg_obj = importlib.import_module(pkg)

    pkg_path = os.path.dirname(pkg_obj.__file__)

    commands = {}
    for module in pkgutil.iter_modules([pkg_path]):
        module_obj = importlib.import_module("{}.{}".format(pkg, module[1]))
        if not module[2]:
            commands[module[1].replace('_', '-')] = module_obj.main

        else:
            commands[module[1].replace('_', '-')] = click.Group(
                context_settings={'help_option_names': ['-h', '--help']},
                help=module_obj.__doc__,
                commands=get_commands_from_pkg("{}.{}".format(pkg, module[1]))
            )

    return commands
