# -*- coding: utf-8 -*-
"""
:Module:            obforce.cli
:Synopsis:          Provides command discovery and installed version reporting
:Created By:        Jeff Shurtliff
:Last Modified:     Jeff Shurtliff (via GPT-6.1 Sol)
:Modified Date:     18 Oct 2026
"""

import click


@click.command(context_settings={'help_option_names': ['-h', '--help']})
@click.version_option(package_name='obforce', prog_name='obforce')
def main() -> None:
    """Discover Obforce, a local Salesforce documentation CLI under development.

    This foundation provides help and version reporting. Source collection and
    vault generation are planned for later implementation threads.
    """
    click.echo(click.get_current_context().get_help())
