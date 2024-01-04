from pydrodelta.node_variable import NodeVariable
from pydrodelta.node_serie import NodeSerie
from pydrodelta.node_serie_prono import NodeSerieProno
from pydrodelta.a5 import createEmptyObsDataFrame
import logging
from pydrodelta.util import serieFillNulls

class ObservedNodeVariable(NodeVariable):
    def __init__(self,params,node=None):
        super().__init__(params,node=node)
        self.series = [NodeSerie(x) for x in params["series"]] if "series" in params else None
        self.series_prono = [NodeSerieProno(x) for x in params["series_prono"]] if "series_prono" in params else None
    def loadData(self,timestart,timeend,include_prono=True,forecast_timeend=None):
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
            self.data = self.series[0].data
    def removeOutliers(self):
        found_outliers = False
        for serie in self.series:
            found_outliers_ = serie.removeOutliers()
            found_outliers = found_outliers_ if found_outliers_ else found_outliers
        return found_outliers
    def detectJumps(self):
        found_jumps = False
        for serie in self.series:
            found_jumps_ = serie.detectJumps()
            found_jumps = found_jumps_ if found_jumps_ else found_jumps
        return found_jumps
    def applyOffset(self):
        for serie in self.series:
            serie.applyOffset()
    def regularize(self,interpolate=False):
        for serie in self.series:
            serie.regularize(self._node.timestart,self._node.timeend,self._node.time_interval,self._node.time_offset,self.interpolation_limit,interpolate=interpolate)
        if self.series_prono is not None:
            for serie in self.series_prono:
                if self._node.forecast_timeend is not None:
                    serie.regularize(self._node.timestart,self._node.forecast_timeend,self._node.time_interval,self._node.time_offset,self.interpolation_limit,interpolate=interpolate)
                else:
                    serie.regularize(self._node.timestart,self._node.timeend,self._node.time_interval,self._node.time_offset,self.interpolation_limit,interpolate=interpolate)
    def fillNulls(self,inline=True,fill_value=None):
        """
        Copies data of first series and fills its null values with the other series
        In the end it fills nulls with fill_value. If None, uses self.fill_value
        If inline=True, saves result in self.data
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
                logging.warning("No other series to fill nulls with")
            if inline:
                self.data = data
            else:
                return data
        else:
            if inline:
                self.data = createEmptyObsDataFrame(extra_columns={"tag":str})
            else:
                return createEmptyObsDataFrame(extra_columns={"tag":str})
