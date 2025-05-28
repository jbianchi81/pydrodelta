import jsonschema
import yaml
import os
from pydrodelta.util import tryParseAndLocalizeDate, interval2timedelta, getRandColor, coalesce
from pathlib import Path
from datetime import timedelta, datetime
from dateutil.relativedelta import relativedelta
from .node import Node
from .node_variable import NodeVariable
import logging
import json
from numpy import nan
from a5client import createEmptyObsDataFrame, Crud
import pandas
import matplotlib.pyplot as plt
from .util import getParamOrDefaultTo
from .observed_node_variable import ObservedNodeVariable
from .derived_node_variable import DerivedNodeVariable
import networkx as nx
from networkx.readwrite import json_graph
import matplotlib.backends.backend_pdf
from colour import Color
from typing import Union, List, Tuple
from .validation import getSchemaAndValidate
from pandas import DataFrame
from .descriptors.datetime_descriptor import DatetimeDescriptor
from .descriptors.duration_descriptor import DurationDescriptor
from .descriptors.duration_descriptor_default_none import DurationDescriptorDefaultNone
from .descriptors.bool_descriptor import BoolDescriptor
from .descriptors.int_descriptor import IntDescriptor
from .descriptors.dict_descriptor import DictDescriptor
from .descriptors.string_descriptor import StringDescriptor
from .descriptors.list_descriptor import ListDescriptor
from .types.plot_variable_params_dict import PlotVariableParamsDict
from .types.save_variable_params_dict import SaveVariableParamsDict
from .types.node_dict import NodeDict
from .types.plot_params_dict import PlotParamsDict
from .base import Base
from .types.typed_list import TypedList

from pydrodelta.config import config
    
