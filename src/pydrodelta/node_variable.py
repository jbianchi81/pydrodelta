from a5client import Crud, Serie
from .node_serie import NodeSerie
from .node_serie_prono import NodeSerieProno
import os
from .util import adjustSeries, linearCombination, adjustSeries, serieFillNulls, interpolateData, getParamOrDefaultTo, plot_prono, coalesce
import pandas
import logging
import json
from datetime import datetime, timedelta
import matplotlib.pyplot as plt
import isodate
from .config import config
from typing import List, Union, Tuple
from .descriptors.int_descriptor import IntDescriptor
from .descriptors.dict_descriptor import DictDescriptor
from .descriptors.float_descriptor import FloatDescriptor
from .descriptors.datetime_descriptor import DatetimeDescriptor
from .descriptors.duration_descriptor import DurationDescriptor
from .descriptors.duration_descriptor_default_none import DurationDescriptorDefaultNone
from .descriptors.bool_descriptor import BoolDescriptor
from .descriptors.dataframe_descriptor import DataFrameDescriptor
from .descriptors.string_descriptor import StringDescriptor
from .types.adjust_from_dict import AdjustFromDict
from .types.linear_combination_dict import LinearCombinationDict
from .types.typed_list import TypedList

input_crud = Crud(**config["input_api"])
output_crud = Crud(**config["output_api"])


