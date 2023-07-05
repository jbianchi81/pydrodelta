import jsonschema
import yaml
from pathlib import Path
import os
from datetime import datetime 
import json
import logging
from pandas import concat

from pydrodelta.a5 import Crud, createEmptyObsDataFrame
import pydrodelta.analysis as analysis
import pydrodelta.util as util
from pydrodelta.procedure import Procedure

config_file = open("%s/config/config.yml" % os.environ["PYDRODELTA_DIR"]) # "src/pydrodelta/config/config.json")
config = yaml.load(config_file,yaml.CLoader)
config_file.close()

output_crud = Crud(config["output_api"])

schemas = {}
plan_schema = open("%s/data/schemas/json/plan.json" % os.environ["PYDRODELTA_DIR"])
schemas["plan"] = yaml.load(plan_schema,yaml.CLoader)

base_path = Path("%s/data/schemas/json" % os.environ["PYDRODELTA_DIR"])
resolver = jsonschema.validators.RefResolver(
    base_uri=f"{base_path.as_uri()}/",
    referrer=True,
)

class Plan():
    def __init__(self,params):
        jsonschema.validate(
            instance=params,
            schema=schemas["plan"],
            resolver=resolver
        )
        self.name = params["name"]
        self.id = params["id"]
        if isinstance(params["topology"],dict):
            self.topology = analysis.Topology(params["topology"])
        else:
            topology_file_path = os.path.join(os.environ["PYDRODELTA_DIR"],params["topology"])
            f = open(topology_file_path)
            self.topology = analysis.Topology(yaml.load(f,yaml.CLoader),plan=self)
            f.close()
        self.procedures = [Procedure(x,self) for x in params["procedures"]]
        self.forecast_date = util.tryParseAndLocalizeDate(params["forecast_date"]) if "forecast_date" in params else datetime.now()
        self.time_interval = util.interval2timedelta(params["time_interval"]) if "time_interval" in params else None
        if self.time_interval is not None:
            self.forecast_date = util.roundDownDate(self.forecast_date,self.time_interval)
        self.output_stats = []
        if params["output_stats"]:
            self.output_stats_file = params["output_stats"]
        else:
            self.output_stats_file = None
    def execute(self,include_prono=True,upload=True):
        """
        Runs analysis and then each procedure sequentially

        :param include_prono: if True (default), concatenates observed and forecasted boundary conditions. Else, reads only observed data.
        :type include_prono: bool
        :returns: None
        """
        self.topology.batchProcessInput(include_prono=include_prono)
        for procedure in self.procedures:
            procedure.run()
            procedure.outputToNodes()
            self.output_stats.append(procedure.procedure_function_results)
        if upload:
            self.uploadSim()
        if self.output_stats_file is not None:
            with open(self.output_stats_file,"w") as outfile:
                json.dump([o.statistics.__dict__ for o in self.output_stats],outfile) # [o.__dict__ for o in self.output_stats],outfile)
    def toCorrida(self):
        series_sim = []
        for node in self.topology.nodes:
            for variable in node.variables.values():
                if variable.series_sim is not None:
                    for serie in variable.series_sim:
                        if serie.data is None:
                            logging.warn("Missing data for series sim:%i, variable:%i, node:%i" % (serie.series_id, variable.id, node.id))
                            continue
                        series_sim.append({
                            "series_id": serie.series_id,
                            "pronosticos": serie.toList(remove_nulls=True)
                        })
        return {
            "cal_id": self.id,
            "forecast_date": self.forecast_date.isoformat(),
            "series": series_sim 
        }
    def uploadSim(self):
        corrida = self.toCorrida()
        return output_crud.createCorrida(corrida)
    def toCorridaJson(self,filename):
        """
        Guarda corrida en archivo .json
        """
        corrida = self.toCorrida()
        f = open(filename,"w")
        f.write(json.dumps(corrida))
        f.close()
    def toCorridaDataFrame(self,pivot=False):
        corrida = createEmptyObsDataFrame(extra_columns={"tag":"str","series_id":"int"})
        for node in self.topology.nodes:
            for variable in node.variables.values():
                if variable.series_sim is not None:
                    for serie in variable.series_sim:
                        if serie.data is None:
                            logging.warn("Missing data for series sim:%i, variable:%i, node:%i" % (serie.series_id, variable.id, node.id))
                            continue
                        if pivot:
                            suffix = "_%i" % serie.series_id
                            corrida = corrida.join(serie.data,rsuffix=suffix,how="outer")
                            corrida = corrida.rename(columns={"valor_%i" % serie.series_id: str(serie.series_id)})
                        else:
                            data = serie.data.copy()
                            data["series_id"] = serie.series_id
                            corrida = concat([corrida,data])
        if pivot:
            del corrida["valor"]
            del corrida["tag"]
            del corrida["series_id"]
        return corrida
                
    def toCorridaCsv(self,filename,pivot=False,include_header=True):
        """
        Guarda corrida en archivo .csv
        """
        corrida = self.toCorridaDataFrame(pivot=pivot)
        corrida.to_csv(filename,header=include_header)
