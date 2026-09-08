import click
import yaml
from collections.abc import Mapping

__version__ = '0.1.dev0'

from pydrodelta.analysis import run_analysis, run_analysis_from_file
from pydrodelta.simulation import run_plan, run_plan_from_file
from pydrodelta.config import edit_config
from pydrodelta.workflow import run_workflow, run_workflow_from_file

@click.group()
@click.version_option(version=__version__)
def cli():
    pass


cli.add_command(run_analysis)
cli.add_command(run_plan)
cli.add_command(edit_config, "config")
cli.add_command(run_workflow)


@click.command()
@click.argument('config_file', type=click.Path(exists=True, dir_okay=False))
@click.option("--csv", "-c", help="Save result as .csv file", type=str)
@click.option("--json", "-j", help="Save result to .json file", type=str)
@click.option("--graph_file", "-g", help="Print topology graph in .png file", type=str)
@click.option("--export_corrida_json", "-e", help="Save result of simulation to .json file", type=str)
@click.option("--export_corrida_csv", "-E", help="Save result of simulation to .csv file", type=str)
@click.option("--pivot", "-p", is_flag=True, help="Pivot output table", default=False, show_default=True)
@click.option("--upload", "-u", is_flag=True, help="Upload output to database API", default=False, show_default=True)
@click.option("--include_prono", "-P", is_flag=True, help="Concatenate series_prono to output series", type=bool, default=None, show_default=True)
@click.option("--verbose", "-v", is_flag=True, help="log to stdout", default=False, show_default=True)
@click.option("--upload_series_prono", "-U", is_flag=True, help="upload [adjusted] series_prono as pronosticos", type=bool, default=False, show_default=True)
@click.option("--upload_series_output_as_prono", "-o", is_flag=True, help="upload series_output as pronosticos", type=bool, default=False, show_default=True)
@click.option("--plot-var", "-V", nargs=2, type=(int, str), help="save plot of selected vars into pdf file", multiple=True, default=None)
@click.option("--pretty", "-r", is_flag=True, help="json pretty print", default=False, show_default=True)
@click.option("--output-stats", "-s", help="output location for stats (json)", type=str, default=None)
@click.option("--output-results", "-R", help="output location for results (json)", type=str, default=None)
@click.option("--output-analysis", "-a", help="output analysis result (json)", type=str, default=None)
@click.option("--quiet", "-q", is_flag=True, help="quiet mode", default=False, show_default=True)
@click.option("--upload-prono", is_flag=True, help="Upload simulation output to database API", default=False)
@click.option("--save-upload-response", help="save analysis output response to this file (json)", default=None)
@click.option("--input-api", help="Override config.input_api. sintax: token@url", type=str)
@click.option("--output-api", help="Override config.output_api. sintax: token@url", type=str)
@click.option("--save-calibration-result", help="Save fitter parameters and scores as yaml", type=str, default=None)
def run(config_file, csv, json, graph_file, export_corrida_json, export_corrida_csv,
    pivot, upload, include_prono, verbose, upload_series_prono,
    upload_series_output_as_prono, plot_var, pretty, output_stats,
    output_results, output_analysis, quiet, upload_prono,
    save_upload_response, input_api, output_api, save_calibration_result):
    """Run a topology analysis or plan from CONFIG_FILE."""
    with open(config_file) as config_stream:
        config_data = yaml.safe_load(config_stream)

    if not isinstance(config_data, Mapping):
        raise click.ClickException("CONFIG_FILE must contain a mapping")
    if "procedures" in config_data:
        run_plan_from_file(
            config_file,
            csv=csv,
            json=json,
            graph_file=graph_file,
            export_corrida_json=export_corrida_json,
            export_corrida_csv=export_corrida_csv,
            pivot=pivot,
            upload=upload,
            include_prono=include_prono,
            verbose=verbose,
            output_stats=output_stats,
            output_results=output_results,
            plot_var=plot_var,
            pretty=pretty,
            output_analysis=output_analysis,
            quiet=quiet,
            upload_prono=upload_prono,
            save_upload_response=save_upload_response,
            input_api=input_api,
            output_api=output_api,
            save_calibration_result=save_calibration_result,
        )
    elif "nodes" in config_data:
        run_analysis_from_file(
            config_file,
            csv=csv,
            json=json,
            graph_file=graph_file,
            pivot=pivot,
            upload=upload,
            include_prono=include_prono,
            verbose=verbose,
            upload_series_prono=upload_series_prono,
            upload_series_output_as_prono=upload_series_output_as_prono,
            plot_var=plot_var,
            pretty=pretty,
            input_api=input_api,
            output_api=output_api,
        )
    elif "tasks" in config_data:
        run_workflow_from_file(config_file)
    else:
        raise click.ClickException(
            "CONFIG_FILE is neither a workflow, plan nor a topology configuration"
        )


cli.add_command(run)