class NodeVariable:
    """
    Variables represent the hydrologic observed/simulated properties at the node (such as discharge, precipitation, etc.). They are stored as a dictionary where and integer, the variable identifier, is used as the key, and the values are dictionaries. They may contain one or many ordered series, which contain the timestamped values. If series are missing from a variable, it is assumed that observations are not available for said variable at said node. Additionally, series_prono may be defined to represent timeseries of said variable at said node that are originated by an external modelling procedure. If series are available, said series_prono may be automatically fitted to the observed data by means of a linear regression. Such a procedure may be useful to extend the temporal extent of the variable into the forecast horizon so as to cover the full time domain of the plan. Finally, one or many series_sim may be added and it is where simulated data (as a result of a procedure) will be stored. All series have a series_id identifier which is used to read/write data from data source whether it be an alerta5DBIO instance or a csv file.
    """
    
    id = IntDescriptor()
    """Id of the variable"""
    
    metadata = DictDescriptor()
    """Variable metadata"""
    
    fill_value = FloatDescriptor()
    """Value used to fill missing values"""
    
    @property
    def series_output(self) -> List[NodeSerie]:
        """Output series of the analysis procedure"""
        return self._series_output
    
    @series_output.setter
    def series_output(
        self,
        series : List[Union[NodeSerie,dict]] = None
        ) -> None:
        if series is None:
            self._series_output = None
            return
        self._series_output = TypedList(NodeSerie, *series, unique_id_property = "series_id", node_variable = self)  # [x if isinstance(x,NodeSerie) else NodeSerie(**x) for x in series] if series is not None else None
    
    @property
    def series_sim(self) -> List[NodeSerieProno]:
        """Output series of the simulation procedure"""
        return self._series_sim
    @series_sim.setter
    def series_sim(
        self,
        series : List[Union[NodeSerie,dict]] = None
        ) -> None:
        if series is None:
            self._series_sim = None
            return
        self._series_sim = TypedList(NodeSerieProno, unique_id_property = "series_id", node_variable = self)
        for serie in series:
            if isinstance(serie,NodeSerieProno):
                self._series_sim.append(serie)
            else:
                serie["cal_id"] = serie["cal_id"] if "cal_id" in serie else self._node._plan.id if self._node is not None and self._node._plan is not None else None
                self._series_sim.append(serie) # NodeSerieProno(**serie))
    
    time_support = DurationDescriptorDefaultNone()
    """Time support of the observations . The time interval that the observation is representative of."""
    
    adjust_from = DictDescriptor()
    """Adjust configuration. 'truth' and 'sim' are the indexes of the .series to be used for the linear regression adjustment."""
    
    linear_combination = DictDescriptor()
    """Linear combination configuration. 'intercept' is the additive term (bias) and the 'coefficients' are the ordered coefficients for each series (independent variables)."""
    
    interpolation_limit = IntDescriptor()
    """Maximum rows to interpolate"""
    
    extrapolate = BoolDescriptor()
    """If true, extrapolate data up to a distance of limit"""
    
    data = DataFrameDescriptor()
    """DataFrame containing the variable time series data"""
    
    original_data = DataFrameDescriptor()
    """DataFrame containing the original variable time series data"""
    
    adjust_results = DictDescriptor()
    """Model resultant of the adjustment procedure"""
    
    name = StringDescriptor()
    """Arbitrary name of the variable"""
    
    time_interval = DurationDescriptor()
    """Intended time spacing of the variable"""

    derived = BoolDescriptor()
    """Indicates wether the variable is derived"""

    @property
    def node_id(self) -> Union[int,str]:
        self._node.id if self._node is not None else "unknown"
    
    timestart = DatetimeDescriptor()
    """Begin date (overrides _node.timestart)"""

    timeend = DatetimeDescriptor()
    """End date (overrides _node.timeend)"""

    time_offset = DurationDescriptor()
    """Time start offset relative to 00:00 (overrides _node.time_offset)"""

    forecast_timeend = DatetimeDescriptor()
    """Forecast end date"""

    def __init__(
        self,
        id : int,
        node = None,
        fill_value : float = None,
        series_output : List[Union[dict,NodeSerie]] = None,
        output_series_id : int = None,
        series_sim : List[Union[dict,NodeSerie]] = None,
        time_support : Union[datetime,dict,int,str] = None,
        adjust_from : AdjustFromDict = None,
        linear_combination : LinearCombinationDict = None,
        interpolation_limit : int = None,
        extrapolate : bool = None,
        time_interval : Union[timedelta,dict,float] = None,
        name : str = None,
        timestart : datetime = None,
        timeend : datetime = None,
        time_offset : timedelta = None,
        forecast_timeend : datetime = None
        ):
        """
        Parameters:
        -----------
        id : int
            Id of the variable
        
        node : Node
            Node that contains this variable
        
        fill_value : float = None
            Value used to fill missing values
        
        series_output : List[Union[dict,NodeSerie]] = None
            Output series of the analysis procedure

        output_series_id : int = None
            Series id where to save the analysis procedure result

        series_sim : List[Union[dict,NodeSerie]] = None
            Output series of the simulation procedure

        time_support : Union[datetime,dict,int,str] = None
            Time support of the observations . The time interval that the observation is representative of.

        adjust_from : AdjustFromDict = None
            Adjust configuration. 'truth' and 'sim' are the indexes of the .series to be used for the linear regression adjustment.

        linear_combination : LinearCombinationDict = None
            Linear combination configuration. 'intercept' is the additive term (bias) and the 'coefficients' are the ordered coefficients for each series (independent variables)

        interpolation_limit : Union[timedelta,dict,float] = None
            Maximum rows to interpolate
        
        extrapolate : bool = False
            If true, extrapolate data up to a distance of limit

        time_interval : Union[timedelta,dict,float] = None
            Intended time spacing of the variable
        
        name :  str = None

            Arbitrary name of the variable

        timestart : datetime = None

            Begin date (overrides _node.timestart)

        timeend : datetime = None

            End date (overrides _node.timeend)

        time_offset : timedelta = None

            Time start offset relative to 00:00 (overrides _node.time_offset)

        forecast_timeend : datetime = None

            Forecast end date
        """
        self.id = id
        self._node = node
        self.metadata = self._node.readVar(self.id) if self._node is not None else input_crud.readVar(self.id)
        self.fill_value = fill_value
        self.series_output = series_output if series_output is not None else [NodeSerie(series_id=output_series_id)]  if output_series_id is not None else None
        self.series_sim = series_sim if series_sim is not None else None
        self.time_support = time_support
        if self.time_support is None and self.metadata is not None:
            self.time_support = self.metadata["timeSupport"]
        self.adjust_from = adjust_from
        self.linear_combination = linear_combination
        self.interpolation_limit = interpolation_limit # in rows
        self.extrapolate = extrapolate
        if self.interpolation_limit is not None and self.interpolation_limit <= 0:
            raise("Invalid interpolation_limit: must be greater than 0")
        self.data = None
        self.original_data = None
        self.adjust_results = None
        self.time_interval = time_interval if time_interval is not None else self._node.time_interval if self._node is not None else None
        self.name = name if name is not None else "%s_%s" % (self._node.name, self.id) if self._node is not None else "0_%s" % str(self.id)
        self.derived = False
        self.timestart = timestart if timestart is not None else self._node.timestart if self._node is not None else None
        self.timeend = timeend if timeend is not None else self._node.timeend if self._node is not None else None
        self.time_offset = time_offset if time_offset is not None else self._node.time_offset if self._node is not None else None
        self.forecast_timeend = forecast_timeend if forecast_timeend is not None else self._node.forecast_timeend if self._node is not None else None
    
    def __repr__(self):
        series_str = ", ".join(["Series(type: %s, id: %i)" % (s.type, s.series_id) for s in self.series])
        return "Variable(id: %i, name: %s, count: %i, series: [%s])" % (self.id, self.metadata["nombre"] if self.metadata is not None else None, len(self.data) if self.data is not None else 0, series_str)
    
    def __getitem__(self, key):
        """key is passed to self.data.loc"""
        if self.data is None:
            return None
        return self.data.loc[key]

    def setOriginalData(self):
        """copies .data into .original_data"""
        self.original_data = self.data.copy(deep=True)
    
    def toDict(self) -> dict:
        """Convert this variable to dict"""
        return {
            "id": self.id,
            "metadata": self.metadata,
            "fill_value": self.fill_value,
            "series_output": [serie.toDict() for serie in self.series_output] if self.series_output is not None else None,
            "series_sim": [serie.toDict() for serie in self.series_sim] if self.series_sim is not None else None,
            "time_support": isodate.duration_isoformat(self.time_support) if self.time_support is not None else None, 
            "adjust_from": self.adjust_from,
            "linear_combination": self.linear_combination,
            "interpolation_limit": self.interpolation_limit,
            "data": self.dataAsDict(),
            "original_data": self.originalDataAsDict(),
            "adjust_results": self.adjust_results,
            "name": self.name,
            "time_interval": isodate.duration_isoformat(self.time_interval) if self.time_interval is not None else None
        }
    def toJSON(self) -> str:
        """Convert this variable to JSON string"""
        return json.dumps(self.toDict())
    
    def dataAsDict(self) -> List[dict]:
        """Convert this variable's data to a list of records (dict)"""
        if self.data is None:
            return None
        data = self.data.reset_index().to_dict("records") 
        for row in data:
            row["timestart"] = row["timestart"].isoformat() if "timestart" in row else None
        return data
    
    def originalDataAsDict(self) -> List[dict]:
        """Convert this variable's original data to a list of records (dict)"""
        if self.original_data is None:
            return None
        data = self.original_data.reset_index().to_dict("records") 
        for row in data:
            row["timestart"] = row["timestart"].isoformat() if "timestart" in row else None
        return data
    
    def getData(
        self,
        include_series_id : bool = False
        ) -> pandas.DataFrame:
        """Read this variable's .data
        
        Parameters:
        -----------
        include_series_id: bool = False
            Add a series_id column
        
        Returns:
        --------
        data : DataFrame"""
        if self.data is None:
            return None
        data = self.data[["valor","tag"]] # self.concatenateProno(inline=False) if include_prono else self.data[["valor","tag"]] # self.series[0].data            
        if include_series_id:
            data["series_id"] = self.series_output.series_id if type(self.series_output) == NodeSerie else self.series_output[0].series_id if type(self.series_output) == list else None
        return data
    
    def toCSV(
        self,
        include_series_id : bool = False,
        include_header : bool = True
        ) -> str:
        """
        Convert this variable's .data to a csv string

        Parameters:
        -----------
        include_series_id : bool = False
            Add a series_id column
        
        include_header : bool = True
            Add a header row
        
        Returns:
        --------
        A csv string : str
        """
        data = self.getData(include_series_id=include_series_id)
        return data.to_csv(header=include_header) # self.series[0].toCSV()
    
    def mergeOutputData(self) -> pandas.DataFrame:
        """
        Merges data of all self.series_output into a single dataframe

        Returns:
        --------
        merged data : DataFrame
        """
        data = None
        i = 0
        for serie in self.series_output:
            i = i + 1
            series_data = serie.data[["valor","tag"]]
            series_data["series_id"] = serie.series_id
            data = series_data if i == 1 else pandas.concat([data,series_data],axis=0)
        return data
    
    def outputToCSV(
        self,
        include_header : bool = True
        ) -> str:
        """
        Converts .data of self.series_output to a csv string

        Parameters:
        -----------
        include_header : bool = True
            Add a header row
        
        Returns:
        --------
        A csv string : str
        """
        data = self.mergeOutputData()
        return data.to_csv(header=include_header) # self.series[0].toCSV()
    
    def toSerie(
        self,
        include_series_id : bool = False,
        use_node_id : bool = False
        ) -> Serie:
        """
        Convert variable to Serie object using self.data as observaciones
    
        Parameters:
        -----------
        include_series_id : bool = False
            Add series_id attribute to observaciones
        
        use_node_id : bool = False
            Use node id as series_id

        Returns:
        --------
        A Serie object : Serie
        """
        if use_node_id and self._node is None:
            raise Exception("Can't use_node_id: node is not set")
        observaciones = self.toList(include_series_id=include_series_id,use_node_id=use_node_id)
        series_id = self.series_output[0].series_id if not use_node_id else self.node_id
        return Serie(
            tipo = self._node.tipo if self._node is not None else None,
            id = series_id,
            observaciones = observaciones
        )
    
    def toList(
        self,
        include_series_id : bool = False,
        use_node_id : bool = False
        ) -> List[dict]:
        """
        Convert .data to a json-serializable list of dicts

        Parameters:
        -----------
        include_series_id : bool = False
            Add series_id attribute to observaciones

        use_node_id : bool = False
            Use node id as series_id

        Returns:
        --------
        A list of records : List[dict]
        """
        if use_node_id and self._node is None:
            raise Exception("Can't use_node_id: node is not set")
        data = self.data[self.data.valor.notnull()].copy()
        # data.loc[:,"timestart"] = data.index
        data = data.reset_index()
        data.loc[:,"timeend"] = [x + self.time_support for x in data["timestart"]] if self.time_support is not None else data["timestart"]
        # data.loc[:,"timestart"] = [x.isoformat() for x in data["timestart"]]
        data["timestart"] = data["timestart"].apply(lambda x: x.isoformat())
        # data.loc[:,"timeend"] = [x.isoformat() for x in data["timeend"]]
        data["timeend"] = data["timeend"].apply(lambda x: x.isoformat())
        if len(data) and include_series_id:
            data.loc[:,"series_id"] = self.node_id if use_node_id else self.series_output[0].series_id if self.series_output is not None else None
        return data.to_dict(orient="records")
    
    def outputToList(
        self,
        flatten : bool = True
        ) -> Union[List[dict],List[Serie]]:
        """
        Convert series_output to list of records (dict)

        Parameters:
        -----------
        flatten : bool = True
            If True, merges observations into single list. Else, returns list of series objects: [{series_id:int, observaciones:[{obs1},{obs2},...]},...]
        
        Returns:
        List of records (dict) or list of Series : Union[List[dict],List[Serie]]
        """
        if self.series_output is None:
            return None
        if self.series_output[0].data is None:
            self.setOutputData()
        list = []
        for serie in self.series_output:
            if flatten:
                obs_list = serie.toList(include_series_id=True,timeSupport=self.time_support,remove_nulls=True)
                list.extend(obs_list)
            else:
                series_dict = serie.toDict(timeSupport=self.time_support, as_prono=False, remove_nulls=True)
                list.append(series_dict)
        return list
    
    def pronoToList(
        self,
        flatten : bool = True,
        qualifiers : List[str] = None
        ) -> Union[List[dict],List[Serie]]:
        """
        Convert series_prono to list of records (dict)

        Parameters:
        -----------
        flatten : bool = True
            If True, merges observations into single list. Else, returns list of series objects: [{series_id:int, observaciones:[{obs1},{obs2},...]},...]
        
        qualifiers : List[str] = None
            Add these qualifiers as additional observations

        Returns:
        List of records (dict) or list of Series : Union[List[dict],List[Serie]]
        """
        if self.series_prono is None:
            return None
        list = []
        for serie in self.series_prono:
            if flatten:
                prono_list = serie.toList(include_series_id=True,timeSupport=self.time_support,remove_nulls=True, qualifiers=qualifiers)
                list.extend(prono_list)
            else:
                series_dict = serie.toDict(timeSupport=self.time_support, as_prono=True, remove_nulls=True, qualifiers=qualifiers)
                list.append(series_dict)
        return list
    
    def adjust(
        self,
        plot : bool = True,
        error_band : bool = True,
        sim : int = None,
        truth : int = None
        ) -> None:
        """By means of a linear regression, adjust data of one of .series ('sim') from data of another .series ('truth')
        
        Parameters:
        -----------
        plot : bool = True
            Plot results

        error_band : bool = True
            Add error band to results

        sim : int = None
            Index of the series to adjust. If None, takes .adjust_from["sim"]

        truth : int = None
            Index of the series to adjust from. In None, takes .adjust_from["truth"]"""
        truth = truth if truth is not None else self.adjust_from["truth"]
        sim = sim if sim is not None else self.adjust_from["sim"]
        truth_data = self.series[truth].data
        sim_data = self.series[sim].data
        self.series[sim].original_data = sim_data.copy(deep=True)
        try:
            adj_serie, tags, model = adjustSeries(sim_data,truth_data,method=self.adjust_from["method"],plot=plot,tag_column="tag",title=self.name)
        except ValueError:
            logging.debug("No observations found to estimate coefficients. Skipping adjust")
            return
        # self.series[self.adjust_from["sim"]].data["valor"] = adj_serie
        self.data.loc[:,"valor"] = adj_serie
        self.data.loc[:,"tag"] = tags
        self.adjust_results = model
        if error_band:
            self.data.loc[:,"error_band_01"] = adj_serie + self.adjust_results["quant_Err"][0.001]
            self.data.loc[:,"error_band_99"] = adj_serie + self.adjust_results["quant_Err"][0.999]     
    
    def apply_linear_combination(
        self,
        plot : bool = True,
        series_index : int = 0,
        linear_combination : LinearCombinationDict = None
        ) -> None:
        """Apply linear combination
        
        Parameters:
        -----------
        plot : bool = True
            Plot results

        series_index : int = 0
            Index of target series

        linear_combination : LinearCombinationDict = None
            Linear combination parameters: "intercept" and "coefficients". If None, reads from self.linear_combination
        """

        self.series[series_index].original_data = self.series[series_index].data.copy(deep=True)
        #self.series[series_index].data.loc[:,"valor"] = util.linearCombination(self.pivotData(),self.linear_combination,plot=plot)
        self.data.loc[:,"valor"],  self.data.loc[:,"tag"] = linearCombination(self.pivotData(),linear_combination if linear_combination is not None else self.linear_combination,plot=plot,tag_column="tag")
    
    def applyMovingAverage(self) -> None:
        """For each serie in .series, apply moving average"""
        if self.series is not None:
            for serie in self.series:
                if isinstance(serie,NodeSerie) and serie.moving_average is not None:
                    serie.applyMovingAverage()
    
    def adjustProno(
        self,
        error_band : bool = True,
        warmup : int = None,
        tail : int = None,
        sim_range : Tuple[float,float] = None,
        method : str = "lfit"
        ) -> None:
        """For each serie in series_prono where adjust is True, perform adjustment against observed data (series[0].data). series_prono[x].data are updated with the results of the adjustment
        
        Parameters:
        -----------
        error_band : bool = True
            Add error band to results
            
        warmup : int = None

        tail : int = None

        sim_range : Tuple[float,float] = None

        method : str = "lfit"
            options:
            - lfit: Linear regression
            - arima: ARIMA
        """
        if not self.series_prono or not len(self.series_prono) or self.series is None or len(self.series) == 0 or self.series[0].data is None:
            return
        truth_data = self.series[0].data
        for serie_prono in [x for x in self.series_prono if x.adjust]:
            sim_data = serie_prono.data[serie_prono.data["tag"]=="prono"]
            # serie_prono.original_data = sim_data.copy(deep=True)
            try:
                adj_serie, tags , model = adjustSeries(
                    sim_data,
                    truth_data,
                    method=method,
                    plot=True,
                    tag_column="tag",
                    title="%s @ %s" % (serie_prono.name, self.name),
                    warmup = coalesce(warmup, serie_prono.warmup),
                    tail = coalesce(tail, serie_prono.tail),
                    sim_range = coalesce(sim_range, serie_prono.sim_range)
                )
            except ValueError:
                logging.debug("No observations found to estimate coefficients. Skipping adjust")
                return
            # self.series[self.adjust_from["sim"]].data["valor"] = adj_serie
            serie_prono.data.loc[:,"valor"] = adj_serie
            serie_prono.data.loc[:,"tag"] = tags
            serie_prono.adjust_results = model
            if error_band:
                serie_prono.data.loc[:,"error_band_01"] = adj_serie + serie_prono.adjust_results["quant_Err"][0.001]
                serie_prono.data.loc[:,"error_band_99"] = adj_serie + serie_prono.adjust_results["quant_Err"][0.999]     
    
    def setOutputData(self) -> None:
        """Copies .data into each series_output .data, and applies offset where .x_offset and/or y_offset are set"""
        if self.series_output is not None and self.data is not None:
            for serie in self.series_output:
                serie.data = self.data[["valor","tag"]]
                serie.applyOffset()
    
    def uploadData(
        self,
        include_prono : bool = False,
        api_config : dict = None,
        ) -> list:
        """
        Uploads series_output (analysis results) to output API. For each serie in series_output, it converts .data into a list of records, uploads the records using .series_id as the series identifier, then concatenates all responses into a single list which it returns

        Parameters:
        -----------
        include_prono : bool = False
            Includes the forecast period of data

        api_config : dict = None
            Api connection parameters. Overrides global config.output_api
            
            Properties:
            - url : str
            - token : str
            - proxy_dict : dict

        Returns:
        --------
        Created observations : list 
        """
        api_client = Crud(**api_config) if api_config is not None else output_crud
        if self.series_output is not None:
            if self.series_output[0].data is None:
                self.setOutputData()
            obs_created = []
            for serie in self.series_output:
                obs_list = serie.toList(remove_nulls=True,max_obs_date=None if include_prono else self.max_obs_date if hasattr(self,"max_obs_date") else None) # include_series_id=True)
                if serie.save_post is not None:
                    json.dump(
                        obs_list,
                        open(
                            os.path.join(
                                config["PYDRODELTA_DIR"], 
                                serie.save_post
                            ),
                            "w"
                        )
                    )
                    logging.info("Wrote output of node %s, variable %i, serie %i to %s" % (self.node_id,self.id, serie.series_id, serie.save_post))
                try:
                    created = api_client.createObservaciones(obs_list,series_id=serie.series_id)
                    obs_created.extend(created)
                except Exception as e:
                    logging.error(str(e))
            return obs_created
        else:
            logging.info("Missing output series for node %i, variable %i, skipping upload" % (self._node.id, self.id))
            return []
    
    def pivotData(
        self,
        include_prono : bool = True
        ) -> pandas.DataFrame:
        """Joins all series into a single pivoted DataFrame
        
        Parameters:
        -----------
        include_prono : bool = True
            Join also all series in series_prono
            
        Returns:
        --------
        pivoted data : DataFrame"""
        data = self.series[0].data[["valor",]]
        for serie in self.series:
            if len(serie.data):
                data = data.join(serie.data[["valor",]].dropna(),how='outer',rsuffix="_%s" % serie.series_id,sort=True)
        if include_prono and self.series_prono is not None and len(self.series_prono):
            for serie in self.series_prono:
                data = data.join(serie.data[["valor",]].dropna(),how='outer',rsuffix="_prono_%s" % serie.series_id,sort=True)
        del data["valor"]
        return data
    
    def pivotOutputData(
        self,
        include_tag : bool = True
        ) -> pandas.DataFrame:
        """Joins all series in series_output into a single pivoted DataFrame
        
        Parameters:
        -----------
        include_tag : bool = True
            Add columns for tags
            
        Returns:
        --------
        pivoted data : DataFrame"""
        columns = ["valor","tag"] if include_tag else ["valor"]
        data = self.series_output[0].data[columns]
        for serie in self.series_output:
            if len(serie.data):
                data = data.join(serie.data[columns],how='outer',rsuffix="_%s" % serie.series_id,sort=True)
        for column in columns:
            del data[column]
        return data

    def pivotSimData(
        self
        ) -> pandas.DataFrame:
        """Joins all series in series_sim into a single pivoted DataFrame
                   
        Returns:
        --------
        pivoted data : DataFrame"""
        if self.series_sim is None:
            return None
        data = None
        for serie in self.series_sim:
            if serie.data is not None and len(serie.data):
                if data is None:
                    data = serie.data[["valor"]].rename(columns={"valor": serie.series_id})
                else:
                    data = data.join(serie.data[["valor"]].rename(columns={"valor": serie.series_id}),how='outer',sort=True) # rsuffix="_%s" % serie.series_id
        return data
    
    def seriesToDataFrame(
        self,
        pivot : bool = False,
        include_prono : bool = True
        ) -> pandas.DataFrame:
        """Joins all series in series_output into a single DataFrame
        
        Parameters:
        -----------
        pivot : bool = False
            Pivot series into columns
        
        include_prono : bool = True            
            Include forecast period

        Returns:
        --------
        joined data : DataFrame"""
        if pivot:
            data = self.pivotData(include_prono)
        else:
            data = self.series[0].data[["valor",]]
            data["series_id"] = self.series[0].series_id
            data["timestart"] = data.index
            data.reset_index()
            for i in range(1,len(self.series)-1):
                if len(self.series[i].data):
                    other_data = self.series[i].data[["valor",]]
                    other_data["series_id"] = self.series[i].series_id
                    other_data["timestart"] = other_data.index
                    other_data.reset_index
                    data = data.append(other_data,ignore_index=True)
        return data
    
    def saveSeries(
        self,
        output : str,
        format : str = "csv",
        pivot : bool = False
        ) -> None:
        """
        Joins all series into a single DataFrame and saves as a csv or json file
        
        Parameters:
        -----------
        output : str
            The path of file to create

        format : str = "csv"
            The output format. Either "csv" or "json"

        pivot : bool = False
            Pivot series into columns
        """
        data = self.seriesToDataFrame(pivot=pivot)
        if format=="csv":
            return data.to_csv(output)
        else:
            return json.dump(data.to_dict(orient="records"),output)
    
    def concatenate(
        self,
        data: pandas.DataFrame, 
        inline : bool = True, 
        overwrite : bool = False, 
        extend : bool = True
        ) -> Union[pandas.DataFrame,None]:
        """
        Concatenates self.data with data

        Parameters:
        -----------
        data: pandas.DataFrame
            Input DataFrame to concatenate with self.data
        
        inline : bool = True
            Save result into self.data. If false, return concatenated result
        
        overwrite : bool = False
            Overwrite records in self.data with records in data 
        
        extend : bool = True
            Extend index of self.data with that of data
        
        Returns:
        --------
        None or DataFrame : Union[pandas.DataFrame,None]

        """
        if self.data is None:
            raise Exception("NodeVariable.data is not defined. Can´t concatenate")
        if "tag" not in data.columns.to_list():
            data["tag"] = "sim"
        if overwrite:
            concatenated_data = serieFillNulls(data,self.data,extend=extend,tag_column="tag")
        else:
            concatenated_data = serieFillNulls(self.data,data,extend=extend,tag_column="tag")
        if inline:
            self.data = concatenated_data
            return
        else:
            return concatenated_data
    
    def concatenateOriginal(
        self, 
        data : pandas.DataFrame, 
        inline : bool = True, 
        overwrite : bool = False
        ) -> Union[pandas.DataFrame,None]:
        """
        Concatenates self.original_data with data

        Parameters:
        -----------
        data : DataFrame
            Input data to concatenate with self.original_data

        inline : bool = True
            Save result into self.data. If false, return concatenated result
        
        overwrite : bool = False
            Overwrite records in self.data with records in data 
        
        Returns:
        --------
        None or DataFrame : Union[pandas.DataFrame,None]
        """
        data["tag"] = "sim"
        if self.original_data is None:
            if inline:
                self.original_data = data.copy()
                return
            else:
                raise Exception("NodeVariable.original_data is not defined. Can´t concatenate")
        if overwrite:
            concatenated_data = serieFillNulls(data,self.original_data,extend=True,tag_column="tag")
        else:
            concatenated_data = serieFillNulls(self.original_data,data,extend=True,tag_column="tag")
        if inline:
            self.data = concatenated_data
            return
        else:
            return concatenated_data
    
    def concatenateProno(
        self,
        inline : bool = True,
        ignore_warmup : bool = True
        ) -> Union[pandas.DataFrame,None]:
        """
        Fills nulls of data with prono 

        Parameters:
        -----------
        inline : bool = True
            Save into self.data. If False return concatenated dataframe

        ignore_warmup : bool = ture
            Ignore prono before last observation
        
        Returns:
        --------
        None or DataFrame : Union[pandas.DataFrame,None]
        """
        if self.series_prono is not None and len(self.series_prono) and len(self.series_prono[0].data):
            data = self.data.copy()
            for i, serie_prono in enumerate(self.series_prono):
                prono_data = serie_prono.data[["valor","tag"]]
                self.setMaxObsDate()
                logging.debug("max_obs_date: %s" % self.max_obs_date)
                if ignore_warmup and self.max_obs_date is not None: #self.forecast_timeend is not None and ignore_warmup:
                    prono_data = prono_data[prono_data.index > self.max_obs_date]
                data = serieFillNulls(data,prono_data,extend=True,tag_column="tag")
            if inline:
                self.data = data
            else:
                return data
        else:
            logging.warning("No series_prono data found for node %i" % self.id)
            if not inline:
                return self.data
    
    def getMaxObsDate(self) -> datetime:
        max_obs_date = self.data[~pandas.isna(self.data["valor"])].index.max()
        if pandas.isnull(max_obs_date):
            return None
        return max_obs_date
    
    def setMaxObsDate(self) -> None:
        self.max_obs_date = self.getMaxObsDate()

    def interpolate(
        self,
        limit : timedelta = None,
        extrapolate : bool = None
        ) -> None:
        """Interpolate missing values in .data
        
        Parameters:
        -----------
        limit : timedelta = None
            Maximum interpolation distance
        
        extrapolate : bool = None
            Extrapolate up to a limit of limit"""
        limit = coalesce(
            limit,
            self.interpolation_limit,
            self._node._topology.interpolation_limit if self._node is not None and self._node._topology is not None else None
        )
        if self.data is not None:
            extrapolate = coalesce(
                extrapolate, 
                self.extrapolate,
                self._node._topology.extrapolate if self._node is not None and self._node._topology is not None else None,
                False
            )
            # logging.debug("limit: %s" % str(limit))
            # logging.debug("self.interpolation_limit: %s" % str(self.interpolation_limit))
            interpolation_limit = int(limit.total_seconds() / self.time_interval.total_seconds()) if isinstance(limit,timedelta) else int(limit) if limit is not None else None
            logging.debug("interpolation limit:%s" % str(interpolation_limit))
            logging.debug("extrapolate:%s" % str(extrapolate))
            if interpolation_limit is not None and interpolation_limit <= 0:
                return
            kwargs = {
                "column": "valor",
                "tag_column": "tag"
            }
            if interpolation_limit is not None:
                kwargs["interpolation_limit"] = interpolation_limit
            if extrapolate is not None:
                kwargs["extrapolate"] = extrapolate
            self.data = interpolateData(
                self.data,
                **kwargs)
    
    def saveData(
        self,
        output : str,
        format : str = "csv"
        ) -> None:
        """
        Saves .data into csv or json file

        Parameters:
        -----------
        output : str
            File path where to save

        format : str = "csv"
            Output format. Either "csv" or "json"
        """
        # data = self.concatenateProno(inline=False) if include_prono else self.data
        if format=="csv":
            return self.data.to_csv(output)
        else:
            return json.dump(self.data.to_dict(orient="records"),output)
    
    def plot(self) -> None:
        """Plot .data together with .series"""
        data = self.data[["valor",]]
        pivot_series = self.pivotData()
        data = data.join(pivot_series,how="outer")
        plt.figure(figsize=(16,8))
        if self._node is not None and self._node.timeend is not None:
            # plt.axvline(x=self._node.timeend, color="black",label="timeend")
            plt.vlines(
                x = [self._node.timeend],
                ymin = min(data.min().dropna()),
                ymax = max(data.max().dropna()),
                colors = ["gray"], 
                label = "_forecast_date",
                linestyles="dashed")
        if self._node is not None and self._node.forecast_timeend is not None:
            # plt.axvline(x=self._node.forecast_timeend, color="red",label="forecast_timeend")
            plt.vlines(
                x = [self._node.forecast_timeend],
                ymin = min(data.min().dropna()),
                ymax = max(data.max().dropna()),
                colors = ["red"], 
                label = "_forecast_timeend",
                linestyles="dashed")
        data_lines = plt.plot(data)
        plt.legend(handles=data_lines, labels=[c for c in data.columns]) # plt.legend(data.columns)
        plt.title(self.name if self.name is not None else self.id)
        # if self._node._topology.forecast_timeend is not None:
        #     plt.vlines(
        #         x = [self._node._topology.timeend],
        #         ymin = min(data.min()),
        #         ymax = max(data.max()),
        #         colors = ["gray"], 
        #         # label = "forecast date",
        #         linestyles="dashed")
    
    def plotProno(
        self,
        output_dir : str = None,
        use_series_sim : bool = None,
        **kwargs
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
        # station_name : str = None,
        # ydisplay : float = None,
        # text_xoffset : float = None,
        # xytext : tuple = None,
        # datum_template_string : str = None,
        # title_template_string : str = None,
        # x_label : str = None,
        # y_label : str = None,
        # xlim : tuple = None,
        # prono_fmt : str = None,
        # annotate : bool = True,
        # table_columns : list = None,
        # date_form : str = None,
        # xaxis_minor_tick_hours : list = None,
        # errorBand : Tuple[str,str] = None,
        # error_band_fmt : str = None,
        # forecast_table : bool = None,
        # footnote_height : float = None
        ) -> None:
        """For each serie in series_prono (or series_sim), plot .data time series together with observed data series[0].data

        Parameters:
        -----------
        output_dir : str = None
            Directory path where to save the plots

        use_series_sim : bool = False
            Use series_sim instead of series_prono. Series_sim is the output of the plan procedures while series_prono are loaded from external sources (and optionally adjusted)
            
        figsize : tuple = None
            Figure size (width, height) in cm
        
        title: str = None
            Figure title
        
        markersize : int = None
            Size of marker in points
        
        obs_label : str = None
            Label for observed data

        tz : str = None
            Time zone for horizontal axis

        prono_label : str = None
            Label for forecast data

        footnote : str = None
            Footnote text
        
        errorBandLabel : str = None
            Label for error band
        
        obsLine : bool = None
            Add a line to observed data

        prono_annotation : str = None
            Annotation for forecast data

        obs_annotation : str = None
            Annotation for observed data

        forecast_date_annotation : str = None
            Annotation for forecast date

        ylim : tuple = None
            Y axis range (min, max)

        station_name : str = None
            Station name

        ydisplay : float = None
            Y position of annotations

        text_xoffset : float = None
            X offset of annotations
        
        xytext : tuple = None
            Not used
        
        datum_template_string : str = None
            Template string for datum text

        title_template_string : str = None
            Template string for title
        
        x_label : str = None
            Label for x axis

        y_label : str = None
            Label for y axis

        xlim : tuple = None
            Range of x axis (min, max)

        prono_fmt : str = 'b-'
            Style of forecast series 
        
        annotate : bool = True
            Add observed data/forecast data/forecast date annotations
        
        table_columns : list = ["Fecha", "Nivel"]
            Which forecast dataframe columns to show. Options: 
            -   Fecha
            -   Nivel
            -   Hora
            -   dd/mm hh
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
        # locals_ = {k: v for k, v in locals().items() if v is not None and k not in ["output_dir"]}
        use_series_sim = use_series_sim if use_series_sim is not None else False
        series = self.series_sim if use_series_sim else self.series_prono
        if series is None:
            logging.debug("Missing series_prono, skipping variable")
            return
        for serie_prono in series:
            output_file = getParamOrDefaultTo(
                "output_file",
                None,
                serie_prono.plot_params,
                os.path.join(
                    output_dir,
                    "%s_%s.png" % (self.name, serie_prono.cal_id)
                ) if output_dir is not None else None
            )
            if output_file is None:
                logging.debug("Missing output_dir or output_file, skipping serie")
                continue
            defaults = {
                "output_file": output_file
            }
            if self.series[0].metadata is not None and "estacion" in self.series[0].metadata:
                defaults["station_name"] = self.series[0].metadata["estacion"]["nombre"]
            if self.series[0].metadata is not None and "estacion" in self.series[0].metadata:
                defaults["thresholds"] = self.series[0].getThresholds()
            if self.series[0].metadata is not None and "estacion" in self.series[0].metadata:
                defaults["datum"] = self.series[0].metadata["estacion"]["cero_ign"]
            if serie_prono.adjust_results is not None:
                defaults["errorBand"] = ("error_band_01","error_band_99")
                defaults["adjust_results_string"] = serie_prono.adjust_results_string
            if self._node is not None and self._node._topology is not None and self._node._topology.plot_params is not None:
                plot_prono_kwargs = {**defaults, **self._node._topology.plot_params, **serie_prono.plot_params, **kwargs}
            elif serie_prono.plot_params is not None:
                plot_prono_kwargs = {**defaults, **serie_prono.plot_params, **kwargs}
            else:
                plot_prono_kwargs = {**defaults, **kwargs}
            # logging.debug("error_band: %s" % str(error_band))
            # ylim = getParamOrDefaultTo("ylim",ylim,serie_prono.plot_params)
            # ydisplay = getParamOrDefaultTo("ydisplay",ydisplay,serie_prono.plot_params)
            # text_xoffset = getParamOrDefaultTo("text_xoffset",text_xoffset,serie_prono.plot_params)
            # xytext = getParamOrDefaultTo("xytext",xytext,serie_prono.plot_params)
            # title = getParamOrDefaultTo("title",title,serie_prono.plot_params)
            # obs_label = getParamOrDefaultTo("obs_label",obs_label,serie_prono.plot_params)
            # tz = getParamOrDefaultTo("tz",tz,serie_prono.plot_params)
            # prono_label = getParamOrDefaultTo("prono_label",prono_label,serie_prono.plot_params)
            # errorBandLabel = getParamOrDefaultTo("errorBandLabel",errorBandLabel,serie_prono.plot_params)
            # obsLine = getParamOrDefaultTo("obsLine",obsLine,serie_prono.plot_params)
            # footnote = getParamOrDefaultTo("footnote",footnote,serie_prono.plot_params)
            # xlim = getParamOrDefaultTo("xlim",xlim,serie_prono.plot_params)
            # table_columns  = getParamOrDefaultTo("table_columns",table_columns,serie_prono.plot_params)
            # date_form = getParamOrDefaultTo("date_form",date_form,serie_prono.plot_params)
            # xaxis_minor_tick_hours = getParamOrDefaultTo("xaxis_minor_tick_hours", xaxis_minor_tick_hours, serie_prono.plot_params)
            # error_band_fmt = getParamOrDefaultTo("error_band_fmt",error_band_fmt,serie_prono.plot_params)
            # forecast_table = getParamOrDefaultTo("forecast_table",forecast_table,serie_prono.plot_params)
            # footnote_height = getParamOrDefaultTo("footnote_height",footnote_height,serie_prono.plot_params)
            plot_prono(
                self.data,
                serie_prono.data,
                forecast_date=serie_prono.metadata["forecast_date"] if serie_prono.metadata is not None and "forecast_date" in serie_prono.metadata else None,
                **plot_prono_kwargs
                # title=title,
                # markersize=markersize,
                # prono_label=prono_label,
                # obs_label=obs_label,
                # errorBand=errorBand,
                # errorBandLabel=errorBandLabel,
                # obsLine=obsLine,
                # prono_annotation=prono_annotation,
                # obs_annotation=obs_annotation,
                # forecast_date_annotation=forecast_date_annotation,
                # station_name=station_name,
                # thresholds=thresholds,
                # datum=datum,
                # footnote=footnote,
                # figsize=figsize,
                # ylim=ylim,
                # ydisplay=ydisplay,
                # text_xoffset=text_xoffset,
                # xytext=xytext,
                # tz=tz,
                # datum_template_string=datum_template_string,
                # title_template_string=title_template_string,
                # x_label=x_label,
                # y_label=y_label,
                # xlim=xlim,
                # prono_fmt=prono_fmt,
                # annotate=annotate,
                # table_columns=table_columns,
                # date_form=date_form,
                # xaxis_minor_tick_hours=xaxis_minor_tick_hours,
                # error_band_fmt=error_band_fmt,
                # forecast_table=forecast_table,
                # footnote_height=footnote_height
            )

    def saveSeriesSeparately(self,types : list=["series","series_prono"]):
        """For each series type (series, series_prono, series_sim and series_output), save data into file if .output_file is defined"""
        valid_series_type = ["series", "series_prono", "series_sim", "series_output"]
        for series_type in types:
            if series_type not in valid_series_type:
                raise ValueError("Invalid series type: %s" % series_type)
            series = getattr(self,series_type)
            if series is not None:
                for serie in series:
                    if serie.output_file is not None:
                        serie.saveData()
    
    def getSerie(self,series_id : int, series_type : str = "series") -> NodeSerie:
        series_list = None
        if series_type == "series":
            if self.series is None:
                raise Exception("series is not defined")
            series_list = self.series
        elif series_type == "series_prono":
            if self.series_prono is None:
                raise Exception("series_prono is not defined")
            series_list = self.series_prono
        elif series_type == "series_sim":
            if self.series_sim is None:
                raise Exception("series_sim is not defined")
            series_list = self.series_sim
        elif series_type == "series_output":
            if self.series_output is None:
                raise Exception("series_output is not defined")
            series_list = self.series_output
        else:
            raise ValueError("series_type must be one of series, series_prono, series_sim, series_output")
        for i, s in enumerate(series_list):
            if s.series_id == series_id:
                return s
        raise KeyError("Series with series_id %i not found in %s" % (series_id, series_type))
