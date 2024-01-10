from datetime import timedelta, datetime 
import pydrodelta.util as util
import os
import logging
from pydrodelta.a5 import createEmptyObsDataFrame, observacionesListToDataFrame, Crud
import yaml
from pandas import isna

config_file = open("%s/config/config.yml" % os.environ["PYDRODELTA_DIR"])
config = yaml.load(config_file,yaml.CLoader)
config_file.close()

input_crud = Crud(config["input_api"])
output_crud = Crud(config["output_api"])

class NodeSerie():
    def __init__(self,params):
        self.series_id = params["series_id"]
        self.type = params["tipo"] if "tipo" in params else "puntual"
        self.lim_outliers = params["lim_outliers"] if "lim_outliers" in params else None
        self.lim_jump = params["lim_jump"] if "lim_jump" in params else None
        self.x_offset = timedelta(seconds=0) if "x_offset" not in params else util.interval2timedelta(params["x_offset"]) if isinstance(params["x_offset"],dict) else params["x_offset"] # shift_by
        self.y_offset = params["y_offset"]  if "y_offset" in params else 0 # bias
        self.moving_average = util.interval2timedelta(params["moving_average"]) if "moving_average" in params else None
        self.data = None
        self.metadata = None
        self.outliers_data = None
        self.jumps_data = None
        self.csv_file = "%s/%s" % (os.environ["PYDRODELTA_DIR"],params["csv_file"]) if "csv_file" in params else None
        self.observations = util.parseObservations(params["observations"]) if "observations" in params else None
    def __repr__(self):
        return "NodeSerie(type: %s, series_id: %i, count: %i)" % (self.type, self.series_id, len(self.data if self.data is not None else 0))
    def __str__(self):
        return str(self.toDict())
    def __dict__(self):
        return {
            "series_id": self.series_id,
            "type": self.type,
            "lim_outliers": self.lim_outliers,
            "lim_jump": self.lim_jump,
            "x_offset": self.x_offset,
            "y_offset": self.y_offset,
            "moving_average": self.moving_average,
            "data": self.data.reset_index().values.tolist() if self.data is not None else None,
            "metadata": self.metadata,
            "outliers_data": self.outliers_data,
            "jumps_data": self.jumps_data
        }
    def loadData(self,timestart,timeend):
        if(self.observations is not None):
            logging.debug("Load data for series_id: %i from configuration" % (self.series_id))
            self.data = observacionesListToDataFrame(self.observations,tag="obs")
            self.metadata = {"id": self.series_id, "tipo": self.type}
        elif(self.csv_file is not None):
            logging.debug("Load data for series_id: %i from file %s" % (self.series_id, self.csv_file))
            data = util.readDataFromCsvFile(self.csv_file,self.series_id,timestart,timeend)
            self.data = observacionesListToDataFrame(data,tag="obs")
            self.metadata = {"id": self.series_id, "tipo": self.type}
        else:
            logging.debug("Load data for series_id: %i [%s to %s] from a5 api" % (self.series_id,timestart.isoformat(),timeend.isoformat()))
            self.metadata = input_crud.readSerie(self.series_id,timestart,timeend,tipo=self.type)
            if len(self.metadata["observaciones"]):
                self.data = observacionesListToDataFrame(self.metadata["observaciones"],tag="obs")
            else:
                logging.warning("No data found for series_id=%i" % self.series_id)
                self.data = createEmptyObsDataFrame(extra_columns={"tag":"str"})
            self.original_data = self.data.copy(deep=True)
            del self.metadata["observaciones"]
    def getThresholds(self):
        if self.metadata is None:
            logging.warn("Metadata missing, unable to set thesholds")
            return None
        thresholds = {}
        if self.metadata["estacion"]["nivel_alerta"]:
            thresholds["nivel_alerta"] = self.metadata["estacion"]["nivel_alerta"]
        if self.metadata["estacion"]["nivel_evacuacion"]:
            thresholds["nivel_evacuacion"] = self.metadata["estacion"]["nivel_evacuacion"]
        if self.metadata["estacion"]["nivel_aguas_bajas"]:
            thresholds["nivel_aguas_bajas"] = self.metadata["estacion"]["nivel_aguas_bajas"]
        return thresholds
    def removeOutliers(self):
        if self.lim_outliers is None:
            return False
        self.outliers_data = util.removeOutliers(self.data,self.lim_outliers)
        if len(self.outliers_data):
            return True
        else:
            return False
    def detectJumps(self):
        if self.lim_jump is None:
            return False
        self.jumps_data = util.detectJumps(self.data,self.lim_jump)
        if len(self.jumps_data):
            return True
        else:
            return False
    def applyMovingAverage(self):
        if self.moving_average is not None:
            # self.data["valor"] = util.serieMovingAverage(self.data,self.moving_average)
            self.data = util.serieMovingAverage(self.data,self.moving_average,tag_column = "tag")
    def applyTimedeltaOffset(self,row,x_offset):
        return row.name + x_offset
    def applyOffset(self):
        if self.data is None:
            logging.warn("applyOffset: self.data is None")
            return
        if not len(self.data):
            logging.warn("applyOffset: self.data is empty")
            return
        if isinstance(self.x_offset,timedelta):
            self.data.index = self.data.apply(lambda row: row.name + self.x_offset, axis=1) # self.applyTimedeltaOffset(row,self.x_offset), axis=1) # for x in self.data.index]
            self.data.index.rename("timestart",inplace=True)
        elif self.x_offset != 0:
            self.data["valor"] = self.data["valor"].shift(self.x_offset, axis = 0) 
            self.data["tag"] = self.data["tag"].shift(self.x_offset, axis = 0) 
        if self.y_offset != 0:
            self.data["valor"] = self.data["valor"] + self.y_offset
    def regularize(self,timestart,timeend,time_interval,time_offset,interpolation_limit,inline=True,interpolate=False):
        data = util.serieRegular(self.data,time_interval,timestart,timeend,time_offset,interpolation_limit=interpolation_limit,tag_column="tag",interpolate=interpolate)
        if inline:
            self.data = data
        else:
            return data
    def fillNulls(self,other_data,fill_value=None,x_offset=0,y_offset=0,inline=False):
        data = util.serieFillNulls(self.data,other_data,fill_value=fill_value,shift_by=x_offset,bias=y_offset,tag_column="tag")
        if inline:
            self.data = data
        else:
            return data
    def toCSV(self,include_series_id=False):
        if include_series_id:
            data = self.data
            data["series_id"] = self.series_id
            return data.to_csv()
        return self.data.to_csv()
    def toList(self,include_series_id=False,timeSupport=None,remove_nulls=False,max_obs_date:datetime=None):
        if self.data is None:
            return list()
        data = self.data[self.data.index <= max_obs_date] if max_obs_date is not None else self.data.copy(deep=True)
        data["timestart"] = data.index
        data["timeend"] = [x + timeSupport for x in data["timestart"]] if timeSupport is not None else data["timestart"]
        data["timestart"] = [x.isoformat() for x in data["timestart"]]
        data["timeend"] = [x.isoformat() for x in data["timeend"]]
        if include_series_id:
            data["series_id"] = self.series_id
        obs_list = data.to_dict(orient="records")
        for obs in obs_list:
            obs["valor"] = None if isna(obs["valor"]) else obs["valor"]
            obs["tag"] = None if "tag" not in obs else None if isna(obs["tag"]) else obs["tag"]
        if remove_nulls:
            obs_list = [x for x in obs_list if x["valor"] is not None] # remove nulls
        return obs_list
    def toDict(self,timeSupport=None,as_prono=False,remove_nulls=False,max_obs_date:datetime=None):
        obs_list = self.toList(include_series_id=False,timeSupport=timeSupport,remove_nulls=remove_nulls,max_obs_date=max_obs_date)
        series_table = "series" if self.type == "puntual" else "series_areal" if self.type == "areal" else "series_rast" if self.type == "raster" else "series"
        if as_prono:
            return {"series_id": self.series_id, "series_table": series_table, "pronosticos": obs_list}
        else:
            return {"series_id": self.series_id, "series_table": series_table, "observaciones": obs_list}
