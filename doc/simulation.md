# Table of Contents

* [pydrodelta.simulation](#pydrodelta.simulation)
  * [run\_plan](#pydrodelta.simulation.run_plan)

<a id="pydrodelta.simulation"></a>

# pydrodelta.simulation

<a id="pydrodelta.simulation.run_plan"></a>

#### run\_plan

```python
@click.command()
@click.pass_context
@click.argument('config_file', type=str)
@click.option("--csv",
              "-c",
              help="Save result of analysis as .csv file",
              type=str)
@click.option("--json",
              "-j",
              help="Save result of analysis to .json file",
              type=str)
@click.option("--graph_file",
              "-g",
              help="Print topology graph in .png file",
              type=str)
@click.option("--export_corrida_json",
              "-e",
              help="Save result of simulation to .json file",
              type=str)
@click.option("--export_corrida_csv",
              "-E",
              help="Save result of simulation to .csv file",
              type=str)
@click.option("--pivot",
              "-p",
              is_flag=True,
              help="Pivot output table",
              default=False,
              show_default=True)
@click.option("--upload",
              "-u",
              is_flag=True,
              help="Upload analysis output to database API",
              default=False,
              show_default=True)
@click.option("--include_prono",
              "-P",
              is_flag=True,
              help="Concatenate series_prono to analysis output series",
              type=bool,
              default=None,
              show_default=True)
@click.option("--verbose",
              "-v",
              is_flag=True,
              help="log to stdout",
              default=False,
              show_default=True)
@click.option("--output-stats",
              "-s",
              help="output location for stats (json)",
              type=str,
              default=None)
@click.option("--output-results",
              "-R",
              help="output location for results (json)",
              type=str,
              default=None)
@click.option("--plot-var",
              "-V",
              nargs=2,
              type=(int, str),
              help="save plot of selected vars into pdf file",
              multiple=True,
              default=None)
@click.option("--pretty",
              "-r",
              is_flag=True,
              help="json pretty print",
              default=False,
              show_default=True)
@click.option("--output-analysis",
              "-a",
              help="output analysis result (json)",
              type=str,
              default=None)
@click.option("--quiet",
              "-q",
              is_flag=True,
              help="quiet mode",
              default=False,
              show_default=True)
@click.option("--upload-prono",
              "-U",
              is_flag=True,
              help="Upload simulation output to database API",
              default=False,
              show_default=True)
@click.option("--save-upload-response",
              help="save analysis output response to this file (json)",
              default=None)
@click.option(
    "--input-api",
    help=
    "Override config.input_api. sintax: token@url. Token and url of the service from where to load data",
    type=str)
@click.option(
    "--output-api",
    help=
    "Override config.output_api. sintax: token@url. Token and url of the service where to upload analysis output",
    type=str)
@click.option("--save-calibration-result",
              help="Save fitter parameters and scores as yaml",
              type=str,
              default=None)
def run_plan(self, config_file, csv, json, graph_file, export_corrida_json,
             export_corrida_csv, pivot, upload, include_prono, verbose,
             output_stats, output_results, plot_var, pretty, output_analysis,
             quiet, upload_prono, save_upload_response, input_api, output_api,
             save_calibration_result)
```

run plan from plan config file

config_file: location of plan config file (.json or .yml)

