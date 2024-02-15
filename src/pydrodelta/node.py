from pydrodelta.util import interval2timedelta, createDatetimeSequence
from pydrodelta.derived_node_variable import DerivedNodeVariable
from pydrodelta.observed_node_variable import ObservedNodeVariable
from pydrodelta.a5 import createEmptyObsDataFrame, Serie
from pydrodelta.descriptors.int_descriptor import IntDescriptor
from pydrodelta.descriptors.string_descriptor import StringDescriptor
from pydrodelta.descriptors.datetime_descriptor import DatetimeDescriptor
from pydrodelta.descriptors.duration_descriptor import DurationDescriptor
from pydrodelta.descriptors.dict_descriptor import DictDescriptor
import pandas
import json
from datetime import datetime, timedelta
import isodate
from typing import Union, List, Dict
from pandas import DatetimeIndex

class Node:
    id = IntDescriptor()
    """Numeric identifier of the node"""
    tipo = StringDescriptor()
    """Type of node according to its geometry. Either 'puntual', 'areal' or 'raster'"""
    name = StringDescriptor()
    """Name of the node"""
    timestart = DatetimeDescriptor()
    """Start time of the observations"""
    timeend = DatetimeDescriptor()
    """End time of the observations"""
    forecast_timeend = DatetimeDescriptor()
    """Time end of the forecast"""
    time_interval = DurationDescriptor()
    """Intended time step of the observations/forecasts"""
    time_offset = DurationDescriptor()
    """Start time of the observations/forecasts relative to zero local time"""
    hec_node = DictDescriptor()
    """Mapping of this node to HECRAS geometry"""
    @property
    def variables(self) -> Dict[int,Union[ObservedNodeVariable,DerivedNodeVariable]]:
        """Variables represent the hydrologic observed/simulated properties at the node (such as discharge, precipitation, etc.). They are stored as a dictionary where and integer, the variable identifier, is used as the key, and the values are dictionaries. They may contain one or many ordered series, which contain the timestamped values. If series are missing from a variable, it is assumed that observations are not available for said variable at said node. Additionally, series_prono may be defined to represent timeseries of said variable at said node that are originated by an external modelling procedure. If series are available, said series_prono may be automatically fitted to the observed data by means of a linear regression. Such a procedure may be useful to extend the temporal extent of the variable into the forecast horizon so as to cover the full time domain of the plan. Finally, one or many series_sim may be added and it is where simulated data (as a result of a procedure) will be stored. All series have a series_id identifier which is used to read/write data from data source whether it be an alerta5DBIO instance or a csv file."""
        return self._variables
    @variables.setter
    def variables(self,variables : List[Union[DerivedNodeVariable,ObservedNodeVariable,dict]] = None):
        self._variables = {}
        if variables is not None:
            for variable in variables:
                if isinstance(variable, (DerivedNodeVariable,ObservedNodeVariable)):
                    self._variables[variable["id"]] = variable
                else:
                    self._variables[variable["id"]] = DerivedNodeVariable(variable,self) if "derived" in variable and variable["derived"] == True else ObservedNodeVariable(variable,self)
    node_type = StringDescriptor()
    """The type of node: either 'station' or 'basin'"""
    def __init__(
            self,
            id : int,
            name : str,
            time_interval : Union[dict,int],
            tipo : str="puntual",
            timestart : datetime = None,
            timeend : datetime = None,
            forecast_timeend : datetime = None,
            plan = None,
            time_offset : timedelta = None,
            topology = None,
            hec_node : dict = None,
            variables : List[Union[DerivedNodeVariable,ObservedNodeVariable]] = list(),
            node_type : str = "station"
        ):
        """Nodes represent stations and basins. These nodes are identified with a node_id and must contain one or many variables each, which represent the hydrologic observed/simulated properties at that node (such as discharge, precipitation, etc.). They are identified with a variable_id and may contain one or many ordered series, which contain the timestamped values. If series are missing from a variable, it is assumed that observations are not available for said variable at said node. Additionally, series_prono may be defined to represent timeseries of said variable at said node that are originated by an external modelling procedure. If series are available, said series_prono may be automatically fitted to the observed data by means of a linear regression. Such a procedure may be useful to extend the temporal extent of the variable into the forecast horizon so as to cover the full time domain of the plan. Finally, one or many series_sim may be added and it is where simulated data (as a result of a procedure) will be stored. All series have a series_id identifier which is used to read/write data from data source whether it be an alerta5DBIO instance or a csv file.
        
        Parameters:
        -----------
        id : int
            The node identifier

        name : str
            The node name

        time_interval : Union[dict,int]
            Intended time step of the observations/forecasts
        
        tipo : str="puntual"
            Type of node according to its geometry. Either 'puntual', 'areal' or 'raster'

        timestart : datetime = None
            Start time of the observations

        timeend : datetime = None
            End time of the observations
        
        forecast_timeend : datetime = None
            Time end of the forecast
        
        plan : Plan = None
            Plan that contains the topology that contains this node
        
        time_offset : timedelta = None
            Start time of the observations/forecasts relative to zero local time
            
        topology : Topology = None
            The topology that contains this node

        hec_node : dict = None
            Mapping of this node to HECRAS geometry
        
        variables : List[Union[DerivedNodeVariable,ObservedNodeVariable]] = list()
            The hydrologic observed/simulated properties at this node

        node_type : str = "station"
            The type of node: either 'station' or 'basin'

        """
        # if "id" not in params:
        #     raise ValueError("id of node must be defined")
        self.id = id
        self.tipo = tipo
        # if "name" not in params:
        #     raise ValueError("name of node must be defined")
        self.name = name
        self.timestart = timestart
        self.timeend = timeend
        self.forecast_timeend = forecast_timeend
        # if "time_interval" not in params:
        #     raise ValueError("time_interval of node must be defined")
        self.time_interval = time_interval
        self.time_offset = time_offset # if time_offset is not None else interval2timedelta(params["time_offset"]) if "time_offset" in params and params["time_offset"] is not None else None
        self.hec_node = hec_node
        self._plan = plan
        self._topology = topology
        self.variables = variables
        self.node_type = node_type
    def __repr__(self):
        variables_repr = ", ".join([ "%i: Variable(id: %i, name: %s)" % (k,self.variables[k].id, self.variables[k].metadata["nombre"] if self.variables[k].metadata is not None else None) for k in self.variables.keys() ])
        return "Node(id: %i, name: %s, variables: {%s})" % (self.id, self.name, variables_repr)
    def setOriginalData(self):
        """For each variable in .variables, set original data"""
        for variable in self.variables.values():
            variable.setOriginalData()
    def toDict(self) -> dict:
        """Convert node to dict"""
        return {
            "id": self.id,
            "tipo": self.tipo,
            "name": self.name,
            "timestart": self.timestart.isoformat() if self.timestart is not None else None,
            "timeend": self.timeend.isoformat() if self.timeend is not None else None,
            "forecast_timeend": self.forecast_timeend.isoformat() if self.forecast_timeend is not None else None,
            "time_interval": isodate.duration_isoformat(self.time_interval) if self.time_interval is not None else None,
            "time_offset": isodate.duration_isoformat(self.time_offset) if self.time_offset is not None else None,
            "hec_node": dict(self.hec_node) if self.hec_node is not None else None,
            "variables": [self.variables[key].toDict() for key in self.variables], 
            "node_type": self.node_type
        }
    def createDatetimeIndex(self) -> DatetimeIndex:
        """Create DatetimeIndex from .time_interval, .timestart, .timeend and .time_offset"""
        return createDatetimeSequence(None, self.time_interval, self.timestart, self.timeend, self.time_offset)
    def toCSV(
            self,
            include_series_id : bool = True,
            include_header : bool = True
            ) -> str:
        """
        returns self.variables.data as csv

        Parameters:
        -----------
        include_series_id : bool = True
            Add a column with series_id
        
        include_header : bool = True
            Add a header row
        
        Returns:
        --------
        csv string : str
        """
        data = createEmptyObsDataFrame(extra_columns={"tag":"str","series_id":"int"} if include_series_id else {"tag":"str"})
        for variable in self.variables.values():
            data = pandas.concat([data,variable.getData(include_series_id=include_series_id)])
        return data.to_csv(header=include_header)
    def outputToCSV(
            self,
            include_header : bool = True
            ) -> str:
        """
        returns data of self.variables.series_output as csv

        Parameters:
        -----------
        include_header : bool = True
            Add a header row
        
        Returns:
        --------
        csv string : csv
        """
        data = createEmptyObsDataFrame(extra_columns={"tag":"str"})
        for variable in self.variables.values():
            data = data.join(variable.mergeOutputData())
        return data.to_csv(header=include_header) # self.series[0].toCSV()
    def variablesToSeries(
            self,
            include_series_id : bool = False,
            use_node_id : bool = False
        ) -> List[Serie]:
        """
        return node variables as array of Series objects using self.variables.data as observaciones

        Parameters:
        -----------
        include_series_id : bool = False
            Add series_id property to items of Series
        
        use_node_id : bool = False
            Use node_id as series_id

        Returns:
        --------
        list of Series : List[Serie]
        """
        return [variable.toSerie(include_series_id=include_series_id,use_node_id=use_node_id) for variable in self.variables.values()]
    def variablesOutputToList(
            self,
            flatten : bool = True
        ) -> list:
        """
        For each variable in .variables, converts series_output to list of dict

        Parameters:
        -----------
        flatten : bool = True
            If True, merges observations into single list. Else, returns list of series objects: [{series_id:int, observaciones:[{obs1},{obs2},...]},...]
        
        Returns:
        --------
        list
        """
        list = []
        for variable in self.variables.values():
            output_list = variable.outputToList(flatten=flatten)
            if output_list is not None:
                list.extend(output_list)
        return list
    def variablesPronoToList(
            self,
            flatten : bool = True
        ) -> list:
        """
        For each variable in .variables, returns series_prono as a list
        
        Parameters:
        -----------
        flatten : bool = True
            If True, returns list of dict each containing one forecast time-value pair (pronosticos). Else returns list of dict each containing series_id:int and pronosticos:list 
        
        Returns:
        --------
        list
        """
        list = []
        for variable in self.variables.values():
            pronolist = variable.pronoToList(flatten=flatten)
            if pronolist is not None:
                list.extend(pronolist)
        return list
    def adjust(self,plot=True,error_band=True):
        for variable in self.variables.values():
            if variable.adjust_from is not None:
                variable.adjust(plot,error_band)
    def apply_linear_combination(self,plot=True,series_index=0):
        for variable in self.variables.values():
            if variable.linear_combination is not None:
                variable.apply_linear_combination(plot,series_index)
    def adjustProno(self,error_band=True):
        for variable in self.variables.values():
            variable.adjustProno(error_band=error_band)
    def setOutputData(self):
        for variable in self.variables.values():
            variable.setOutputData()
    def uploadData(self,include_prono=False):
        created = []
        for variable in self.variables.values():
            result = variable.uploadData(include_prono=include_prono)
            created.extend(result)
        return created
    def pivotData(self,include_prono=True):
        data = createEmptyObsDataFrame()
        for variable in self.variables.values():
            data = data.join(variable.pivotData(include_prono=include_prono))
        return data
    def pivotOutputData(self,include_tag=True):
        data = createEmptyObsDataFrame()
        for variable in self.variables.values():
            data = data.join(variable.pivotOutputData(include_tag=include_tag))
        return data
    def seriesToDataFrame(self,pivot=False,include_prono=True):
        if pivot:
            data = self.pivotData(include_prono)
        else:
            data = createEmptyObsDataFrame()
            for variable in self.variables.values():
                data = data.append(variable.seriesToDataFrame(include_prono=include_prono),ignore_index=True)
        return data
    def saveSeries(self,output,format="csv",pivot=False):
        data = self.seriesToDataFrame(pivot=pivot)
        if format=="csv":
            return data.to_csv(output)
        else:
            return json.dump(data.to_dict(orient="records"),output)
    def concatenateProno(self,inline=True,ignore_warmup=True):
        if inline:
            for variable in self.variables.values():
                variable.concatenateProno(inline=True,ignore_warmup=ignore_warmup)
        else:
            data = createEmptyObsDataFrame()
            for variable in self.variables.values():
                data = data.append(variable.concatenateProno(inline=False,ignore_warmup=ignore_warmup))
            return data
    def interpolate(self,limit : timedelta=None,extrapolate=None):
        for variable in self.variables.values():
                variable.interpolate(limit=limit,extrapolate=extrapolate)
    def plot(self):
        for variable in self.variables.values():
            variable.plot()
    def plotProno(self,output_dir=None,figsize=None,title=None,markersize=None,obs_label=None,tz=None,prono_label=None,footnote=None,errorBandLabel=None,obsLine=None,prono_annotation=None,obs_annotation=None,forecast_date_annotation=None,ylim=None,station_name=None,ydisplay=None,text_xoffset=None,xytext=None,datum_template_string=None,title_template_string=None,x_label=None,y_label=None,xlim=None):
        for variable in self.variables.values():
            variable.plotProno(output_dir=output_dir,figsize=figsize,title=title,markersize=markersize,obs_label=obs_label,tz=tz,prono_label=prono_label,footnote=footnote,errorBandLabel=errorBandLabel,obsLine=obsLine,prono_annotation=prono_annotation,obs_annotation=obs_annotation,forecast_date_annotation=forecast_date_annotation,ylim=ylim,station_name=station_name,ydisplay=ydisplay,text_xoffset=text_xoffset,xytext=xytext,datum_template_string=datum_template_string,title_template_string=title_template_string,x_label=x_label,y_label=y_label,xlim=xlim)
    def loadData(self,timestart,timeend,include_prono=True,forecast_timeend=None):
        for variable in self.variables.values():
            if isinstance(variable,ObservedNodeVariable):
                variable.loadData(timestart,timeend,include_prono,forecast_timeend)
    def removeOutliers(self):
        found_outliers = False
        for variable in self.variables.values():
            if isinstance(variable,ObservedNodeVariable):
                found_outliers_ = variable.removeOutliers()
                found_outliers = found_outliers_ if found_outliers_ else found_outliers
        return found_outliers
    def detectJumps(self):
        found_jumps = False
        for variable in self.variables.values():
            if isinstance(variable,ObservedNodeVariable):
                found_jumps_ = variable.detectJumps()
                found_jumps = found_jumps_ if found_jumps_ else found_jumps
        return found_jumps
    def applyOffset(self):
        for variable in self.variables.values():
            if isinstance(variable,ObservedNodeVariable):
                variable.applyOffset()
    def regularize(self,interpolate=False):
        for variable in self.variables.values():
            if isinstance(variable,ObservedNodeVariable):
                variable.regularize(interpolate=interpolate)
    def fillNulls(self,inline=True,fill_value=None):
        for variable in self.variables.values():
            if isinstance(variable,ObservedNodeVariable):
                variable.fillNulls(inline,fill_value)
    def derive(self):
        for variable in self.variables.values():
            if isinstance(variable,DerivedNodeVariable):
                variable.derive()
    def applyMovingAverage(self):
        for variable in self.variables.values():
            variable.applyMovingAverage()
