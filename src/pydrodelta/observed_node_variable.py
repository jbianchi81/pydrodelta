from .node_variable import NodeVariable
from .node_serie import NodeSerie
from .node_serie_prono import NodeSerieProno
from .a5 import createEmptyObsDataFrame
import logging
from .util import serieFillNulls, serieRegular, createDatetimeSequence
import numpy as np
from typing import List, Union
from datetime import datetime
from pandas import DataFrame
from .types.typed_list import TypedList

class ObservedNodeVariable(NodeVariable):
    """This class represents a variable observed at a node"""
    
    @property
    def series(self) -> List[NodeSerie]:
        """Series of observed data of this variable at this node. They may represent different data sources such as different instruments at the same station or different stations at (or near) the same site"""
        return self._series  
    @series.setter
    def series(
        self,
        series
        ) -> None:
        self._series = TypedList(NodeSerie, *series) if series is not None else None
    
    @property
    def series_prono(self) -> List[NodeSerieProno]:
        """Series of forecasted data of this variable at this node. They may represent different data sources such as different model outputs"""
        return self._series_prono
    @series_prono.setter
    def series_prono(
        self,
        series
        ) -> None:
        self._series_prono = TypedList(NodeSerieProno, *series) if series is not None else None
    
    def __init__(
        self,
        series : List[Union[dict,NodeSerie]] = None,
        series_prono : List[Union[dict,NodeSerieProno]] = None,
        **kwargs,
        ):
        """
        Parameters:
        -----------
        series : List[Union[dict,NodeSerie]]
            Series of observed data of this variable at this node. They may represent different data sources such as different instruments at the same station or different stations at (or near) the same site
        
        series_prono : List[Union[dict,NodeSerieProno]]
            Series of forecasted data of this variable at this node. They may represent different data sources such as different model outputs

        \**kwargs:
            Keyword arguments inherited from the parent class (see NodeVariable :func:`~pydrodelta.NodeVariable.__init__`)
        """
        super().__init__(**kwargs)
        self.derived = False
        self.series = series
        self.series_prono = series_prono

    def loadData(
        self,
        timestart : datetime,
        timeend : datetime,
        include_prono : bool = True,
        forecast_timeend : datetime = None,
        input_api_config : dict = None,
        no_metadata : bool = False
        ) -> None:
        """
        Load data of each serie in .series from source
        
        Parameters:
        -----------
        timestart : datetime
            Begin date of data

        timeend : datetime
            End date of data

        include_prono : bool = True
            Also load forecasted data for each serie in .series_prono
        
        forecast_timeend : datetime = None
            End date of forecasted data
        
        input_api_config : dict
            Api connection parameters. Overrides global config.input_api
            
            Properties:
            - url : str
            - token : str
            - proxy_dict : dict
        
        no_metadata : bool = False
            Don't retrieve series metadata on load from api
        """
        logging.debug("Load data for observed node: %i" % (self.id))
        if self.series is not None:
            for serie in self.series:
                serie.loadData(
                    timestart,
                    timeend,
                    input_api_config,
                    no_metadata=no_metadata)
                if serie.required:
                    serie.assertNotEmpty()
        elif hasattr(self,"derived_from") and self.derived_from is not None:
            self.series = []
        else:
            self.series = []
        if include_prono and self.series_prono is not None and len(self.series_prono):
            forecast_timeend = forecast_timeend if forecast_timeend is not None else self.forecast_timeend
            for serie in self.series_prono:
                try:
                    if forecast_timeend is not None:
                        serie.loadData(timestart,forecast_timeend,input_api_config)
                    else:
                        serie.loadData(timestart,timeend,input_api_config)
                    if serie.required:
                        serie.assertNotEmpty()
                except Exception as e:
                    logging.error(e)
                    raise Exception("Node %s, Variable: %i, series_id %i, cal_id %i: failed loadData: %s" % (self._node.id,self.id,serie.series_id,serie.cal_id,str(e)))
        if self.data is None and self.series is not None and len(self.series):
            self.setDataWithNoValues()
            self.concatenate(self.series[0].data)
        else:
            self.setDataWithNoValues()
    
    def setDataWithNoValues(self) -> None:
        """Sets .data with null values and tags"""
        if self.time_interval is None:
            raise Exception("Cant' create datetime sequence: time_interval is not set")
        if self.timestart is None:
            raise Exception("Cant' create datetime sequence: timestart is not set")
        if self.timeend is None:
            raise Exception("Cant' create datetime sequence: timeend is not set")
        index = createDatetimeSequence(None, self.time_interval, self.timestart, self.timeend, self.time_offset) # self._node.createDatetimeIndex()
        data = index.to_frame(index=False,name="timestart")
        data = data.set_index("timestart")
        data["valor"] = np.nan
        data["tag"] = ""
        self.data = data
    
    def removeOutliers(self) -> bool:
        """For each serie in .series, remove outliers. Only series where lim_outliers is set are checked.
        
        Returns:
        --------
        True if at least one outlier was found : bool"""
        found_outliers = False
        for serie in self.series:
            found_outliers_ = serie.removeOutliers()
            found_outliers = found_outliers_ if found_outliers_ else found_outliers
        return found_outliers
    
    def detectJumps(self) -> bool:
        """For each serie in .series, detect jumps. Only series where lim_jump is set are checked
        
        Returns:
        --------
        True if at least one jump was found : bool"""
        found_jumps = False
        for serie in self.series:
            found_jumps_ = serie.detectJumps()
            found_jumps = found_jumps_ if found_jumps_ else found_jumps
        return found_jumps
    
    def applyOffset(self) -> None:
        """For each serie in .series, apply offset where .x_offset and/or .y_offset is set"""
        for serie in self.series:
            serie.applyOffset()
    
    def regularize(
        self,
        interpolate : bool = False
        ) -> None:
        """For each serie in .series, apply timestep regularization using stored parameters (timestart, timeend, time_interval, time_offset, forecast_timeend)
        
        Parameters:
        -----------
        interpolate : bool = False
            Interpolate missing values up to a limit of self.interpolation_limit. If false, values will be assigned to closest regular step up to a distance of self.interpolation_limit"""
        if self.timestart is None:
            raise Exception("Can't regularize: timestart is not set")
        if self.timeend is None:
            raise Exception("Can't regularize: timeend is not set")
        if self.time_interval is None:
            raise Exception("Can't regularize: time_interval is not set")
        for serie in self.series:
            serie.regularize(self.timestart,self.timeend,self.time_interval,self.time_offset,self.interpolation_limit,interpolate=interpolate)
        if self.series_prono is not None:
            for serie in self.series_prono:
                if self.forecast_timeend is not None:
                    serie.regularize(self.timestart,self.forecast_timeend,self.time_interval,self.time_offset,self.interpolation_limit,interpolate=interpolate)
                else:
                    serie.regularize(self.timestart,self.timeend,self.time_interval,self.time_offset,self.interpolation_limit,interpolate=interpolate)
    
    def fillNulls(
        self,
        inline : bool = True,
        fill_value : bool = None
        ) -> Union[DataFrame,None]:
        """
        Copies data of first series and fills its null values with the other series
        In the end it fills nulls with fill_value. If None, uses self.fill_value
        If inline=True, saves result in self.data

        Parameters:
        -----------
        inline : bool = True
            If True, save result into each series .data. Else, return null-filled DataFrame

        fill_value : bool = None
            Value to fill up with

        Returns:
        --------
        DataFrame or None : Union[DataFrame,None]
        """
        if len(self.series):
            fill_value = fill_value if fill_value is not None else self.fill_value
            data = self.series[0].data[["valor","tag"]]
            if len(self.series) > 1:
                i = 2
                for serie in self.series[1:]:
                    # if last, fills  
                    fill_value_this = fill_value if i == len(self.series) else None 
                    data = serieFillNulls(data,serie.data,fill_value=fill_value_this,tag_column="tag")
                    i = i + 1
            else:
                logging.debug("No other series to fill nulls with")
            if inline:
                self.data = data
            else:
                return data
        else:
            if self.time_interval is None:
                raise Exception("Can't create regular series. Missing time_interval")
            if self.timestart is None:
                raise Exception("Can't create regular series. Missing timestart")
            if self.timeend is None:
                raise Exception("Can't create regular series. Missing timeend")
            data = createEmptyObsDataFrame(extra_columns={"tag":str})
            data = serieRegular(
                data, 
                time_interval = self.time_interval, 
                timestart = self.timestart, 
                timeend = self.timeend, 
                time_offset = self.time_offset, 
                interpolate = False,
                tag_column = "tag"
            )
            if inline:
                self.data = data
            else:
                return data
