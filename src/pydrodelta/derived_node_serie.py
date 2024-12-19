from .derived_origin import DerivedOrigin
from .interpolated_origin import InterpolatedOrigin
import logging
from datetime import timedelta
from .a5 import createEmptyObsDataFrame
from .util import applyTimeOffsetToIndex
from .types.derived_origin_dict import DerivedOriginDict
from .types.interpolated_origin_dict import InterpolatedOriginDict
from .types.tvp import TVP
from .descriptors.dataframe_descriptor import DataFrameDescriptor
from .descriptors.string_descriptor import StringDescriptor
from .config import config 
from typing import Union, List
from pandas import Series
import os
import json
import yaml

class DerivedNodeSerie:
    """
    Represents a timeseries of a variable at a node derived or interpolated from another timeseries, i.e. of the same variable at a nearby node or another variable at the same (or nearby) node
    """
    @property
    def derived_from(self) -> DerivedOrigin:
        """Derivation configuration"""
        return self._derived_from
    @derived_from.setter
    def derived_from(
        self,
        derived_from : DerivedOriginDict
        ) -> None:
        self._derived_from = derived_from if isinstance(derived_from,DerivedOrigin) else DerivedOrigin(**derived_from,topology=self._topology) if derived_from is not None else None

    @property
    def interpolated_from(self) -> InterpolatedOrigin:
        """Interpolation configuration"""
        return self._interpolated_from
    @interpolated_from.setter
    def interpolated_from(
        self,
        interpolated_from : InterpolatedOriginDict
        ) -> None: 
            self._interpolated_from = interpolated_from if isinstance(interpolated_from,InterpolatedOrigin) else InterpolatedOrigin(**interpolated_from,topology=self._topology) if interpolated_from is not None else None
    
    data = DataFrameDescriptor()
    """DataFrame containing the timestamped values. Index is the time (with time zone), column 'valor' contains the values (floats) and column 'tag' contains the tag indicating the origin of the value (one of: observed, simulated, interpolated, moving_average, extrapolated, derived)"""

    output_file = StringDescriptor()
    """Save analysis results into this file"""

    output_format = StringDescriptor()
    """File format for output_file. Defaults to json"""

    output_schema = StringDescriptor()
    """JSON schema for output_file. Defaults to dict"""


    def __init__(
        self,
        topology,
        series_id : int = None,
        derived_from : Union[DerivedOrigin,DerivedOriginDict] = None,
        interpolated_from : Union[InterpolatedOrigin,InterpolatedOriginDict] = None,
        output_file : str = None,
        output_format : str = "json",
        output_schema : str = "dict"
        ):
        """
        Parameters:
        -----------
        topology : Topology

            Topology that contains the node_variable that contains this series and the node_variable pointed out by derived_from/interpolated_from
        
        series_id : int

            Series identifier

        derived_from : DerivedOriginDict = None

            Derivation configuration
            
        interpolated_from : InterpolatedOriginDict = None
        
        """
        self.series_id = series_id
        self._topology = topology
        self.derived_from = derived_from
        self.interpolated_from = interpolated_from
        self.data = None
        self.output_file = output_file
        self.output_format = output_format
        self.output_schema = output_schema
    
    def deriveTag(
        self,
        row : Series,
        tag_column : str,
        tag : str = "derived"
        ) -> str:
        """Generate tag for derived row"""
        if row[tag_column] is None:
            return tag
        else:
            return "%s,%s" % (row[tag_column], tag)
    def deriveOffsetIndex(
        self,
        row : Series,
        x_offset : int
        ) -> Union[int,timedelta]:
        """Apply offset to index of row"""
        return row.name + x_offset
    def derive(
        self,
        keep_index : bool = True
        ) -> None:
        """Derive this series from .derived_origin
        
        Parameters:
        -----------
        keep_index : bool = True

            Don't overwrite index (apply offset in-place)
        """
        if self.derived_from is not None:
            logging.debug("Deriving %i from %s" % (self.series_id, self.derived_from.origin.name))
            if not len(self.derived_from.origin.data):
                logging.warn("No data found to derive from origin. Skipping derived node")
                self.data = createEmptyObsDataFrame()
                return
            self.data = self.derived_from.origin.data[["valor","tag"]] # self.derived_from.origin.series[0].data[["valor",]]
            if isinstance(self.derived_from.x_offset,timedelta):
                self.data["valor"] = self.data["valor"] + self.derived_from.y_offset
                self.data.index = self.data.apply(lambda row: self.deriveOffsetIndex(row,self.derived_from.x_offset),axis=1)# for x in self.data.index]
                self.data["tag"] = self.data.apply(lambda row: self.deriveTag(row,"tag"),axis=1) # ["derived" if x is None else "%s,derived" % x for x in self.data.tag]
            else:
                self.data["valor"] = self.data["valor"].shift(self.derived_from.x_offset, axis = 0) + self.derived_from.y_offset
            self.data["tag"] = self.data.apply(lambda row: self.deriveTag(row,"tag"),axis=1) #["derived" if x is None else "%s,derived" % x for x in self.data.tag]
            if hasattr(self.derived_from.origin,"max_obs_date"):
                self.max_obs_date = self.derived_from.origin.max_obs_date
        elif self.interpolated_from is not None:
            logging.debug("Interpolating %i from %s and %s" % (self.series_id, self.interpolated_from.origin_1.name, self.interpolated_from.origin_2.name))
            if not len(self.interpolated_from.origin_1.data) or not len(self.interpolated_from.origin_2.data):
                logging.warn("No data found to derive from origin. Skipping derived node")
                self.data = createEmptyObsDataFrame()
                return
            self.data = self.interpolated_from.origin_1.data[["valor","tag"]] # self.interpolated_from.origin_1.series[0].data[["valor",]]
            self.data = self.data.join(self.interpolated_from.origin_2.data[["valor","tag"]],how='left',rsuffix="_other") # self.data.join(self.interpolated_from.origin_2.series[0].data[["valor",]],how='left',rsuffix="_other")
            self.data["valor"] = self.data["valor"] * (1 - self.interpolated_from.interpolation_coefficient) + self.data["valor_other"] * self.interpolated_from.interpolation_coefficient
            self.data["tag"] = self.data.apply(lambda row: self.deriveTag(row,"tag","interpolated"),axis=1) #["interpolated" if x is None else "%s,interpolated" % x for x in self.data.tag]
            del self.data["valor_other"]
            del self.data["tag_other"]
            if isinstance(self.interpolated_from.x_offset,timedelta):
                if keep_index:
                    self.data = applyTimeOffsetToIndex(self.data,self.interpolated_from.x_offset)
                else:
                    self.data.index = self.data.apply(lambda row: self.deriveOffsetIndex(row,self.interpolated_from.x_offset),axis=1) # for x in self.data.index]
            else:
                self.data[["valor","tag"]] = self.data[["valor","tag"]].shift(self.interpolated_from.x_offset, axis = 0)    
            if hasattr(self.interpolated_from.origin_1,"max_obs_date"):
                self.max_obs_date = self.interpolated_from.origin_1.max_obs_date
            
    def toCSV(
        self,
        include_series_id : bool = False
        ) -> str:
        """Convert series to csv string
        
        Parameters:
        -----------
        include_series_id : bool = False
        
            Add series_id column
        
        Returns:
        --------
        csv string : str
        """
        if include_series_id:
            data = self.data
            data["series_id"] = self.series_id
            return data.to_csv()
        return self.data.to_csv()
    def toList(
        self,
        include_series_id : bool = False,
        timeSupport : timedelta = None
        ) -> List[TVP]:
        """
        Convert series to list of time-value pair dicts

        Parameters:
        -----------
        include_series_id : bool = False

            Add series_id property

        timeSupport : timedelta = None

            Time support of the timeseries (i.e., None for instantaneous observations, 1 day for daily mean)

        Returns:
        --------
        List of time-value pair dicts : List[TVP]
        """
        data = self.data
        data["timestart"] = data.index
        data["timeend"] = [x + timeSupport for x in data["timestart"]] if timeSupport is not None else data["timestart"]
        data["timestart"] = [x.isoformat() for x in data["timestart"]]
        data["timeend"] = [x.isoformat() for x in data["timeend"]]
        if include_series_id:
            data["series_id"] = self.series_id
        return data.to_dict(orient="records")

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
