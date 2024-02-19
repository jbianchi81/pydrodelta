from pydrodelta.node_variable import NodeVariable
from pydrodelta.node_serie import NodeSerie
from pydrodelta.node_serie_prono import NodeSerieProno
from pydrodelta.a5 import createEmptyObsDataFrame
import logging
from pydrodelta.util import serieFillNulls
import numpy as np
from typing import List, Union
from datetime import datetime
from pandas import DataFrame

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
        self._series = [x if isinstance(x,NodeSerie) else NodeSerie(**x) for x in series] if series is not None else None
    @property
    def series_prono(self) -> List[NodeSerieProno]:
        """Series of forecasted data of this variable at this node. They may represent different data sources such as different model outputs"""
        return self._series_prono
    @series_prono.setter
    def series_prono(
        self,
        series
        ) -> None:
        self._series_prono = [x if isinstance(x,NodeSerieProno) else NodeSerieProno(**x) for x in series] if series is not None else None
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
        self.series = series
        self.series_prono = series_prono
    def loadData(
        self,
        timestart : datetime,
        timeend : datetime,
        include_prono : bool = True,
        forecast_timeend : datetime = None
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
        """
        logging.debug("Load data for observed node: %i" % (self.id))
        if self.series is not None:
            for serie in self.series:
                # try:
                    serie.loadData(timestart,timeend)
                # except Exception as e:
                #     raise Exception("Node %s, Variable: %i, series_id %i: failed loadData: %s" % (self._node.id,self.id,serie.series_id,str(e)))
        elif hasattr(self,"derived_from") and self.derived_from is not None:
            self.series = []
        else:
            self.series = []
        if include_prono and self.series_prono is not None and len(self.series_prono):
            for serie in self.series_prono:
                if forecast_timeend is not None:
                    try:
                        serie.loadData(timestart,forecast_timeend)
                    except Exception as e:
                        raise "Node %s, Variable: %i, series_id %i, cal_id %: failed loadData: %s" % (self._node.id,self.id,serie.series_id,serie.cal_id,str(e))
                else:
                    try:
                        serie.loadData(timestart,timeend)
                    except Exception as e:
                        raise "Node %s, Variable: %i, series_id %i, cal_id %: failed loadData: %s" % (self._node.id,self.id,serie.series_id,serie.cal_id,str(e))
        if self.data is None and self.series is not None and len(self.series):
            self.setDataWithNoValues()
            self.concatenate(self.series[0].data)
        else:
            self.setDataWithNoValues()
    def setDataWithNoValues(self) -> None:
        """Sets .data with null values and tags"""
        index = self._node.createDatetimeIndex()
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
        """For each serie in .series, apply timestep regularization using parameters stored in ._node (timestart, timeend, time_interval, time_offset)
        
        Parameters:
        -----------
        interpolate : bool = False
            Interpolate missing values up to a limit of self.interpolation_limit. If false, values will be assigned to closest regular step up to a distance of self.interpolation_limit"""
        for serie in self.series:
            serie.regularize(self._node.timestart,self._node.timeend,self._node.time_interval,self._node.time_offset,self.interpolation_limit,interpolate=interpolate)
        if self.series_prono is not None:
            for serie in self.series_prono:
                if self._node.forecast_timeend is not None:
                    serie.regularize(self._node.timestart,self._node.forecast_timeend,self._node.time_interval,self._node.time_offset,self.interpolation_limit,interpolate=interpolate)
                else:
                    serie.regularize(self._node.timestart,self._node.timeend,self._node.time_interval,self._node.time_offset,self.interpolation_limit,interpolate=interpolate)
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
            if inline:
                self.data = createEmptyObsDataFrame(extra_columns={"tag":str})
            else:
                return createEmptyObsDataFrame(extra_columns={"tag":str})
