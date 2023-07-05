import logging
import os
import yaml
import click
import sys
from pydrodelta.plan import Plan

config_file = open("%s/config/config.yml" % os.environ["PYDRODELTA_DIR"]) # "src/pydrodelta/config/config.json")
config = yaml.load(config_file,yaml.CLoader)
config_file.close()

logging.basicConfig(filename="%s/%s" % (os.environ["PYDRODELTA_DIR"],config["log"]["filename"]), level=logging.DEBUG, format="%(asctime)s:%(levelname)s:%(message)s")
logging.FileHandler("%s/%s" % (os.environ["PYDRODELTA_DIR"],config["log"]["filename"]),"w+")
  
# class ProcedureType():
#     def __init__(self,params):
#         self.name = params["name"]
#         self.input_names = params["input_names"] if "input_names" in params else []
#         self.output_names = params["output_names"] if "output_names" in params else []
#         self.parameter_names = params["parameter_names"] if "parameter_names" in params else []
#         self.state_names = params["state_names"] if "state_names" in params else []

# class QQProcedure(Procedure):
#     def __init__(self,params,plan):
#         super().__init__(params,plan)

# class PQProcedure(Procedure):
#     def __init__(self,params,plan):
#         super().__init__(params,plan)

# class MemProcedure(Procedure):
#     def __init__(self,params,plan):
#         super().__init__(params,plan)

# class HecRasProcedure(Procedure):
#     def __init__(self,params,plan):
#         super().__init__(params,plan)
#         hecras.createHecRasProcedure(self,params,plan)

# class LinearProcedure(Procedure):
#     def __init__(self,params,plan):
#         super().__init__(params,plan)

# procedureClassDict = {
#     "QQ": QQProcedure,
#     "PQ": PQProcedure,
#     "Mem": MemProcedure,
#     "HecRas":  HecRasProcedure,
#     "Linear": LinearProcedure
# }

@click.command()
@click.pass_context
@click.argument('config_file', type=str)
@click.option("--csv", "-c", help="Save result of analysis as .csv file", type=str)
@click.option("--json", "-j", help="Save result of analysis to .json file", type=str)
@click.option("--export_corrida_json", "-e", help="Save result of simulation to .json file", type=str)
@click.option("--export_corrida_csv", "-E", help="Save result of simulation to .csv file", type=str)
@click.option("--pivot", "-p", is_flag=True, help="Pivot output table", default=False,show_default=True)
@click.option("--upload", "-u", is_flag=True, help="Upload output to database API", default=False, show_default=True)
@click.option("--include_prono", "-P", is_flag=True, help="Concatenate series_prono to output series",type=bool, default=False, show_default=True)
@click.option("--verbose", "-v", is_flag=True, help="log to stdout", default=False, show_default=True)
@click.option("--output-stats", "-s", help="output location for stats (json)", type=str, default=None)
def run_plan(self,config_file,csv,json,export_corrida_json,export_corrida_csv,pivot,upload,include_prono,verbose,output_stats):
    """
    run plan from plan config file
    
    config_file: location of plan config file (.json or .yml)
    """
    if verbose:
        root = logging.getLogger()
        root.setLevel(logging.DEBUG)
        handler = logging.StreamHandler(sys.stdout)
        handler.setLevel(logging.DEBUG)
        formatter = logging.Formatter("%(asctime)s:%(levelname)s:%(message)s")
        handler.setFormatter(formatter)
        root.addHandler(handler)
    t_config = yaml.load(open(config_file),yaml.CLoader)
    plan = Plan(t_config)
    if output_stats is not None:
        t_config.output_stats = output_stats
    plan.execute(include_prono=include_prono,upload=False)
    if csv is not None:
        plan.topology.saveData(csv,pivot=pivot)
    if json is not None:
        plan.topology.saveData(json,format="json",pivot=pivot)
    if upload:
        plan.topology.uploadData()
        if include_prono:
            plan.topology.uploadDataAsProno()
    if export_corrida_json is not None:
        plan.toCorridaJson(export_corrida_json)
    if export_corrida_csv is not None:
        plan.toCorridaCsv(export_corrida_csv,pivot=pivot)
