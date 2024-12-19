import logging
import os
import sys
import click
from .config import config
from .util import ParseApiConfig

logging.basicConfig(
    filename = os.path.join(
        "/var/log",
        config["log"]["filename"]
    ), 
    level = logging.DEBUG, 
    format = "%(asctime)s:%(levelname)s:%(message)s"
)
logging.FileHandler(
    os.path.join(
        "/var/log",
        config["log"]["filename"]
    ),
    "w+"
)

from pydrodelta.topology import Topology

@click.command()
@click.pass_context
@click.argument('config_file', type=str)
@click.option("--csv", "-c", help="Save result of analysis as .csv file", type=str)
@click.option("--json", "-j", help="Save result of analysis to .json file", type=str)
@click.option("--graph_file", "-g", help="Print topology graph in .png file", type=str)
@click.option("--pivot", "-p", is_flag=True, help="Pivot output table", default=False,show_default=True)
@click.option("--upload", "-u", is_flag=True, help="Upload output to database API", default=False, show_default=True)
@click.option("--include_prono", "-P", is_flag=True, help="Concatenate series_prono to output series",type=bool, default=None, show_default=True)
@click.option("--verbose", "-v", is_flag=True, help="log to stdout", default=False, show_default=True)
@click.option("--upload_series_prono","-U", is_flag=True, help="upload [adusted] series_prono as pronosticos", type=bool, default=False, show_default=True)
@click.option("--upload_series_output_as_prono","-o", is_flag=True, help="upload series_output as pronosticos", type=bool, default=False, show_default=True)
@click.option("--plot-var", "-V", nargs=2, type=(int,str), help="save plot of selected vars into pdf file",multiple=True,default=None)
@click.option("--pretty", "-r", is_flag=True, help="json pretty print", default=False, show_default=True)
@click.option("--input-api",help="Override config.input_api. sintax: token@url. Token and url of the service from where to load data", type=str)
@click.option("--output-api",help="Override config.output_api. sintax: token@url. Token and url of the service where to upload analysis output", type=str)
def run_analysis(self,config_file,csv,json,graph_file,pivot,upload,include_prono,verbose,upload_series_prono,upload_series_output_as_prono,plot_var,pretty,input_api,output_api):
    """
    run analysis of border conditions from topology file
    
    config_file: location of config file (.json or .yml)
    """
    if verbose:
        root = logging.getLogger()
        root.setLevel(logging.DEBUG)
        handler = logging.StreamHandler(sys.stdout)
        handler.setLevel(logging.DEBUG)
        formatter = logging.Formatter("%(asctime)s:%(levelname)s:%(message)s")
        handler.setFormatter(formatter)
        root.addHandler(handler)
    input_api_config = ParseApiConfig(input_api)
    output_api_config = ParseApiConfig(output_api)

    topology = Topology.load(config_file)
    topology.batchProcessInput(
        include_prono = include_prono, 
        input_api_config = input_api_config)
    if csv is not None:
        topology.saveData(csv,pivot=pivot)
    if json is not None:
        topology.saveData(json,format="json",pivot=pivot,pretty=pretty)
    if upload:
        uploaded = topology.uploadData(include_prono=include_prono, api_config=output_api_config)
    if upload_series_prono:
        if upload_series_output_as_prono:
            topology.uploadDataAsProno(True,True,api_config=output_api_config)
        else:
            topology.uploadDataAsProno(False,True,api_config=output_api_config)
    elif upload_series_output_as_prono:
        topology.uploadDataAsProno(True,False,api_config=output_api_config)
    if graph_file is not None:
        topology.printGraph(output_file=graph_file)
    if plot_var is not None:
        for var_tuple in plot_var:
            var_id, filename = var_tuple
            logging.info("plotVariable: var_id: %s, filename: %s" % (var_id, filename))
            topology.plotVariable(var_id,output=filename)


