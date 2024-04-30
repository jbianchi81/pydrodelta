import click

__version__ = '0.1.dev0'

import os
if "PYDRODELTA_DIR" not in os.environ:
    pydrodelta_dir = os.path.abspath(os.path.join(__file__,"../../.."))
    os.environ["PYDRODELTA_DIR"] = pydrodelta_dir

from pydrodelta.analysis import run_analysis
from pydrodelta.simulation import run_plan

@click.group()
@click.version_option(version=__version__)
def cli():
    pass


cli.add_command(run_analysis)
cli.add_command(run_plan)
