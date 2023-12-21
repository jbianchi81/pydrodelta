from pydrodelta.util import interval2timedelta, createDatetimeSequence
from pydrodelta.derived_node_variable import DerivedNodeVariable
from pydrodelta.observed_node_variable import ObservedNodeVariable
from pydrodelta.a5 import createEmptyObsDataFrame
import pandas
import json
from datetime import timedelta

class Node:
    def __init__(self,params,timestart=None,timeend=None,forecast_timeend=None,plan=None,time_offset=None,topology=None):
        if "id" not in params:
            raise ValueError("id of node must be defined")
        self.id = params["id"]
        self.tipo = params["tipo"] if "tipo" in params else "puntual"
        if "name" not in params:
            raise ValueError("name of node must be defined")
        self.name = params["name"]
        self.timestart = timestart
        self.timeend = timeend
        self.forecast_timeend = forecast_timeend
        if "time_interval" not in params:
            raise ValueError("time_interval of node must be defined")
        self.time_interval = interval2timedelta(params["time_interval"])
        self.time_offset = time_offset if time_offset is not None else interval2timedelta(params["time_offset"]) if "time_offset" in params and params["time_offset"] is not None else None
        self.hec_node = params["hec_node"] if "hec_node" in params else None
        self._plan = plan
        self._topology = topology
        self.variables = {}
        if "variables" in params:
            for variable in params["variables"]:
                self.variables[variable["id"]] = DerivedNodeVariable(variable,self) if "derived" in variable and variable["derived"] == True else ObservedNodeVariable(variable,self)
        self.downstream_node = params["downstream_node"] if "downstream_node" in params else None
        self.node_type = params["node_type"] if "node_type" in params else "station"
    def __repr__(self):
        variables_repr = ", ".join([ "%i: Variable(id: %i, name: %s)" % (k,self.variables[k].id, self.variables[k].metadata["nombre"] if self.variables[k].metadata is not None else None) for k in self.variables.keys() ])
        return "Node(id: %i, name: %s, variables: {%s})" % (self.id, self.name, variables_repr)
    def createDatetimeIndex(self):
        return createDatetimeSequence(None, self.time_interval, self.timestart, self.timeend, self.time_offset)
    def toCSV(self,include_series_id=True,include_header=True):
        """
        returns self.variables.data as csv
        """
        data = createEmptyObsDataFrame(extra_columns={"tag":"str","series_id":"int"} if include_series_id else {"tag":"str"})
        for variable in self.variables.values():
            data = pandas.concat([data,variable.getData(include_series_id=include_series_id)])
        return data.to_csv(header=include_header)
    def outputToCSV(self,include_header=True):
        """
        returns data of self.variables.series_output as csv
        """
        data = createEmptyObsDataFrame(extra_columns={"tag":"str"})
        for variable in self.variables.values():
            data = data.join(variable.mergeOutputData())
        return data.to_csv(header=include_header) # self.series[0].toCSV()
    def variablesToSeries(self,include_series_id=False,use_node_id=False):
        """
        return node variables as array of Series objects using self.variables.data as observaciones
        """
        return [variable.toSerie(include_series_id=include_series_id,use_node_id=use_node_id) for variable in self.variables.values()]
    def variablesOutputToList(self,flatten=True):
        """
        returns series_output of variables as list of dict
        if flatten == True, merges observations into single list. Else, returns list of series objects: [{series_id:int, observaciones:[{obs1},{obs2},...]},...]
        """
        list = []
        for variable in self.variables.values():
            output_list = variable.outputToList(flatten=flatten)
            if output_list is not None:
                list.extend(output_list)
        return list
    def variablesPronoToList(self,flatten=True):
        """
        if flatten=True return list of dict each containing one forecast time-value pair (pronosticos)
        else returns list of dict each containing series_id:int and pronosticos:list 
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
        for variable in self.variables.values():
            variable.uploadData(include_prono=include_prono)
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
    def interpolate(self,limit : timedelta=None,extrapolate=False):
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