class Topology(Base):
    """The topology defines a list of nodes which represent stations and basins. These nodes are identified with a node_id and must contain one or many variables each, which represent the hydrologic observed/simulated properties at that node (such as discharge, precipitation, etc.). They are identified with a variable_id and may contain one or many ordered series, which contain the timestamped values. If series are missing from a variable, it is assumed that observations are not available for said variable at said node. Additionally, series_prono may be defined to represent timeseries of said variable at said node that are originated by an external modelling procedure. If series are available, said series_prono may be automatically fitted to the observed data by means of a linear regression. Such a procedure may be useful to extend the temporal extent of the variable into the forecast horizon so as to cover the full time domain of the plan. Finally, one or many series_sim may be added and it is where simulated data (as a result of a procedure) will be stored. All series have a series_id identifier which is used to read/write data from data source whether it be an alerta5DBIO instance or a csv file."""

    timestart = DatetimeDescriptor()
    """start date of observations period"""
    timeend = DatetimeDescriptor()
    """end date of observations period"""
    forecast_timeend = DatetimeDescriptor()
    """forecast horizon"""        
    time_offset_start = DurationDescriptor()
    """time of day where first timestep start"""
    time_offset_end = DurationDescriptorDefaultNone()
    """time of day where last timestep ends"""
    interpolation_limit = DurationDescriptorDefaultNone()
    """maximum duration between observations for interpolation"""
    extrapolate = BoolDescriptor()
    """Extrapolate observations outside the observation time domain, up to a maximum duration equal to .interpolation_limit"""
    @property
    def nodes(self) -> List[Node]:
        """Nodes represent stations and basins. These nodes are identified with a node_id and must contain one or many variables each, which represent the hydrologic observed/simulated properties at that node (such as discharge, precipitation, etc.). They are identified with a variable_id and may contain one or many ordered series, which contain the timestamped values. If series are missing from a variable, it is assumed that observations are not available for said variable at said node. Additionally, series_prono may be defined to represent timeseries of said variable at said node that are originated by an external modelling procedure. If series are available, said series_prono may be automatically fitted to the observed data by means of a linear regression. Such a procedure may be useful to extend the temporal extent of the variable into the forecast horizon so as to cover the full time domain of the plan. Finally, one or many series_sim may be added and it is where simulated data (as a result of a procedure) will be stored. All series have a series_id identifier which is used to read/write data from data source whether it be an alerta5DBIO instance or a csv file."""
        return self._nodes
    @nodes.setter
    def nodes(self,nodes : List[Union[dict, Node]]):
        self._nodes : List[Node] = TypedList(Node, unique_id_property = "id", topology = self, plan = self._plan, timestart = self.timestart, timeend = self.timeend, forecast_timeend = self.forecast_timeend, time_offset = self.time_offset_start)
        for i, node in enumerate(nodes):
            if "id" not in node:
                raise ValueError("Missing node.id at index %i of topology.nodes" % i)
            if node["id"] in [n.id for n in self._nodes]:
                raise ValueError("Duplicate node.id = %s at index %i of topology.nodes" % (str(node["id"]), i))
            self._nodes.append(node)
            # if isinstance(node, Node):
            #     self._nodes.append(node)
            # else:
            #     self._nodes.append(
            #         Node(
            #             **node,
            #             timestart=self.timestart,
            #             timeend=self.timeend,
            #             forecast_timeend=self.forecast_timeend,
            #             plan=self._plan,
            #             time_offset=self.time_offset_start,
            #             topology=self
            #         )
            #     )
    cal_id = IntDescriptor()
    """Identifier for saving analysis results as forecast (i.e. using .uploadDataAsProno)"""
    plot_params = DictDescriptor()
    """Plotting configuration. See .plotProno"""
    report_file = StringDescriptor()
    """Write analysis report into this file"""
    @property
    def graph(self) -> nx.DiGraph:
        """Directional graph representing this topology"""
        return self._graph

    no_metadata = BoolDescriptor()
    """Don't retrieve series metadata on load from api"""

    @property
    def plot_variable(self) -> List[PlotVariableParamsDict]:
        return self._plot_variable
    @plot_variable.setter
    def plot_variable(self, params : List[PlotVariableParamsDict]) -> None:
        if params is None:
            self._plot_variable = None
            return
        self._plot_variable = []
        for i, item in enumerate(params):
            if "var_id" not in item:
                raise ValueError("Missing var_id from PlotVariableParamsDict at index %i of plot_variable" %i)
            if "output" not in item:
                raise ValueError("Missing output from PlotVariableParamsDict at index %i of plot_variable" %i)
            d = {
                "var_id": int(item["var_id"]),
                "output": item["output"]
            }
            if "timestart" in item:
                d["timestart"] = tryParseAndLocalizeDate(item["timestart"])
            if "timeend" in item:
                d["timeend"] = tryParseAndLocalizeDate(item["timeend"])
            if "extra_sim_columns" in item:
                d["extra_sim_columns"] = bool(item["extra_sim_columns"])
            self._plot_variable.append(d)
        if not len(self._plot_variable):
            self._plot_variable = None

    @property
    def save_variable(self) -> List[SaveVariableParamsDict]:
        return self._save_variable
    @save_variable.setter
    def save_variable(self, params : List[SaveVariableParamsDict]) -> None:
        if params is None:
            self._save_variable = None
            return
        self._save_variable = []
        for i, item in enumerate(params):
            if "var_id" not in item:
                raise ValueError("Missing var_id from SaveVariableParamsDict at index %i of save_variable" %i)
            if "output" not in item:
                raise ValueError("Missing output from SaveVariableParamsDict at index %i of save_variable" %i)
            d = {
                "var_id": int(item["var_id"]),
                "output": item["output"]
            }
            if "format" in item:
                d["format"] = item["format"]
            if "pretty" in item:
                d["pretty"] = bool(item["pretty"])
            if "pivot" in item:
                d["pivot"] = bool(item["pivot"])
            self._save_variable.append(d)
        if not len(self._save_variable):
            self._save_variable = None

    include_prono = BoolDescriptor()
    """While executing .batchProcessInput, use series_prono to fill nulls of series"""

    output_csv = StringDescriptor()
    """Save analysis results as csv into this path (relative to PYDRODELTA_DIR)"""

    output_json = StringDescriptor()
    """Save analysis results as json into this path (relative to PYDRODELTA_DIR)""" 

    pivot = BoolDescriptor()
    """If output_csv is set, pivot series into columns of the table (default True)"""

    pretty = BoolDescriptor()
    """For output_json, prettify json"""

    upload_prono = BoolDescriptor()
    """Upload series_prono"""

    qualifiers = ListDescriptor()
    """create additional observations using these keys from series_prono data"""

    save_response = StringDescriptor()
    """Save prono creation response into this file"""

    save_post_data = StringDescriptor()
    """Save prono creation request data into this file"""

    prono_ignore_warmup = BoolDescriptor()
    """In concatenation, ignore warmup period of series_prono (default True)"""

    var_map = DictDescriptor()
    """Variable metadata is stored in this dict"""

    def __init__(
        self,
        timestart : Union[str,dict], 
        timeend :  Union[str,dict], 
        forecast_timeend :  Union[str,dict,None] = None,
        time_offset :  Union[str,dict,None] = None, 
        time_offset_start : Union[str,dict,None] = None, 
        time_offset_end : Union[str,dict,None] = None, 
        interpolation_limit : Union[dict,int] = None,
        extrapolate : bool = False,
        nodes : List[Union[Node,NodeDict]] = list(),
        cal_id : Union[int,None] = None,
        plot_params : Union[PlotParamsDict,None] = None,
        report_file : Union[str,None] = None,
        plan = None,
        no_metadata : bool = False,
        plot_variable : List[PlotVariableParamsDict] = None,
        save_variable : List[SaveVariableParamsDict] = None,
        include_prono : bool = False,
        output_csv : str = None,
        output_json : str = None,
        pivot : bool = True,
        pretty : bool = True,
        upload_prono : bool = False,
        qualifiers : List[str] = None,
        save_response : str = None,
        save_post_data : str = None,
        prono_ignore_warmup : bool = True,
        output_graph : str = None,
        **kwargs
        ):
        """Initiate topology
        
        Parameters:
        -----------
        timestart : str or dict
            start date of observations period (datetime or timedelta relative to now)
         
        timeend :  str or dict
            end date of observations period (datetime or timedelta relative to now)
        
        forecast_timeend :  str, dict or None
            forecast horizon (datetime or timedelta relative to timeend)
        
        time_offset :    str, dict or None
            time of day where timesteps start

        time_offset_start : str, dict or None
            time of day where first timestep start. Defaults to 0 hours

        time_offset_end : str, dict or None
            time of day where last timestep ends. Defaults to timeend.hour

        interpolation_limit : dict or int
            maximum duration between observations for interpolation (default: 0)

        extrapolate : boolean (default: False)
            Extrapolate observations outside the observation time domain, up to a maximum duration equal to interpolation_limit 

        nodes : List[Union[Node,NodeDict]]
            Nodes represent stations and basins. These nodes are identified with a node_id and must contain one or many variables each, which represent the hydrologic observed/simulated properties at that node (such as discharge, precipitation, etc.). They are identified with a variable_id and may contain one or many ordered series, which contain the timestamped values. If series are missing from a variable, it is assumed that observations are not available for said variable at said node. Additionally, series_prono may be defined to represent timeseries of said variable at said node that are originated by an external modelling procedure. If series are available, said series_prono may be automatically fitted to the observed data by means of a linear regression. Such a procedure may be useful to extend the temporal extent of the variable into the forecast horizon so as to cover the full time domain of the plan. Finally, one or many series_sim may be added and it is where simulated data (as a result of a procedure) will be stored. All series have a series_id identifier which is used to read/write data from data source whether it be an alerta5DBIO instance or a csv file.

        cal_id : int or None
            Identifier for saving analysis results as forecast (i.e. using .uploadDataAsProno)

        plot_params : dict or None
            Plotting configuration. See .plotProno
        
        report_file : str or None
            Write analysis report into this file
        
        plan : Plan
            Plan containing this topology
        
        no_metadata : bool = False
            Don't retrieve series metadata on load from api

        plot_variable : List[PlotVariableParamsDict] = None
            Print graphs to pdf files of the selected variables at every node where said variables are defined 
                PlotVariableParamsDict:
                    var_id : int
                    output : str
                    timestart : Union[datetime,str,dict], optional
                    timeend : Union[datetime,str,dict], optional
        
        save_variable : List[SaveVariableParamsDict] = None
            Print text files of the selected variables
                SaveVariableParamsDict:
                    var_id : int
                    nodes : list[int]
                    output : str
                    format : Literal["csv", "json"]
                    pretty : bool
                    pivot : bool
        
        include_prono : bool = False
            While executing .batchProcessInput, use series_prono to fill nulls of series 
        
        output_csv : str = None
            Save analysis results as csv into this path (relative to PYDRODELTA_DIR)

        output_json : str = None
            Save analysis results as json into this path (relative to PYDRODELTA_DIR)

        pivot : bool = True
            If output_csv is set, pivot series into columns of the table

        pretty : bool = True
            For output_json, prettify json

        upload_prono : bool = False
            Upload series_prono
        
        qualifiers : List[str] = None
            Add these qualifiers to the uploaded series_prono

        save_response : str = None
            Save prono creation response into this file

        save_post_data : str = None
            Save prono creation request data into this file

        prono_ignore_warmup : bool
        In concatenation, ignore warmup period of series_prono (default True)

        output_graph : str
        Print graph representation of the topology into this file (png) 
        """
        super().__init__(**kwargs)
        params = {
            "timestart": timestart, 
            "timeend":  timeend, 
            "forecast_timeend": forecast_timeend,
            "time_offset":  time_offset, 
            "time_offset_start": time_offset_start, 
            "time_offset_end": time_offset_end, 
            "interpolation_limit": interpolation_limit,
            "extrapolate": extrapolate,
            "nodes": nodes,
            "cal_id": cal_id,
            "plot_params": plot_params,
            "report_file" : report_file,
            "no_metadata": no_metadata,
            "plot_variable": plot_variable,
            "save_variable": save_variable,
            "include_prono": include_prono,
            "output_csv": output_csv,
            "output_json": output_json,
            "pivot": pivot,
            "pretty": pretty,
            "upload_prono": upload_prono,
            "qualifiers": qualifiers,
            "save_response": save_response,
            "save_post_data": save_post_data,
            "output_graph": output_graph
        }
        getSchemaAndValidate(params=params, name="topology")
        self.var_map = {}
        self.timestart = timestart
        self.timeend = timeend
        self.forecast_timeend = forecast_timeend
        self.time_offset_start = time_offset_start if time_offset_start is not None else time_offset if time_offset is not None else {"hours":0}
        self.time_offset_end = time_offset_end if time_offset_end is not None else time_offset if time_offset is not None else None
        # round down to day if timestart is relative 
        self.timestart = self.timestart.replace(hour=0,minute=0,second=0,microsecond=0) + self.time_offset_start if type(timestart) == dict else self.timestart
        # round down to day if timeend is relative 
        self.timeend = self.timeend.replace(hour=0,minute=0,second=0,microsecond=0) + self.time_offset_end if type(timeend) == dict and self.time_offset_end is not None else self.timeend
        if self.timestart >= self.timeend:
            raise("Bad timestart, timeend parameters. timestart must be before timeend")
        self.interpolation_limit = interpolation_limit
        self.extrapolate = extrapolate
        self._plan = plan
        """Plan that contains this topology"""
        self.nodes = nodes
        self.cal_id = cal_id
        self.plot_params = plot_params
        self.report_file = report_file
        self._graph = self.toGraph()
        self.no_metadata = no_metadata
        self.plot_variable = plot_variable
        self.save_variable = save_variable
        self.include_prono = include_prono
        self.output_csv = "%s/%s" % (config["PYDRODELTA_DIR"],output_csv) if output_csv is not None else None
        self.output_json = "%s/%s" % (config["PYDRODELTA_DIR"],output_json) if output_json is not None else None
        self.pivot = pivot
        self.pretty = pretty
        self.upload_prono = upload_prono
        self.qualifiers = qualifiers
        self.save_response = save_response
        self.save_post_data = save_post_data
        self.prono_ignore_warmup = prono_ignore_warmup
        self.output_graph = output_graph
    
    def __repr__(self):
        nodes_str = ", ".join(["%i: Node(id: %i, name: %s)" % (self.nodes.index(n), n.id, n.name) for n in self.nodes])
        return "Topology(timestart: %s, timeend: %s, nodes: [%s])" % (self.timestart.isoformat(), self.timeend.isoformat(), nodes_str)

    def __getitem__(self, key : int):
        return self.getNode(key)

    def index(self) -> List[int]:
        return [n.id for n in self.nodes]

    def getNode(
        self,
        node_id : int) -> Node:
        if self.nodes is None:
            raise Exception("Nodes is not defined")
        for i, n in enumerate(self.nodes):
            if n.id == node_id:
                return n
        raise KeyError("Node with id %i not found" % node_id)

    def getNodeVariable(
        self,
        node_id : int,
        var_id: int) -> NodeVariable:
        if self.nodes is None:
            raise Exception("Nodes is not defined")
        for i, n in enumerate(self.nodes):
            if n.id == node_id:
                if var_id in n.variables:
                    return n[var_id]
                else:
                    raise KeyError("Variable with id %i not found in node %i" % (var_id, node_id))
        raise KeyError("Node with id %i not found" % node_id)

    def batchProcessInput(
        self,
        include_prono : bool = None,
        input_api_config : dict = None) -> None:
        """
        Run input processing sequence. This includes (in this order):
        
        - .loadData()
        - .removeOutliers()
        - .detectJumps()
        - .applyOffset()
        - .regularize()
        - .applyMovingAverage()
        - .fillNulls()
        - .adjust()
        - .concatenateProno() (if include_prono is True)
        - .derive()
        - .interpolate()
        - .setOriginalData()
        - .setOutputData()
        - .plotProno()
        - .printReport() if ().report_file is not None)
        - .printGraph()
        
        Parameters:
        -----------
        include_prono : bool default False
            For each variable, fill missing observations with values from series_prono
        
        input_api_config : dict
            Api connection parameters (used to load data). Overrides global config.input_api
            
            Properties:
            - url : str
            - token : str
            - proxy_dict : dict
        """
        include_prono = include_prono if include_prono is not None else self.include_prono
        logging.debug("loadData")
        self.loadData(input_api_config=input_api_config)
        logging.debug("removeOutliers")
        self.removeOutliers()
        logging.debug("detectJumps")
        self.detectJumps()
        logging.debug("applyOffset")
        self.applyOffset()
        logging.debug("regularize")
        self.regularize()
        logging.debug("applyMovingAverage")
        self.applyMovingAverage()
        logging.debug("fillNulls")
        self.fillNulls()
        logging.debug("adjust")
        self.adjust()
        if include_prono:
            logging.debug("concatenateProno")
            self.concatenateProno()
        logging.debug("fillNullsWithValue")
        self.fillNullsWithValue()
        logging.debug("derive")
        self.derive()
        logging.debug("interpolate")
        self.interpolate()
        self.setOriginalData()
        self.setOutputData()
        self.plotProno()
        if(self.report_file is not None):
            report = self.printReport()
            f = open(
                os.path.join(
                    config["PYDRODELTA_DIR"],
                    self.report_file
                ),
                "w"
            )
            json.dump(report,f,indent=2)
            f.close()
        self.saveSeries()
        if self.output_csv is not None:
            self.saveData(self.output_csv,pivot=self.pivot,format="csv")
        if self.output_json is not None:
            self.saveData(self.output_json,pivot=self.pivot,format="json",pretty=self.pretty)
        if self.upload_prono:
            self.uploadDataAsProno(False, True)
        if self.output_graph:
            self.printGraph(output_file=os.path.join(config["PYDRODELTA_DIR"],self.output_graph))

    def loadData(
        self,
        include_prono : bool = True,
        input_api_config : dict = None,
        no_metadata : bool = None) -> None:
        """For each series of each variable of each node, load data from the source.
        
        Parameters:
        -----------
        
        include_prono : bool default True
            Load forecasted data
        
        input_api_config : dict
            Api connection parameters. Overrides global config.input_api
            
            Properties:
            - url : str
            - token : str
            - proxy_dict : dict
            
        no_metadata : bool = None
            Don't retrieve series metadata on load from api. If not given, reads from self.no_metadata
        """
        for node in self.nodes:
            # logging.debug("loadData timestart: %s, timeend: %s, time_interval: %s" % (self.timestart.isoformat(), self.timeend.isoformat(), str(node.time_interval)))
            timestart = self.timestart - node.time_interval if node.time_interval is not None else self.timeend
            timeend = self.timeend + node.time_interval if node.time_interval is not None else self.timeend
            forecast_timeend = self.forecast_timeend+node.time_interval if self.forecast_timeend is not None and node.time_interval is not None else self.forecast_timeend
            if hasattr(node,"loadData"):
                node.loadData(
                    timestart, 
                    timeend, 
                    forecast_timeend = forecast_timeend, 
                    include_prono = include_prono,
                    input_api_config = input_api_config,
                    no_metadata = no_metadata if no_metadata is not None else self.no_metadata)

    def setOriginalData(self) -> None:
        """For each variable of each node, copy .data into .original_data"""
        for node in self.nodes:
            node.setOriginalData()

    def removeOutliers(self) -> None:
        """For each serie of each variable of each node, perform outlier removal (only in series where lim_outliers is not None)."""
        found_outliers = False
        for node in self.nodes:
            found_outliers_ = node.removeOutliers()
            found_outliers = found_outliers_ if found_outliers_ else found_outliers
        return found_outliers

    def detectJumps(self) -> None:
        """For each serie of each variable of each node, perform jumps detection (only in series where lim_jump is not None). Results are saved in jumps_data of the series object."""
        found_jumps = False
        for node in self.nodes:
            found_jumps_ = node.detectJumps()
            found_jumps = found_jumps_ if found_jumps_ else found_jumps
        return found_jumps

    def applyMovingAverage(self) -> None:
        """For each serie of each variable of each node, apply moving average (only in series where moving_average is not None)"""
        for node in self.nodes:
            node.applyMovingAverage()

    def applyOffset(self) -> None:
        """For each serie of each variable of each node, apply x and/or y offset (only in series where x_offset (time) or y_offset (value) is defined)"""
        for node in self.nodes:
            node.applyOffset()

    def regularize(self,interpolate=False) -> None:
        """For each series and series_prono of each observed variable of each node, regularize the time step according to time_interval and time_offset
        
        Parameters:
        ----------
        interpolate : bool default False
            if False, interpolates only to the closest timestep of the regular timeseries. If observation is equidistant to preceding and following timesteps it interpolates to both
        """
        for node in self.nodes:
            node.regularize(interpolate=interpolate)

    def fillNulls(self) -> None:
        """For each observed variable of each node, copies data of first series and fills its null values with the other series. In the end it fills nulls with self.fill_value. Saves result in self.data
        """
        for node in self.nodes:
            node.fillNulls()

    def fillNullsWithValue(self) -> None:
        """For each observed variable of each node, if fill_value is defined, fills nulls of data with that value
        """
        for node in self.nodes:
            node.fillNullsWithValue()
        

    def derive(self) -> None:
        """For each derived variable of each node, derives data from related variable according to derived_from attribute
        """
        for node in self.nodes:
            node.derive()

    def adjust(self) -> None:
        """For each series_prono of each variable of each node, if observations are available, perform error correction by linear regression"""
        for node in self.nodes:
            node.adjust()
            node.apply_linear_combination()
            node.adjustProno()

    def concatenateProno(self, ignore_warmup : bool = None) -> None:
        """For each variable of each node, if series_prono are available, concatenate series_prono into variable.data"""
        ignore_warmup = ignore_warmup if ignore_warmup is not None else self.prono_ignore_warmup
        for node in self.nodes:
            for variable in node.variables.values():
                if variable.series_prono is not None:
                    variable.concatenateProno(ignore_warmup=ignore_warmup)

    def interpolate(
        self,
        limit : relativedelta = None,
        extrapolate: bool = None
        ) -> None:
        """For each variable of each node, fill nulls of data by interpolation
        
        Parameters:
        -----------
        limit : relativedelta
            Maximum interpolation distance
        
        extrapolate : bool
            Extrapolate up to limit
        """
        for node in self.nodes:
            node.interpolate(limit=limit,extrapolate=extrapolate)

    def setOutputData(self) -> None:
        """For each series_output of each variable of each node, copy variable.data into series_output.data. If x_offset or y_offset are not 0, applies the offset"""
        for node in self.nodes:
            node.setOutputData()

    def toCSV(
        self,
        pivot : bool=False,
        nodes : list = None,
        variables : list = None
        ) -> str:
        """Generates csv table from all variables of all nodes
        
        Parameters:
        -----------
        pivot : bool = False
            If True, pivots variables into columns

        nodes : list or None = None
            Print only the selected nodes

        variables : list or None = None
            Print only the selected variables
        
        Returns:
        --------
        str"""
        if pivot:
            data = self.pivotData(nodes=nodes, variables=variables)
            data["timestart"] = [x.isoformat() for x in data.index]
            # data.reset_index(inplace=True)
            return data.to_csv(index=False)
        else:
            header = ",".join(["timestart","valor","tag","series_id"])
            csv_list = []
            for node in self.nodes:
                if nodes is not None and node.id not in nodes:
                    # skip node
                    continue
                csv_list.append(node.toCSV(True,False,variables=variables))
            return header + "\n" + "\n".join(csv_list)

    def outputToCSV(
        self,
        pivot=False
        ) -> str:
        """Generates csv table of all series_output of all variables of all nodes
        
        Parameters:
        -----------
        pivot : bool
            If true, pivots variables into columns
        
        Returns:
        --------
        str"""
        if pivot:
            data = self.pivotOutputData()
            data["timestart"] = [x.isoformat() for x in data.index]
            # data.reset_index(inplace=True)
            return data.to_csv(index=False)    
        header = ",".join(["timestart","valor","tag","series_id"])
        return header + "\n" + "\n".join([node.outputToCSV(False) for node in self.nodes])
    def toSeries(
        self,
        use_node_id : bool=False
        ) -> list:
        """
        returns list of Series objects. Same as toList(flatten=True)

        Parameters:
        -----------
        use_node_id : bool
            use node_id as series identifier
        
        Returns:
        --------
        list of Observations
        """
        return self.toList(use_node_id=use_node_id,flatten=False)
    def toList(
        self,
        pivot : bool = False,
        use_node_id : bool = False,
        flatten : bool = True,
        nodes : list = None,
        variables : list = None
        ) -> list:
        """
        returns list of data of selected variables of selected nodes
        
        Parameters:
        -----------
        pivot : bool
            pivot variables into columns

        use_node_id : bool
            use node.id as series_id instead of node.output_series[0].id

        flatten : bool
            If set to False, return list of Series: [{"series_id":int,observaciones:[obs,obs,...]},...] (ignored if pivot=True). If True, return list of Observations: [{"timestart":str,"valor":float,"series_id":int},...]
        
        nodes : list or None = None

        variables : list or None = None
        
        Returns:
        --------
        list of Series or list of Observations
        """
        if pivot:
            data = self.pivotData(nodes=nodes, variables=variables)
            data["timestart"] = [x.isoformat() for x in data.index]
            data.reset_index
            data["timeend"] = data["timestart"]
            return data.to_dict(orient="records")
        else:
            obs_list = []
            for node in self.nodes:
                if nodes is not None and node.id not in nodes:
                    # skip node
                    continue
                for var_id, variable in node.variables.items():
                    if variables is not None and var_id not in variables:
                        # skip variable
                        continue
                    if flatten:
                        obs_list.extend(variable.toList(True,use_node_id=use_node_id))
                    else:
                        obs_list.append(variable.toSerie(True,use_node_id=use_node_id))
            return obs_list
    
    def outputToList(
        self,
        pivot : bool = False,
        flatten : bool = False
        ) -> list:
        """returns list of data of all output_series of all variables of all nodes
        
        Parameters:
        -----------
        pivot : bool
            pivot variables into columns

        flatten : bool
            If set to False, return list of Series: [{"series_id":int,observaciones:[obs,obs,...]},...] (ignored if pivot=True). If True, return list of Observations: [{"timestart":str,"valor":float,"series_id":int},...]
        
        Returns:
        --------
        list of Series or list of Observations"""
        if pivot:
            data = self.pivotOutputData()
            data["timestart"] = [x.isoformat() for x in data.index]
            data.reset_index
            data["timeend"] = data["timestart"]
            data = data.replace({nan:None})
            return data.to_dict(orient="records")
        obs_list = []
        for node in self.nodes:
            obs_list.extend(node.variablesOutputToList(flatten=flatten))
        return obs_list
    def saveData(
        self,
        file : str,
        format : str = "csv",
        pivot : bool = False,
        pretty : bool = False,
        nodes : list = None,
        variables : list = None
        ) -> None:
        """Save data of selected variables of selected nodes to a file in the desired format
        
        Parameters:
        -----------
        file : str
            Where to save the data

        format : str
            File format: csv or json
        
        pivot : bool
            pivot variables into columns

        pretty : bool
            Pretty-print JSON (w/ indentation)    

        nodes : list or None = None

        variables : list or None = None

        """
        f = open(file,"w")
        if format == "json":
            if pretty:
                obs_json = json.dumps(self.toList(pivot=pivot, nodes=nodes, variables=variables),ensure_ascii=False,indent=4)
            else:
                obs_json = json.dumps(self.toList(pivot=pivot, nodes=nodes, variables=variables),ensure_ascii=False)
            f.write(obs_json)
            f.close()
            return
        else:
            f.write(self.toCSV(pivot,nodes=nodes, variables=variables))
            f.close()
            return
    def saveOutputData(
        self,
        file : str,
        format : str = "csv",
        pivot : bool = False,
        pretty : bool =False
        ) -> None:
        """Save data of all series_output of all variables of all nodes to a file in the desired format
        
        Parameters:
        -----------
        file : str
            Where to save the data

        format : str
            File format: csv or json
        
        pivot : bool
            pivot variables into columns

        pretty : bool
            Pretty-print JSON (w/ indentation)        
        """
        f = open(file,"w")
        if format == "json":
            if pretty:
                obs_json = json.dumps(self.outputToList(pivot),ensure_ascii=False,indent=4)
            else:
                obs_json = json.dumps(self.outputToList(pivot),ensure_ascii=False)
            f.write(obs_json)
            f.close()
            return
        f.write(self.outputToCSV(pivot))
        f.close
        return
    def uploadData(
        self,
        include_prono : bool,
        api_config : dict = None
        ) -> list:
        """
        Uploads analysis data (series_output) of all variables of all nodes as a5 observaciones (https://raw.githubusercontent.com/jbianchi81/alerta5DBIO/master/public/schemas/a5/observacion.yml)
        
        Parameters:
        -----------
        include_prono : bool
            Include the forecast horizon
        
        api_config : dict = None
            Api connection parameters. Overrides global config.output_api
            
            Properties:
            - url : str
            - token : str
            - proxy_dict : dict

        Returns:
        list of Observations
        """
        created = []
        for node in self.nodes:
            obs_created = node.uploadData(
                include_prono = include_prono,
                api_config = api_config)
            if obs_created is not None and len(obs_created):
                created.extend(obs_created)
        return created

    def dataAsProno(
        self,
        include_obs : bool = True,
        include_prono : bool = False
    ) -> dict:
        """
        Converts analysis data (series_output) of all variables of all nodes to a5 'corrida' object (https://github.com/jbianchi81/alerta5DBIO/blob/master/public/schemas/a5/pronostico.yml)

        Parameters:
        -----------
        include_obs : bool
            Include period before the forecast date
        include_prono : bool
            Include period after the forecast date

        Returns:
        --------
        dict : (https://github.com/jbianchi81/alerta5DBIO/blob/master/public/schemas/a5/corrida.yml)
        """
        if self.cal_id is None:
            if self._plan is not None:
                 cal_id = self._plan.id
            else:
                raise Exception("upload analysis: Missing required parameter cal_id")
        else:
            cal_id = self.cal_id
        prono = {
            "cal_id": cal_id,
            "forecast_date": self.timeend.isoformat(),
            "series": []
        }
        if include_obs:
            for node in self.nodes:
                serieslist = node.variablesOutputToList(flatten=False)
                for serie in serieslist:
                    serie["pronosticos"] = serie["observaciones"]
                    del serie["observaciones"]
                prono["series"].extend(serieslist)
        if include_prono:
            for node in self.nodes:
                serieslist = node.variablesPronoToList(flatten=False, qualifiers = self.qualifiers)
                prono["series"].extend(serieslist)
        return prono
        
    def uploadDataAsProno(
        self,
        include_obs : bool = True,
        include_prono : bool = False,
        api_config : dict = None,
        save_response : str = None,
        save_post_data : str = None
        ) -> dict:
        """
        Uploads analysis data (series_output) of all variables of all nodes to output api as a5 pronosticos (https://github.com/jbianchi81/alerta5DBIO/blob/master/public/schemas/a5/pronostico.yml)

        Parameters:
        -----------
        include_obs : bool
            Include period before the forecast date
        include_prono : bool
            Include period after the forecast date
        api_config : dict = None
            Api connection parameters. Overrides global config.output_api
            
            Properties:
            - url : str
            - token : str
            - proxy_dict : dict

        Returns:
        --------
        dict : server response. Either a successfully created forecast (https://github.com/jbianchi81/alerta5DBIO/blob/master/public/schemas/a5/corrida.yml) or an error message
        """
        save_response = coalesce(save_response, self.save_response)
        save_post_data = coalesce(save_post_data, self.save_post_data)
        
        prono = self.dataAsProno(include_obs=include_obs, include_prono=include_prono)
        
        if save_post_data:
            json.dump(prono, open("%s/%s" % (config["PYDRODELTA_DIR"], save_post_data), "w"), indent=4)
        api_client = Crud(**api_config) if api_config is not None else self.output_crud
        response = api_client.createCorrida(prono)
        if save_response:
            json.dump(response, open("%s/%s" % (config["PYDRODELTA_DIR"], save_response), "w"), indent=4)
        return response

    def pivotData(
        self,
        include_tag : bool = True,
        use_output_series_id : bool = True,
        use_node_id : bool = False,
        nodes : list = None,
        variables : list = None
        ) -> DataFrame:
        """Pivot variables of all nodes into columns of a single DataFrame
        
        Parameters:
        -----------
        include_tag : bool (default True)
            Add columns for tags
        
        use_output_series_id : bool (default True)
            Use series_output[x].series_id as column header
        
        use_node_id : bool (default False)
            Use node.id + variable.id as column header
        
        nodes : list or None
            Nodes of the topology to read. If None, reads all self.nodes

        variables : list or None
            Variables of the topology to read. If None, reads all variables
        
        Returns:
        --------
        DataFrame
        """
        if nodes is None:
            nodes = self.nodes
        columns = ["valor","tag"] if include_tag else ["valor"]
        #data = nodes[0].data[columns]
        data = createEmptyObsDataFrame(extra_columns={"tag":str})
        for node in nodes:
            for var_id, variable in node.variables.items():
                if variables is not None and var_id not in variables:
                    # skip variable
                    continue
                if variable.data is not None and len(variable.data):
                    rsuffix = "_%i" % (variable.series_output[0].series_id) if use_output_series_id and variable.series_output is not None else "_%s_%i" % (str(node.id),variable.id) if use_node_id else "_%s_%i" % (node.name,variable.id) 
                    # if include_prono:
                    #     node_data = node.concatenateProno(inline=False)
                    #     data = data.join(node_data[columns][node_data.valor.notnull()],how='outer',rsuffix=rsuffix,sort=True) # data.join(node.series[0].data[["valor",]][node.series[0].data.valor.notnull()],how='outer',rsuffix="_%s" % node.name,sort=True)    
                    # else:
                    data = data.join(variable.data[columns][variable.data.valor.notnull()],how='outer',rsuffix=rsuffix,sort=True) # data.join(node.series[0].data[["valor",]][node.series[0].data.valor.notnull()],how='outer',rsuffix="_%s" % node.name,sort=True)
                    if use_output_series_id and variable.series_output is not None:
                        data = data.rename(columns={"valor_%i" % (variable.series_output[0].series_id) : str(variable.series_output[0].series_id)})
                    elif use_node_id:
                        data = data.rename(columns={"valor_%s_%i" % (str(node.id),variable.id) : node.id})
        # for column in columns:
        #     del data[column]
        del data["valor"]
        del data["tag"]
        data = data.replace({nan:None})
        return data
    def pivotOutputData(
        self,
        include_tag : bool = True
        ) -> DataFrame:
        """Pivot data of all output_series of all variables of all nodes into columns of a single DataFrame
        
        Parameters:
        -----------
        include_tag : bool (default True)
            Add columns for tags
        
        Returns:
        --------
        DataFrame
        """
        i = 0
        data = None
        for node in self.nodes:
            i = i+1
            node_data = node.pivotOutputData(include_tag=include_tag)
            data = node_data if i == 1 else pandas.concat([data,node_data],axis=1)
        # data = data.replace({np.nan:None})
        return data
    
    def pivotSimData(
        self,
        nodes : List[int] = None,
        variables : List[int] = None
        ) -> DataFrame:
        """Pivot data of all series_sim of selected variables of selected nodes into columns of a single DataFrame

        nodes : List[int] = None
        Node ids. If None, selects all nodes

        variables : List[int] = None
        Variable ids. If None, selects all variables
        
        Returns:
        --------
        DataFrame
        """
        data = None
        for node in self.nodes:
            if nodes is not None and node.id not in nodes:
                # skip node
                continue
            node_data = node.pivotSimData(variables=variables)
            if node_data is not None:
                if data is None:
                    data = node_data
                else:
                    data = pandas.concat([data,node_data],axis=1)
        # data = data.replace({np.nan:None})
        return data
    

    def plotVariable(
        self,
        var_id : int,
        timestart : datetime = None,
        timeend : datetime = None,
        output : str = None,
        extra_sim_columns : bool = True,
        table : bool = True,
        round_to : int = 2
        ) -> None:
        """Generates time-value plots for a selected variable, one per node where this variable is found. 
        
        Parameters:
        ----------
        var_id : int
            Variable identifier

        timestart : datetime or None
            If not None, start time of the plot

        timeend : datetime or None
            If not None, end time of the plot
          
        output : str or None
            If not None, save the result into a pdf file
        
        extra_sim_columns : bool = True
            Add additional simulation series to plot

        table : bool = True
            Add table
        """
        color_map = {"obs": "blue", "sim": "red","interpolated": "yellow","extrapolated": "orange","analysis": "green", "prono": "purple", "sum": "yellow","filled":"gray", "moving_average": "blue"}
        if output is not None:
            matplotlib.use('pdf')
            pdf = matplotlib.backends.backend_pdf.PdfPages(
                os.path.join(
                    config["PYDRODELTA_DIR"],
                    output
                )
            )
        else:
            matplotlib.use(os.environ["MPLBACKEND"] if "MPLBACKEND" in os.environ else "Agg")
        for node in self.nodes:
            # if hasattr(node.series[0],"data"):
            if var_id in node.variables and node.variables[var_id].data is not None and len(node.variables[var_id].data):
                data = node.variables[var_id].data.reset_index().rename(columns={"index":"timestart"}) # .plot(y="valor")
                data["valor"] = pandas.to_numeric(data["valor"], errors="coerce")
                if timestart is not None:
                    data = data[data["timestart"] >= timestart]
                if timeend is not None:
                    data = data[data["timestart"] <= timeend]
                # data = node.series[0].data.reset_index() # .plot(y="valor")
                # data.plot(kind="scatter",x="timestart",y="valor",title=node.name, figsize=(20,8),grid=True)
                fig, ax = plt.subplots(ncols=2,figsize=(20,8),gridspec_kw={'width_ratios': [2, 1]})
                grouped = data.groupby('tag')
                for key, group in grouped:
                    group.plot(ax=ax[0],kind='scatter', x='timestart', y='valor', label=key,title=node.name, figsize=(20,8),grid=True, color=color_map[key])
                # data.plot.line(x="timestart",y="valor",ax=ax)
                original_data = node.variables[var_id].original_data.reset_index().rename(columns={"index":"timestart"})
                original_data["valor"] = pandas.to_numeric(original_data["valor"], errors="coerce")
                data_table = data.set_index("timestart")[["valor"]].rename(columns={"valor":"analysis"})
                if len(original_data.dropna()["valor"]):
                    logging.debug("Add original data to plot at node %s" % str(node.name))
                    if timestart is not None:
                        original_data = original_data[original_data["timestart"] >= timestart]
                    if timeend is not None:
                        original_data = original_data[original_data["timestart"] <= timeend]
                    original_data.plot(ax=ax[0],kind='line', x='timestart', y='valor', label="analysis",title=node.name, figsize=(20,8),grid=True, color=color_map["analysis"])
                    data_table = original_data.set_index("timestart")[["valor"]].rename(columns={"valor":"analysis"})
                else:
                    logging.debug("Missing original data at node %s variable %i" % (node.name, var_id))
                data_table["analysis"] = data_table["analysis"].round(2)
                if node.variables[var_id].series_sim is not None and len(node.variables[var_id].series_sim):
                    sim_colors = list(Color("orange").range_to(Color("red"),len(node.variables[var_id].series_sim)))
                    for i, serie_sim in enumerate(node.variables[var_id].series_sim):
                        if serie_sim.data is not None and len(serie_sim.data.dropna()["valor"]):
                            logging.debug("Add sim data to plot at node %s, series_sim %i" % (str(node.name),i))
                            data_sim = serie_sim.data.reset_index().rename(columns={"index":"timestart"})
                            data_sim["valor"] = pandas.to_numeric(data_sim["valor"], errors="coerce")
                            if timestart is not None:
                                data_sim = data_sim[data_sim["timestart"] >= timestart]
                            if timeend is not None:
                                data_sim = data_sim[data_sim["timestart"] <= timeend]
                            label = "sim_%i" % serie_sim.series_id
                            data_sim.plot(ax=ax[0],kind='line', x='timestart', y='valor', label=label,title=node.name, figsize=(20,8),grid=True, color=sim_colors[i].get_hex())
                            data_table = data_table.join(data_sim.set_index("timestart")[["valor"]].rename(columns={"valor":label}))
                            data_table[label] = data_table[label].round(2)
                            # plot extra sim columns
                            if extra_sim_columns:
                                for i, c in enumerate([c for c in data_sim.columns.to_list() if c not in [ "timestart", "valor", "tag"]]):
                                    data_sim[c] = pandas.to_numeric(data_sim[c], errors="coerce")
                                    label = "sim_%i_%s" % (serie_sim.series_id, c)
                                    logging.debug("Add series sim column %s, label %s" % (c,label))
                                    data_sim.plot(
                                        ax=ax[0],
                                        kind='line', 
                                        x='timestart', 
                                        y=c, 
                                        label=label,
                                        title=node.name, 
                                        figsize=(20,8),
                                        grid=True, 
                                        color=getRandColor(),
                                        linestyle="--",
                                        alpha=0.5)
                                    data_table = data_table.join(data_sim.set_index("timestart")[[c]].rename(columns={c:label}))
                                    data_table[label] = data_table[label].round(2)
                if hasattr(node.variables[var_id],"max_obs_date") and node.variables[var_id].max_obs_date is not None:
                    plt.axvline(node.variables[var_id].max_obs_date, color='k', linestyle='--')
                if table:
                    ax[1].axis('off')  # Hide axes
                    data_table = data_table.reset_index()
                    data_table["timestart"] = data_table["timestart"].dt.strftime('%Y-%m-%d' if node.time_interval is not None and datetime(2000, 1, 1) + node.time_interval >= datetime(2000, 1, 1) + relativedelta(days=1) else '%Y-%m-%d %H:%M')
                    table = ax[1].table(cellText=[[s[-9:] for s in data_table.columns.tolist()]] + data_table.tail(40).round(round_to).values.tolist(), loc='center')
                    table.auto_set_font_size(False)
                if output is not None:
                    pdf.savefig()
                plt.close()
            else:
                logging.debug("topology.plotVariable: Skipping node %s" % str(node.id))
        if output is not None:
            pdf.close()
            matplotlib.use(os.environ["MPLBACKEND"] if "MPLBACKEND" in os.environ else "Agg")
        else:
            plt.show()
    def plotProno(
        self,
        **kwargs
        # output_dir : str = None,
        # figsize : tuple = None,
        # title : str = None,
        # markersize : int = None,
        # obs_label : str = None,
        # tz : str = None,
        # prono_label : str = None,
        # footnote : str = None,
        # errorBandLabel : str = None,
        # obsLine : bool = None,
        # prono_annotation : str = None,
        # obs_annotation : str = None,
        # forecast_date_annotation : str = None,
        # ylim : tuple = None,
        # datum_template_string : str = None,
        # title_template_string : str = None,
        # x_label : str = None,
        # y_label : str = None,
        # xlim : tuple = None,
        # text_xoffset : tuple = None,
        # prono_fmt : str = None,
        # annotate : bool = None,
        # table_columns : list = None,
        # date_form : str = None,
        # xaxis_minor_tick_hours : list = None,
        # errorBand : Tuple[str,str] = None,
        # error_band_fmt : Union[str,Tuple[str,str]] = None,
        # forecast_table : bool = None,
        # footnote_height : float = None
        ) -> None:
        """For each series_prono (where plot_params is defined) of each variable of each node, print time-value chart including observed data
        
        Parameters:
        -----------
        output_dir : str
            Output directory path
        
        figsize : tuple
            figure size in cm (width, length)
        
        title : str
            Chart title

        markersize : int
            Marker size in points
        
        obs_label : str
            label for observed data

        tz : str
            time zone
        
        prono_label : str
            Label for forecast data

        footnote : str
            Footnote text
        
        errorBandLabel : str
            Label for error band
        
        obsLine : bool
            Add line to observed data
        
        prono_annotation : str
            Annotation text for forecast period

        obs_annotation : str
            Annotation text for observations period
        
        forecast_date_annotation : str
            Annotation text for forecast date
        
        ylim : tuple
            range of y axis (min, max)

        datum_template_string : str
            Template string for datum text

        title_template_string : str
            Template string for title text
        
        x_label : str
            Label for x axis

        y_label : str
            Label for y axis

        xlim : tuple
            range of x axis (min, max)

        text_xoffset : tuple
            Offset of text position

        prono_fmt : str
            Style for forecast series
        
        annotate : bool
            Add observed data/forecast data/forecast date annotations
        
        table_columns : list = ["Fecha", "Nivel"]
            Which forecast dataframe columns to show. Options: 
            -   Fecha
            -   Nivel
            -   Hora
            -   Fechap
            -   Dia
        
        date_form : str = "%H hrs \n %d-%b"
            Date formatting string for x axis tick labels

        xaxis_minor_tick_hours : list = [3,9,15,21]
            Hours of location of minor ticks of x axis

        errorBand : tuple[str,str] = None
            Columns to use as error band (lower bound, upper bound). If not set and series_prono.adjust_results is True, "error_band_01" and "error_band_99" resulting from the adjustment are used

        error_band_fmt : str = None
            style for error band. Set to 'errorbar' for error bars, else fmt parameter for plot function. Optionally, a 2-tuple may be used to set different styles for lower and upper bounds, respectively
        
        forecast_table : bool = True
            Print forecast table
        
        footnote_height : float = 0.2
            Height of space for footnote in inches    
        """
        # locals_ = { k: v for k, v in locals().items() if v is not None}
        # plot_prono_kwargs = {**self.plot_params, **kwargs} # **locals_}
        # output_dir = getParamOrDefaultTo("output_dir",output_dir,self.plot_params)
        # footnote = getParamOrDefaultTo("footnote",footnote,self.plot_params)
        # figsize = getParamOrDefaultTo("figsize",figsize,self.plot_params)
        # markersize = getParamOrDefaultTo("markersize",markersize,self.plot_params)  
        # prono_annotation = getParamOrDefaultTo("prono_annotation",prono_annotation,self.plot_params)  
        # obsLine = getParamOrDefaultTo("obsLine",obsLine,self.plot_params)
        # obs_annotation = getParamOrDefaultTo("obs_annotation",obs_annotation,self.plot_params)
        # forecast_date_annotation = getParamOrDefaultTo("forecast_date_annotation",forecast_date_annotation,self.plot_params)
        # output_dir = getParamOrDefaultTo("output_dir",output_dir,self.plot_params)
        # ylim = getParamOrDefaultTo("ylim",ylim,self.plot_params)
        # errorBandLabel = getParamOrDefaultTo("errorBandLabel",errorBandLabel,self.plot_params)
        # obs_label = getParamOrDefaultTo("obs_label",obs_label,self.plot_params)
        # tz = getParamOrDefaultTo("tz",tz,self.plot_params)
        # prono_label = getParamOrDefaultTo("prono_label",prono_label,self.plot_params)
        # title = getParamOrDefaultTo("title",title,self.plot_params)
        # datum_template_string = getParamOrDefaultTo("datum_template_string",datum_template_string,self.plot_params)
        # title_template_string = getParamOrDefaultTo("title_template_string",title_template_string,self.plot_params)
        # x_label = getParamOrDefaultTo("x_label",x_label,self.plot_params)
        # y_label = getParamOrDefaultTo("y_label",y_label,self.plot_params)
        # xlim = getParamOrDefaultTo("xlim",xlim,self.plot_params)
        # text_xoffset = getParamOrDefaultTo("text_xoffset",text_xoffset,self.plot_params)
        # prono_fmt = getParamOrDefaultTo("prono_fmt",prono_fmt,self.plot_params)
        # annotate = getParamOrDefaultTo("annotate",annotate,self.plot_params, True)
        # table_columns = getParamOrDefaultTo("table_columns",table_columns,self.plot_params, ["Fecha", "Nivel"])
        # date_form = getParamOrDefaultTo("date_form",date_form,self.plot_params,"%H hrs \n %d-%b")
        # xaxis_minor_tick_hours = getParamOrDefaultTo("xaxis_minor_tick_hours",xaxis_minor_tick_hours,self.plot_params,[3,9,15,21])
        # errorBand = getParamOrDefaultTo("errorBand",errorBand,self.plot_params)
        # error_band_fmt = getParamOrDefaultTo("error_band_fmt",error_band_fmt,self.plot_params,"k-")
        # forecast_table = getParamOrDefaultTo("forecast_table",forecast_table,self.plot_params,True)
        # footnote_height = getParamOrDefaultTo("footnote_height",footnote_height,self.plot_params)
        
        for node in self.nodes:
            node.plotProno(
                **kwargs
                # output_dir,
                # figsize=figsize,
                # title=title,
                # markersize=markersize,
                # obs_label=obs_label,
                # tz=tz,
                # prono_label=prono_label,
                # footnote=footnote,
                # errorBandLabel=errorBandLabel,
                # obsLine=obsLine,
                # prono_annotation=prono_annotation,
                # obs_annotation=obs_annotation,
                # forecast_date_annotation=forecast_date_annotation,
                # ylim=ylim,
                # datum_template_string=datum_template_string,
                # title_template_string=title_template_string,
                # x_label=x_label,
                # y_label=y_label,
                # xlim=xlim,
                # text_xoffset=text_xoffset,
                # prono_fmt=prono_fmt,
                # annotate=annotate,
                # table_columns=table_columns,
                # date_form=date_form,
                # xaxis_minor_tick_hours=xaxis_minor_tick_hours,
                # errorBand=errorBand,
                # error_band_fmt=error_band_fmt,
                # forecast_table=forecast_table,
                # footnote_height=footnote_height
            )
    def printReport(self) -> dict:
        """
        Print topology report
        
        Returns:
        -------
        dict"""
        report = {"nodes":[]}
        for node in self.nodes:
            node_report = {
                "id": node.id,
                "name": node.name,
                "variables": {}
            }
            for variable in node.variables.values():
                variable_report = {
                    "id": variable.id
                }
                if isinstance(variable,ObservedNodeVariable):
                    if len(variable.series):
                        variable_report["series_obs"] = []
                        for serie in variable.series:
                            serie_notnull = serie.data[serie.data["valor"].notnull()]
                            serie_report = {
                                "series_id": serie.series_id,
                                "len": len(serie.data),
                                "outliers": [(x[0].isoformat(), x[1], x[2]) for x in list(serie.outliers_data.itertuples(name=None))] if serie.outliers_data is not None else None,
                                "jumps": [(x[0].isoformat(), x[1], x[2]) for x in list(serie.jumps_data.itertuples(name=None))] if serie.jumps_data is not None else None,
                                "nulls": int(serie.data["valor"].isna().sum()),
                                "tag_counts": serie.data.groupby("tag").size().to_dict(),
                                "min_date": serie_notnull.index[0].isoformat() if len(serie_notnull) else None,
                                "max_date": serie_notnull.index[-1].isoformat() if len(serie_notnull) else None
                            }
                            variable_report["series_obs"].append(serie_report)
                elif isinstance(variable,DerivedNodeVariable):
                    if len(variable.series):
                        variable_report["series_der"] = []
                        for serie in variable.series:
                            serie_notnull = serie.data[serie.data["valor"].notnull()]
                            serie_report = {
                                "series_id": serie.series_id,
                                "len": len(serie.data),
                                "nulls": int(serie.data["valor"].isna().sum()),
                                "tag_counts": serie.data.groupby("tag").size().to_dict(),
                                "min_date": serie_notnull.index[0].isoformat() if len(serie_notnull) else None,
                                "max_date": serie_notnull.index[-1].isoformat() if len(serie_notnull) else None
                            }
                            variable_report["series_der"].append(serie_report)
                if variable.series_prono is not None and len(variable.series_prono):
                    variable_report["series_prono"] = []
                    for serie in variable.series_prono:
                        serie_notnull = serie.data[serie.data["valor"].notnull()]
                        serie_report = {
                            "series_id": serie.metadata["series_id"],
                            "cal_id": serie.metadata["cal_id"],
                            "forecast_date": serie.metadata["forecast_date"].isoformat() if serie.metadata["forecast_date"] is not None else None,
                            "len": len(serie.data),
                            "outliers": [(x[0].isoformat(), x[1], x[2]) for x in list(serie.outliers_data.itertuples(name=None))] if serie.outliers_data is not None else None,
                            "jumps": [(x[0].isoformat(), x[1], x[2]) for x in list(serie.jumps_data.itertuples(name=None))] if serie.jumps_data is not None else None,
                            "nulls": int(serie.data["valor"].isna().sum()),
                            "tag_counts": serie.data.groupby("tag").size().to_dict(),
                            "min_date": serie_notnull.index[0].isoformat() if len(serie_notnull) else None,
                            "max_date": serie_notnull.index[-1].isoformat() if len(serie_notnull) else None,
                            "adjust_results": serie.adjust_result_dict
                        }
                        variable_report["series_prono"].append(serie_report)
                if variable.data is not None:
                    serie_notnull = variable.data[variable.data["valor"].notnull()]
                    variable_report["result"] = {
                        "len": len(variable.data),
                        "nulls": int(variable.data["valor"].isna().sum()),
                        "tag_counts": variable.data.groupby("tag").size().to_dict(),
                        "min_date": serie_notnull.index[0].isoformat() if len(serie_notnull) else None,
                        "max_date": serie_notnull.index[-1].isoformat() if len(serie_notnull) else None
                    }
                node_report["variables"][variable.id] = variable_report
            report["nodes"].append(node_report)
        return report    
    def printGraph(
        self,
        nodes : list = None,
        output_file : str = None
        ) -> None:
        """Print topology directioned graph
        
        Parameters:
        -----------
        nodes : list
            If not None, use only these nodes
            
        output_file : str
            Save graph into this file (png format)
        
        See also:
        ---------
        toGraph
        exportGraph"""
        DG = self.toGraph(nodes)
        attrs = nx.get_node_attributes(DG, 'object') 
        labels = {}
        colors = []
        for key in attrs:
            labels[key] = attrs[key]["name"] if "name" in attrs[key] else attrs[key]["id"] if "id" in attrs[key] else "N"
            colors.append("blue" if attrs[key]["node_type"] == "basin" else "red")
        # logging.debug("nodes: %i, attrs: %s, labels: %s, colors: %s" % (DG.number_of_nodes(), str(attrs.keys()), str(labels.keys()), str(colors)))
        nx.draw_shell(DG, with_labels=True, font_weight='bold', labels=labels, node_color=colors)
        if output_file is not None:
            plt.savefig(output_file, format='png')
            plt.close()
    def toGraph(self,nodes=None) -> nx.DiGraph:
        """
        Generate directioned graph from the topology.

        Parameters:
        -----------
        nodes : list or None
            List of nodes to use for building the graph. If None, uses self.topology.nodes 
        
        Returns:
        --------
        NetworkX.DiGraph (See https://networkx.org for complete documentation)

        See also:
        ---------
        printGraph
        exportGraph

        """
        if nodes is None:
            nodes = self.nodes
        DG = nx.DiGraph()
        # edges = list()
        for node in nodes:
            # logging.debug("topology.toGraph: adding node: %s. number of nodes: %i, number of edges: %i" % (node.id, DG.number_of_nodes(), DG.number_of_edges()))
            DG.add_node(node.id,object=node.toDict())
            # logging.debug("topology.toGraph: added node: %s. number of nodes: %i, number of edges: %i" % (node.id, DG.number_of_nodes(), DG.number_of_edges()))
            # if node.downstream_node is not None:
                # if type(node.downstream_node) is list:
                    # for id in node.downstream_node:
                    #     edges.append((node.id,id))
                # else:
                #     edges.append((node.id,node.downstream_node))
        # for edge in edges:
        #     if not DG.has_node(edge[1]):
        #         raise Exception("Topology error: missing downstream node %s at node %s" % (edge[1], edge[0]))
        #     DG.add_edge(edge[0],edge[1])
        return DG
    def exportGraph(
        self,
        nodes : list = None,
        output_file : str = None
        ) -> str:
        """Creates directioned graph from the plan and converts it to JSON. 
        
        Parameters:
        -----------        
        nodes : list or None
            List of nodes to use for building the graph. If None, uses self.topology.nodes 
        
        output_file : str or None
            Where to save the JSON file. If None, returns the JSON string
        
        Returns:
        --------
        str or None
        
        See also:
        ---------
        toGraph
        printGraph
        """
        DG = self.toGraph(nodes)
        # NLD = nx.node_link_data(DG)
        if output_file is not None:
            with open(output_file,"w") as f:
                f.write(json.dumps(json_graph.node_link_data(DG),indent=4)) # json.dumps(NLD,indent=4))
                f.close()
        else:
            return json.dumps(json_graph.node_link_data(DG),indent=4)
    
    def saveSeries(self):
        """For each series, series_prono, series_sim and series_output of each variable of each node, save data into file if .output_file is defined"""
        for node in self.nodes:
            node.saveSeriesSeparately()

    def storeSeries(
            self,
            bucket_name : str, 
            series : list, 
            node_id : int, 
            var_id : int, 
            series_type : str = "series"):
        self.s3_client.assertClient()
        if series is None:
            return
        for serie in series:
            if serie.data is None:
                continue
            series_id = serie.series_id
            file_name = "topology/nodes/%i/variables/%i/%s/%i/data.csv" % (node_id, var_id, series_type, series_id)
            self.s3_client.saveSeriesData(bucket_name, serie.data, file_name)


    def storeSeriesData(self,bucket_name : str = None) -> None:
        self.s3_client.assertClient()
        if bucket_name is None:
            bucket_name = self.s3_client.bucket_name
        for node in self.nodes:
            node_id = node.id
            for var_id, variable in node.variables.items():
                if variable.data is not None:
                    self.s3_client.saveSeriesData(bucket_name, variable.data, "topology/nodes/%i/variables/%i/data.csv" % (node_id, var_id))
                self.storeSeries(bucket_name,variable.series,node_id,var_id, "series")
                self.storeSeries(bucket_name,variable.series_prono,node_id,var_id, "series_prono")
                self.storeSeries(bucket_name,variable.series_sim,node_id,var_id, "series_sim")
                self.storeSeries(bucket_name,variable.series_output,node_id,var_id, "series_output")

    def restoreSeries(
            self,
            bucket_name : str, 
            series : list, 
            node_id : int, 
            var_id : int, 
            series_type : str = "series"):
        self.s3_client.assertClient()
        if series is None:
            return
        for serie in series:
            series_id = serie.series_id
            try:
                data = self.s3_client.loadSeriesData(bucket_name, "topology/nodes/%i/variables/%i/%s/%i/data.csv" % (node_id, var_id,series_type,series_id))
            except ValueError as e:
                logging.warn("node %i var %i, %s, %i: data not found in storage: %s" % (node_id, var_id, series_type, series_id, str(e)))
                continue
            serie.data = data

    def restoreSeriesData(self,bucket_name : str = None) -> None:
        self.s3_client.assertClient()
        if bucket_name is None:
            bucket_name = self.s3_client.bucket_name
        for node in self.nodes:
            node_id = node.id
            for var_id, variable in node.variables.items():
                try:
                    data = self.s3_client.loadSeriesData(bucket_name, "topology/nodes/%i/variables/%i/data.csv" % (node_id, var_id))
                except ValueError as e:
                    logging.warn("node %i var %i: data not found in storage: %s" % (node_id, var_id,str(e)))
                    continue
                variable.data = data
                self.restoreSeries(bucket_name,variable.series,node_id,var_id, "series")
                self.restoreSeries(bucket_name,variable.series_prono,node_id,var_id, "series_prono")
                self.restoreSeries(bucket_name,variable.series_sim,node_id,var_id, "series_sim")
                self.restoreSeries(bucket_name,variable.series_output,node_id,var_id, "series_output")

    def readVar(self, id : int):
        if id not in self.var_map:
            self.var_map[id]  = self.input_crud.readVar(id)
        return self.var_map[id]
        