from datetime import timedelta, datetime 
import pydrodelta.util as util
import os
import logging
from .a5 import createEmptyObsDataFrame, observacionesListToDataFrame, Crud
from pandas import isna, DataFrame
from .config import config
from typing import Union, List, Tuple
from .types.tvp import TVP
from .types.series_dict import SeriesDict
from .types.series_prono_dict import SeriesPronoDict
from .descriptors.int_descriptor import IntDescriptor
from .descriptors.string_descriptor import StringDescriptor
from .descriptors.float_descriptor import FloatDescriptor
from .descriptors.duration_descriptor import DurationDescriptor
from .descriptors.duration_descriptor_default_none import DurationDescriptorDefaultNone
from .descriptors.dict_descriptor import DictDescriptor
from .descriptors.dataframe_descriptor import DataFrameDescriptor
from .descriptors.bool_descriptor import BoolDescriptor
import json
import yaml
from .base import Base

class NodeSerie(Base):
    """Represents a timestamped series of observed or simulated values for a variable in a node. """
    
    series_id = IntDescriptor()
    """Identifier of the series. If csv_file is set, reads the column identified in the header with this id. Else, unless observations is set, retrieves the identified series from the input api"""
    
    type = StringDescriptor()
    """Type of the series (only for retrieval from input api). One of 'puntual', 'areal', 'raster'"""
    
    @property
    def lim_outliers(self) -> Tuple[float,float]:
        """Minimum and maximum values for outliers removal (2-tuple of float)"""
        return self._lim_outliers
    @lim_outliers.setter
    def lim_outliers(
        self,
        values : Tuple[float,float]
        ) -> None:
        if values is None:
            self._lim_outliers = None
        elif isinstance(values,(tuple, list)):
            if len(values) < 2:
                raise ValueError("lim_outliers must be of length 2")
            else:
                self._lim_outliers = (values[0],values[1])
        else:
            raise ValueError("lim_outliers must be a 2-tuple of floats")
    
    lim_jump = FloatDescriptor()
    """Maximum absolute value for jump detection"""
    
    x_offset = DurationDescriptor()
    """Time offset applied to the timestamps of the input data on import"""
    
    y_offset = FloatDescriptor()
    """Offset applied to the values of the input data on import"""
    
    moving_average = DurationDescriptorDefaultNone()
    """Size of the time window used to compute a moving average to the input data"""
    
    data = DataFrameDescriptor()
    """DataFrame containing the timestamped values. Index is the time (with time zone), column 'valor' contains the values (floats) and column 'tag' contains the tag indicating the origin of the value (one of: observed, simulated, interpolated, moving_average, extrapolated, derived)"""
    
    metadata = DictDescriptor()
    """Metadata of the series"""
    
    outliers_data = DataFrameDescriptor()
    """Data rows containing removed outliers"""
    
    jumps_data = DataFrameDescriptor()
    """Data rows containing detected jumps"""
    
    csv_file = StringDescriptor()
    """Read data from this csv file. The csv file must have one column for the timestamps called 'timestart' and one column per series of data with the series_id in the header"""

    json_file = StringDescriptor()
    """Read data from this json or yaml file. The file must validate against a5 'series' schema, with 'observaciones' key containing a list of time value pairs"""

    @property
    def observations(self) -> List[TVP]:
        """Time-value pairs of data. List of dicts {'timestart':datetime, 'valor':float}, or list of 2-tuples (datetime,float)"""
        return self._observations
    @observations.setter
    def observations(
        self,
        values : List[TVP]
        ) -> None:
        self._observations = util.parseObservations(values) if values is not None else None
    
    save_post = StringDescriptor()
    """Save upload payload into this file"""
    
    comment = StringDescriptor()
    """Comment about this series"""
    
    name = StringDescriptor()
    """Series name"""
    
    output_file = StringDescriptor()
    """ Save analysis results into this file"""

    output_format = StringDescriptor()
    """File format for output_file. Defaults to json"""

    output_schema = StringDescriptor()
    """JSON schema for output_file. Defaults to dict"""

    required = BoolDescriptor()
    """Raise error if no data found"""

    agg_func = StringDescriptor()
    """"Aggregate observations using this aggregate function. If set, interpolation is not performed"""

    def __init__(
        self,
        series_id : int,
        tipo : str = "puntual",
        lim_outliers : Tuple[float,float] = None,
        lim_jump : float = None,
        x_offset : timedelta = timedelta(seconds=0),
        y_offset : float = 0,
        moving_average : timedelta = None,
        csv_file : str = None,
        observations : Union[List[TVP],List[Tuple[datetime,float]]] = None,
        save_post : str = None,
        comment : str = None,
        name : str = None,
        node_variable = None,
        json_file : str = None,
        output_file : str = None,
        output_format : str = "json",
        output_schema : str = "dict",
        required : bool = False,
        agg_func : str = None,
        **kwargs
        ):
        """
        Parameters:
        -----------
        series_id : int
            Identifier of the series. If csv_file is set, reads the column identified in the header with this id. Else, unless observations is set, retrieves the identified series from the input api
        
        tipo : str = "puntual"
            Type of the series (only for retrieval from input api). One of 'puntual', 'areal', 'raster'
        
        lim_outliers : Tuple[float,float] = None
            Minimum and maximum values for outliers removal (2-tuple of float)

        lim_jump : float = None
            Maximum absolute value for jump detection

        x_offset : timedelta = timedelta(seconds=0)
            Apply this time offset to the timestamps of the input data

        y_offset : float = 0
            Apply this offset to the values of the input data

        moving_average : timedelta = None
            Compute a moving average using a time window of this size to the input data
         
        csv_file : str = None
            Read data from this csv file. The csv file must have one column for the timestamps called 'timestart' and one column per series of data with the series_id in the header

        observations : Union[List[TVP],List[Tuple[datetime,float]]] = None
            Time-value pairs of data. List of dicts {'timestart':datetime, 'valor':float}, or list of 2-tuples (datetime,float)

        save_post : str = None
            Save upload payload into this file
            
        node_variable : NodeVariable = None
            NodeVariable of the Topology that contains this Series
        
        json_file : str = None
            Read data from this json or yaml file. The file must validate against a5 'series' schema, with 'observaciones' key containing a list of time value pairs
        
        output_file = StringDescriptor()
            Save analysis results into this file

        output_format = StringDescriptor()
            File format for output_file. Defaults to json

        output_schema = StringDescriptor()
            JSON schema for output_file. Defaults to dict
        
        required : bool = False
            Raise error if no data found

        agg_func : str = None
            Aggregate observations using this aggregate function. If set, interpolation is not performed

        """
        super().__init__(**kwargs)
        self.series_id = series_id
        self.type = tipo
        self.lim_outliers : Tuple[float,float] = lim_outliers
        self.lim_jump = lim_jump
        self.x_offset = x_offset # util.interval2timedelta(x_offset) if isinstance(x_offset,dict) else x_offset # shift_by
        self.y_offset = y_offset # bias
        self.moving_average = util.interval2timedelta(moving_average) if moving_average is not None else None
        self.data = None
        self.metadata = None
        self.outliers_data = None
        self.jumps_data = None
        self.csv_file = os.path.join(
            config["PYDRODELTA_DIR"],
            csv_file
            ) if csv_file is not None else None
        self.observations = observations
        self.save_post = save_post
        self.comment = comment
        self.name = name
        self._variable = node_variable
        self.json_file = os.path.join(
            config["PYDRODELTA_DIR"],
            json_file
            ) if json_file is not None else None
        self.output_file = output_file
        self.output_format = output_format
        self.output_schema = output_schema
        self.required = required
        self.agg_func = agg_func
    
    def __repr__(self):
        return "NodeSerie(type: %s, series_id: %i, count: %i)" % (self.type, self.series_id, len(self.data) if self.data is not None else 0)
    
    def toDict(self) -> dict:
        """Convert series to dict"""
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
            "jumps_data": self.jumps_data,
            "required": self.required
        }

    def assertNotEmpty(self) -> None:
        if self.data is None:
            raise ValueError("data is not defined")
        elif not isinstance(self.data,DataFrame):
            raise ValueError("data is not an instance of DataFrame")
        elif "valor" not in self.data.columns.to_list():
            raise ValueError("valor column missing from data")
        elif not len(self.data["valor"]):
            raise ValueError("valor column of data is of null length")
        elif not len(self.data["valor"].dropna()):
            raise ValueError("valor column of data has no non-null values")

    def loadData(
        self,
        timestart : datetime,
        timeend : datetime,
        input_api_config : dict = None,
        no_metadata : bool = False,
        tag : str = "obs"
        ) -> None:
        """Load data from source according to configuration. 
        
        Priority is in this order: 
        - if .observations is set, loads time-value pairs from there, 
        - else if .csv_file is set, loads data from said csv file, 
        - else if .json_file is set, loads data from said json (or yaml) file
        - else loads from input api the series of id .series_id and of type .type
        
        Parameters:
        -----------
        timestart : datetime
            Begin time of the timeseries
        
        timeend : datetime
            End time of the timeseries
        
        input_api_config : dict
            Api connection parameters. Overrides self._variable._node._crud and global config.input_api 

        no_metadata : bool = True
            Don't retrieve metadata
            
            Properties:
            - url : str
            - token : str
            - proxy_dict : dict
        
        tag : str = "obs"
            Tag observations with this string
        """
        timestart = util.tryParseAndLocalizeDate(timestart)
        timeend = util.tryParseAndLocalizeDate(timeend)
        if(self.observations is not None):
            logging.debug("Load data for series_id: %i from configuration" % (self.series_id))
            data = observacionesListToDataFrame(self.observations,tag=tag)
            self.data = data[(data.index >= timestart) & (data.index <= timeend)]
            self.metadata = {"id": self.series_id, "tipo": self.type}
        elif(self.csv_file is not None):
            logging.debug("Load data for series_id: %i from file %s" % (self.series_id, self.csv_file))
            data = util.readDataFromCsvFile(self.csv_file,self.series_id,timestart,timeend)
            self.data = observacionesListToDataFrame(data,tag=tag)
            self.metadata = {"id": self.series_id, "tipo": self.type}
        elif(self.json_file is not None):
            logging.debug("Load data for series_id: %i from file %s" % (self.series_id, self.json_file))
            series = yaml.load(open(self.json_file,"r",encoding="utf-8"),yaml.CLoader)
            #,self.series_id,timestart,timeend)
            if isinstance(series,list):
                logging.debug("Parsed json is a list")
                self.data = observacionesListToDataFrame(series,tag=tag)
                self.metadata = {"id": self.series_id, "tipo": self.type}
            elif "observaciones" in series:
                self.data = observacionesListToDataFrame(series["observaciones"],tag=tag)
                self.metadata = {"id": series["id"] if "id" in series else self.series_id, "tipo": series["tipo"] if "tipo" in series else self.type}
            else:
                raise KeyError("Observaciones key not found in file " % self.json_file)
        else:
            if self._variable is not None and self._variable.time_support is not None:
                timeend = timeend + self._variable.time_support
            logging.debug("Load data for series_id: %i [%s to %s] from a5 api" % (self.series_id,timestart.isoformat(),timeend.isoformat()))
            crud = Crud(**input_api_config) if input_api_config is not None else self._variable._node._crud if self._variable is not None and self._variable._node is not None else self.input_crud
            self.metadata = crud.readSerie(
                self.series_id,
                timestart,
                timeend,
                tipo = self.type, 
                no_metadata = no_metadata)
            if len(self.metadata["observaciones"]):
                self.data = observacionesListToDataFrame(self.metadata["observaciones"],tag=tag)
            else:
                logging.warning("No data found for series_id=%i" % self.series_id)
                self.data = createEmptyObsDataFrame(extra_columns={"tag":"str"})
            self.original_data = self.data.copy(deep=True)
            del self.metadata["observaciones"]
    
    def saveData(
        self,
        output_file = None,
        format : str = None,
        schema : str = None
        ) -> None:
        """Print data into file 

        Args:
            output_file (_type_): path of output file relative to config["PYDRODELTA_DIR"]. Defaults to self.output_file
            format (str, optional): File format (json, yaml, csv). Defaults to "json".
            schema (str, optional): schema of json object (dict, list). Defaults to "dict".
        """
        if output_file is None:
            if self.output_file is None:
                raise ValueError("Missing output_file or self.output_file")
            else:
                output_file = self.output_file
        try:
            f = open(
                os.path.join(
                    config["PYDRODELTA_DIR"], 
                    output_file
                ),
                "w"
            )
        except OSError as e:
            raise OSError("Couln't open file %s for writing: %s" % (output_file, e))
        format = format if format is not None else self.output_format if self.output_format is not None else "json"
        schema = schema if schema is not None else self.output_schema if self.output_schema is not None else "dict"
        if format == "json":
            if schema == "dict":
                json.dump(self.toDict(),f)
            elif schema == "list":
                json.dump(self.toList(),f)
            else:
                raise ValueError("Invalid schema. Options: dict, list")
        elif format == "yaml":
            if schema == "dict":
                yaml.dump(self.toDict(),f)
            elif schema == "list":
                yaml.dump(self.toList(),f)
            else:
                raise ValueError("Invalid schema. Options: dict, list")
        elif format == "csv":
            f.write(self.toCSV())
        else:
            raise ValueError("Invalid format. Options: json, csv")
        f.close()

    def getThresholds(self) -> dict:
        """Read level threshold information from .metadata"""
        if self.metadata is None:
            logging.warn("Metadata missing at serie %i, unable to set thesholds" % self.series_id)
            return None
        thresholds = {}
        if "estacion" not in self.metadata:
            logging.warn("Estacion missing from metadata at serie %i, unable to set thesholds" % self.series_id)
            return None
        if self.metadata["estacion"]["nivel_alerta"]:
            thresholds["nivel_alerta"] = self.metadata["estacion"]["nivel_alerta"]
        if self.metadata["estacion"]["nivel_evacuacion"]:
            thresholds["nivel_evacuacion"] = self.metadata["estacion"]["nivel_evacuacion"]
        if self.metadata["estacion"]["nivel_aguas_bajas"]:
            thresholds["nivel_aguas_bajas"] = self.metadata["estacion"]["nivel_aguas_bajas"]
        return thresholds
    
    def removeOutliers(self) -> bool:
        """If .lim_outliers is set, removes outilers and returns True if any outliers were removed. Removed data rows are saved into .outliers_data"""
        if self.lim_outliers is None:
            return False
        self.outliers_data = util.removeOutliers(self.data,self.lim_outliers)
        if len(self.outliers_data):
            logging.warning("Se encontraron %d outliers en la serie %d, variable %d, nodo %s" % (len(self.outliers_data), self.series_id, self._variable.id, str(self._variable._node.id)))
            return True
        else:
            return False
    
    def detectJumps(self) -> bool:
        """If lim_jump is set, detects jumps. Returns True if any jumps were found. Data rows containing jumps are saved into .jumps_data"""
        if self.lim_jump is None:
            return False
        self.jumps_data = util.detectJumps(self.data,self.lim_jump)
        if len(self.jumps_data):
            return True
        else:
            return False
    
    def applyMovingAverage(self) -> None:
        """If .moving_average is set, apply a moving average with a time window size equal to .moving_average to the values of the series"""
        if self.moving_average is not None:
            # self.data["valor"] = util.serieMovingAverage(self.data,self.moving_average)
            self.data = util.serieMovingAverage(self.data,self.moving_average,tag_column = "tag")
    
    def applyTimedeltaOffset(
        self,
        row,
        x_offset) -> datetime:
        return row.name + x_offset
    
    def applyOffset(self) -> None:
        """Applies .x_offset (time axis) and .y_offset (values axis) to the data"""
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
    
    def regularize(
        self,
        timestart : datetime,
        timeend : datetime,
        time_interval : timedelta,
        time_offset : timedelta,
        interpolation_limit : Union[timedelta,int],
        inline : bool = True,
        interpolate : bool = False,
        agg_func : str = None
        ) -> Union[None,DataFrame]:
        """Regularize the time step of the timeseries
        
        Parameters:
        -----------
        timestart : datetime
            Begin time of the output regular timeseries

        timeend : datetime
            End time of the output regular timeseries

        time_interval : timedelta
            time step of the output regular timeseries

        time_offset : timedelta
            Start time of the day of the output regular timeseries (overrides that of timestart)

        interpolation_limit : timedelta or int
            Maximum number of time steps to interpolate (default: 1)
        
        inline : bool = True
            If True, saves output regular timeseries to .data. Else, returns output regular timeseries
        
        interpolate : bool = False
            If True, interpolate missing values
            
        agg_func : str = None
            Aggregate observations of data using agg_func function. If set, interpolation is not performed"""
        agg_func = agg_func if agg_func is not None else self.agg_func
        interpolation_limit = int(interpolation_limit / time_interval) if type(interpolation_limit) == timedelta else interpolation_limit 
        data = util.serieRegular(self.data,time_interval,timestart,timeend,time_offset,interpolation_limit=interpolation_limit,tag_column="tag",interpolate=interpolate, agg_func = agg_func)
        if inline:
            self.data = data
        else:
            return data
    
    def fillNulls(
        self,
        other_data : DataFrame,
        fill_value : float = None,
        x_offset : int = 0,
        y_offset : float = 0,
        inline : bool = False
        ) -> Union[None,DataFrame]:
        """Fills missing values of .data from other_data, optionally applying x_offset and y_offset. If for a missing value in .data, other_data is also missing, fill_value is set.
        
        Parameters:
        -----------
        other_data : DataFrame
            Timeseries data to be used to fill missing values in .data. Index must be the localized time and a column 'valor' must contain the values

        fill_value : float = None
            If for a missing value in .data, other_data is also missing, set this value.

        x_offset : int = 0
            Shift other_data this number of rows

        y_offset : float = 0
            Apply this offset to other_data values

        inline : bool = False
            If True, save null-filled timeseries into .data. Else return null-filled timeseries"""
        data = util.serieFillNulls(self.data,other_data,fill_value=fill_value,shift_by=x_offset,bias=y_offset,tag_column="tag")
        if inline:
            self.data = data
        else:
            return data
    
    def toCSV(
        self,
        include_series_id : bool = False
        ) -> str:
        """Convert timeseries into csv string
        
        Parameters:
        -----------
        include_series_id : bool = False
            Add a column with series_id"""
        if self.data is None:
            logging.warn("Series %i data is None, returning only header")
            if include_series_id:
                return "timestart,valor,%i" % self.series_id
            else:
                return "timestart,valor"
        if include_series_id:
            data = self.data
            data["series_id"] = self.series_id
            return data.to_csv()
        return self.data.to_csv()
    
    def toList(
        self,
        include_series_id : bool = False,
        timeSupport : timedelta = None,
        remove_nulls : bool = False,
        max_obs_date : datetime = None,
        qualifiers : List[str] = None,
        value_key : str = "valor"
        ) -> List[TVP]:
        """Convert timeseries to list of time-value pair dicts
        
        Parameters:
        -----------
        include_series_id : bool = False
            Add series_id to TVP dicts

        timeSupport : timedelta = None
            Time support of the timeseries (i.e., None for instantaneous observations, 1 day for daily mean)

        remove_nulls : bool = False
            Remove null values

        max_obs_date : datetime = None
            Remove data beyond this date

        qualifiers : List[str] = None
            Generate additional time-value pairs using the values of this qualifier keys

        value_key : str = "valor"
            Use the values of this key as the value for the observations 

        Returns:
        --------
        list of time-value pair dicts : List[TVP]"""
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
        qualifier_obs = []
        for obs in obs_list:
            obs[value_key] = None if isna(obs[value_key]) else obs[value_key]
            obs["tag"] = None if "tag" not in obs else None if isna(obs["tag"]) else obs["tag"]
            if qualifiers is not None:
                for qualifier in qualifiers:
                    if qualifier in obs and not isna(obs[qualifier]):
                        new_obs = {
                            "timestart": obs["timestart"],
                            "timeend": obs["timeend"],
                            "valor":  obs[qualifier],
                            "qualifier": qualifier
                        }
                        if include_series_id:
                            new_obs["series_id"] = self.series_id
                        qualifier_obs.append(new_obs)
                    else:
                        logging.warn("Qualifier %s not found in data at timestart %s" % (qualifier, obs["timestart"]))
            obs["valor"] = obs[value_key]
            if qualifiers is not None:
                obs["qualifier"] = "main"
        obs_list = [*obs_list, *qualifier_obs]
        if remove_nulls:
            obs_list = [x for x in obs_list if x["valor"] is not None] # remove nulls
        return obs_list
    
    def toDict(
        self,
        timeSupport : timedelta = None,
        as_prono : bool = False,
        remove_nulls : bool = False,
        max_obs_date : datetime = None,
        qualifiers : List[str] = None,
        value_key : str = "valor"
        ) -> Union[SeriesDict, SeriesPronoDict]:
        """Convert timeseries to series dict
        
        Parameters:
        -----------
        timeSupport : timedelta = None
            Time support of the timeseries (i.e., None for instantaneous observations, 1 day for daily mean)
        as_prono : bool = False
            Return SeriesPronoDict instead of SeriesDict
        
        remove_nulls : bool = False
            Remove null values
        
        max_obs_date : datetime = None
            Remove data beyond this date

        qualifiers : List[str] = None
            Generate additional time-value pairs using the values of this qualifier keys

        value_key : str = None
            Use the values of this key as the value for the observations
        Returns:
        --------
        Dict containing
        - series_id: int
        - tipo: str
        - observaciones (or pronosticos, if as_prono=True): list of dict"""
        obs_list = self.toList(include_series_id=False,timeSupport=timeSupport,remove_nulls=remove_nulls,max_obs_date=max_obs_date, qualifiers = qualifiers, value_key = value_key)
        series_table = self.getSeriesTable()
        if as_prono:
            return {"series_id": self.series_id, "series_table": series_table, "pronosticos": obs_list}
        else:
            return {"series_id": self.series_id, "series_table": series_table, "observaciones": obs_list}
    
    def getSeriesTable(self) -> str:
        """Retrieve series table name (of a5 schema) for this timeseries"""
        return "series" if self.type == "puntual" else "series_areal" if self.type == "areal" else "series_rast" if self.type == "raster" else "series"
