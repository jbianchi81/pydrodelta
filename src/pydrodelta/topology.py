import jsonschema
import yaml
import os
from pydrodelta.util import tryParseAndLocalizeDate, interval2timedelta
from pathlib import Path
from datetime import timedelta, datetime
from pydrodelta.node import Node
import logging
import json
from numpy import nan, NaN
from pydrodelta.a5 import Crud, createEmptyObsDataFrame
import pandas
import matplotlib.pyplot as plt
from pydrodelta.util import getParamOrDefaultTo
from pydrodelta.observed_node_variable import ObservedNodeVariable
from pydrodelta.derived_node_variable import DerivedNodeVariable
import networkx as nx
from networkx.readwrite import json_graph
import matplotlib.backends.backend_pdf
from colour import Color
from typing import Union
from pydrodelta.validation import getSchemaAndValidate
from pandas import DataFrame

from pydrodelta.config import config

input_crud = Crud(config["input_api"])
output_crud = Crud(config["output_api"])

class Topology():
    """The topology defines a list of nodes which represent stations and basins. These nodes are identified with a node_id and must contain one or many variables each, which represent the hydrologic observed/simulated properties at that node (such as discharge, precipitation, etc.). They are identified with a variable_id and may contain one or many ordered series, which contain the timestamped values. If series are missing from a variable, it is assumed that observations are not available for said variable at said node. Additionally, series_prono may be defined to represent timeseries of said variable at said node that are originated by an external modelling procedure. If series are available, said series_prono may be automatically fitted to the observed data by means of a linear regression. Such a procedure may be useful to extend the temporal extent of the variable into the forecast horizon so as to cover the full time domain of the plan. Finally, one or many series_sim may be added and it is where simulated data (as a result of a procedure) will be stored. All series have a series_id identifier which is used to read/write data from data source whether it be an alerta5DBIO instance or a csv file."""
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
            nodes : list = list(),
            cal_id : Union[int,None] = None,
            plot_params : Union[dict,None] = None,
            report_file : Union[str,None] = None,
            plan = None
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

        nodes : List[Node]
            Nodes represent stations and basins. These nodes are identified with a node_id and must contain one or many variables each, which represent the hydrologic observed/simulated properties at that node (such as discharge, precipitation, etc.). They are identified with a variable_id and may contain one or many ordered series, which contain the timestamped values. If series are missing from a variable, it is assumed that observations are not available for said variable at said node. Additionally, series_prono may be defined to represent timeseries of said variable at said node that are originated by an external modelling procedure. If series are available, said series_prono may be automatically fitted to the observed data by means of a linear regression. Such a procedure may be useful to extend the temporal extent of the variable into the forecast horizon so as to cover the full time domain of the plan. Finally, one or many series_sim may be added and it is where simulated data (as a result of a procedure) will be stored. All series have a series_id identifier which is used to read/write data from data source whether it be an alerta5DBIO instance or a csv file.

        cal_id : int or None
            Identifier for saving analysis results as forecast (i.e. using .uploadDataAsProno)

        plot_params : dict or None
            Plotting configuration. See .plotProno
        
        report_file : str or None
            Write analysis report into this file
        
        plan : Plan
            Plan containing this topology
        """
        getSchemaAndValidate(params=locals(), name="topology")
        self.timestart = tryParseAndLocalizeDate(timestart)
        """start date of observations period"""
        self.timeend = tryParseAndLocalizeDate(timeend)
        """end date of observations period"""
        self.forecast_timeend = tryParseAndLocalizeDate(forecast_timeend) if forecast_timeend is not None else None
        """forecast horizon"""
        self.time_offset_start = interval2timedelta(time_offset_start) if time_offset_start is not None else interval2timedelta(time_offset) if time_offset is not None else timedelta(hours=0)
        """time of day where first timestep start"""
        self.time_offset_end = interval2timedelta(time_offset_end) if time_offset_end is not None else interval2timedelta(time_offset) if time_offset is not None else timedelta(hours=self.timeend.hour)
        """time of day where last timestep ends"""
        self.timestart = self.timestart.replace(hour=0,minute=0,second=0,microsecond=0) + self.time_offset_start if type(timestart) == dict else self.timestart
        """start date of observations period"""
        self.timeend = self.timeend.replace(hour=0,minute=0,second=0,microsecond=0) + self.time_offset_end if type(timeend) == dict else self.timeend
        """end date of observations period"""
        if self.timestart >= self.timeend:
            raise("Bad timestart, timeend parameters. timestart must be before timeend")
        self.interpolation_limit = interval2timedelta(interpolation_limit) if isinstance(interpolation_limit,dict) else interpolation_limit
        """maximum duration between observations for interpolation"""
        self.extrapolate = bool(extrapolate)
        """Extrapolate observations outside the observation time domain, up to a maximum duration equal to .interpolation_limit"""
        self.nodes = []
        """Nodes represent stations and basins. These nodes are identified with a node_id and must contain one or many variables each, which represent the hydrologic observed/simulated properties at that node (such as discharge, precipitation, etc.). They are identified with a variable_id and may contain one or many ordered series, which contain the timestamped values. If series are missing from a variable, it is assumed that observations are not available for said variable at said node. Additionally, series_prono may be defined to represent timeseries of said variable at said node that are originated by an external modelling procedure. If series are available, said series_prono may be automatically fitted to the observed data by means of a linear regression. Such a procedure may be useful to extend the temporal extent of the variable into the forecast horizon so as to cover the full time domain of the plan. Finally, one or many series_sim may be added and it is where simulated data (as a result of a procedure) will be stored. All series have a series_id identifier which is used to read/write data from data source whether it be an alerta5DBIO instance or a csv file."""
        for i, node in enumerate(nodes):
            if "id" not in node:
                raise Exception("Missing node.id at index %i of topology.nodes" % i)
            if node["id"] in [n.id for n in self.nodes]:
                raise Exception("Duplicate node.id = %s at index %i of topology.nodes" % (str(node["id"]), i))
            self.nodes.append(Node(params=node,timestart=self.timestart,timeend=self.timeend,forecast_timeend=self.forecast_timeend,plan=plan,time_offset=self.time_offset_start,topology=self))
        self.cal_id = cal_id
        """Identifier for saving analysis results as forecast (i.e. using .uploadDataAsProno)"""
        self.plot_params = plot_params
        """Plotting configuration. See .plotProno"""
        self.report_file = report_file
        """Write analysis report into this file"""
        self._plan = plan
        """Plan containing this topology"""
        self.graph = self.toGraph()
        """Directional graph representing this topology"""
    def __repr__(self):
        nodes_str = ", ".join(["%i: Node(id: %i, name: %s)" % (self.nodes.index(n), n.id, n.name) for n in self.nodes])
        return "Topology(timestart: %s, timeend: %s, nodes: [%s])" % (self.timestart.isoformat(), self.timeend.isoformat(), nodes_str)
    def addNode(self,node,plan=None) -> None:
        """Append node into .nodes
        
        Parameters:
        -----------
        node : dict
            Node to append
        
        plan : Node or None
            Plan that contains the topology
        """
        self.nodes.append(Node(params=node,timestart=self.timestart,timeend=self.timeend,forecast_timeend=self.forecast_timeend,plan=plan,time_offset=self.time_offset_start,topology=self))
    def batchProcessInput(self,include_prono=False) -> None:
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
        
        Parameters:
        -----------
        include_prono : bool default False
            For each variable, fill missing observations with values from series_prono
        """
        logging.debug("loadData")
        self.loadData()
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
        logging.debug("derive")
        self.derive()
        logging.debug("interpolate")
        self.interpolate(limit=self.interpolation_limit,extrapolate=self.extrapolate)
        self.setOriginalData()
        self.setOutputData()
        self.plotProno()
        if(self.report_file is not None):
            report = self.printReport()
            f = open(self.report_file,"w")
            json.dump(report,f,indent=2)
            f.close()
    def loadData(self,include_prono=True) -> None:
        """For each series of each variable of each node, load data from the source.
        
        Parameters:
        -----------
        
        include_prono : bool default True
            Load forecasted data"""
        for node in self.nodes:
            # logging.debug("loadData timestart: %s, timeend: %s, time_interval: %s" % (self.timestart.isoformat(), self.timeend.isoformat(), str(node.time_interval)))
            timestart = self.timestart - node.time_interval if node.time_interval is not None else self.timeend
            timeend = self.timeend + node.time_interval if node.time_interval is not None else self.timeend
            forecast_timeend = self.forecast_timeend+node.time_interval if self.forecast_timeend is not None and node.time_interval is not None else self.forecast_timeend
            if hasattr(node,"loadData"):
                node.loadData(timestart, timeend, forecast_timeend=forecast_timeend, include_prono=include_prono)
            # for serie in node.series:
            #     if isinstance(serie,NodeSerie):
            #         serie.loadData(self.timestart,self.timeend)
                # if include_prono and node.series_prono is not None and len(node.series_prono):
                #     for serie in node.series_prono:
                #         if isinstance(serie,NodeSerieProno):
                #             if self.forecast_timeend is not None:
                #                 serie.loadData(self.timestart,self.forecast_timeend)
                #             else:
                #                 serie.loadData(self.timestart,self.timeend)
            # if isinstance(node,observedNode):
            #     node.loadData(self.timestart,self.timeend)
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
    def concatenateProno(self) -> None:
        """For each variable of each node, if series_prono are available, concatenate series_prono into variable.data"""
        for node in self.nodes:
            for variable in node.variables.values():
                if variable.series_prono is not None:
                    variable.concatenateProno()
    def interpolate(
            self,
            limit : timedelta = None,
            extrapolate: bool = None
        ) -> None:
        """For each variable of each node, fill nulls of data by interpolation
        
        Parameters:
        -----------
        limit : timedelta
            Maximum interpolation distance
        
        extrapolate : bool
            Extrapolate up to limit
        """
        for node in self.nodes:
            node.interpolate(limit=limit,extrapolate=extrapolate)
    def setOutputData(self) -> None:
        for node in self.nodes:
            node.setOutputData()
    def toCSV(self,pivot=False) -> str:
        if pivot:
            data = self.pivotData()
            data["timestart"] = [x.isoformat() for x in data.index]
            # data.reset_index(inplace=True)
            return data.to_csv(index=False)    
        header = ",".join(["timestart","valor","tag","series_id"])
        return header + "\n" + "\n".join([node.toCSV(True,False) for node in self.nodes])
    def outputToCSV(self,pivot=False) -> str:
        if pivot:
            data = self.pivotOutputData()
            data["timestart"] = [x.isoformat() for x in data.index]
            # data.reset_index(inplace=True)
            return data.to_csv(index=False)    
        header = ",".join(["timestart","valor","tag","series_id"])
        return header + "\n" + "\n".join([node.outputToCSV(False) for node in self.nodes])
    def toSeries(self,use_node_id=False) -> list:
        """
        returns list of Series objects. Same as toList(flatten=True)
        """
        return self.toList(use_node_id=use_node_id,flatten=False)
    def toList(self,pivot=False,use_node_id=False,flatten=True) -> list:
        """
        returns list of all data in nodes[0..n].data
        
        pivot: boolean              pivot observations on index (timestart)
        use_node_id: boolean    uses node.id as series_id instead of node.output_series[0].id
        flatten: boolean        if set to False, returns list of series objects:[{"series_id":int,observaciones:[obs,obs,...]},...] (ignored if pivot=True)
        """
        if pivot:
            data = self.pivotData()
            data["timestart"] = [x.isoformat() for x in data.index]
            data.reset_index
            data["timeend"] = data["timestart"]
            return data.to_dict(orient="records")
        obs_list = []
        for node in self.nodes:
            for variable in node.variables.values():
                if flatten:
                    obs_list.extend(variable.toList(True,use_node_id=use_node_id))
                else:
                    obs_list.append(variable.toSerie(True,use_node_id=use_node_id))
        return obs_list
    def outputToList(self,pivot=False,flatten=False) -> list:
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
    def saveData(self,file : str,format="csv",pivot=False,pretty=False) -> None:
        f = open(file,"w")
        if format == "json":
            if pretty:
                obs_json = json.dumps(self.toList(pivot),ensure_ascii=False,indent=4)
            else:
                obs_json = json.dumps(self.toList(pivot),ensure_ascii=False)
            f.write(obs_json)
            f.close()
            return
        f.write(self.toCSV(pivot))
        f.close
        return
    def saveOutputData(self,file : str,format="csv",pivot=False,pretty=False) -> None:
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
    def uploadData(self,include_prono) -> list:
        """
        Uploads analysis data of all nodes as a5 observaciones
        """
        created = []
        for node in self.nodes:
            obs_created = node.uploadData(include_prono=include_prono)
            if obs_created is not None and len(obs_created):
                created.extend(obs_created)
        return created
    def uploadDataAsProno(self,include_obs=True,include_prono=False) -> dict:
        """
        Uploads analysis data of all nodes as a5 pronosticos
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
                serieslist = node.variablesPronoToList(flatten=False)
                prono["series"].extend(serieslist)
        return output_crud.createCorrida(prono)

    def pivotData(self,include_tag=True,use_output_series_id=True,use_node_id=False,nodes=None) -> DataFrame:
        if nodes is None:
            nodes = self.nodes
        columns = ["valor","tag"] if include_tag else ["valor"]
        #data = nodes[0].data[columns]
        data = createEmptyObsDataFrame(extra_columns={"tag":str})
        for node in nodes:
            for variable in node.variables.values():
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
        for column in columns:
            del data[column]
        data = data.replace({NaN:None})
        return data
    def pivotOutputData(self,include_tag=True) -> DataFrame:
        i = 0
        data = None
        for node in self.nodes:
            i = i+1
            node_data = node.pivotOutputData(include_tag=include_tag)
            data = node_data if i == 1 else pandas.concat([data,node_data],axis=1)
        # data = data.replace({np.NaN:None})
        return data
    def plotVariable(self,var_id,timestart:datetime=None,timeend:datetime=None,output=None) -> None:
        color_map = {"obs": "blue", "sim": "red","interpolated": "yellow","extrapolated": "orange","analysis": "green"}
        if output is not None:
            matplotlib.use('pdf')
            pdf = matplotlib.backends.backend_pdf.PdfPages(output)
        else:
            matplotlib.use(os.environ["MPLBACKEND"])
        for node in self.nodes:
            # if hasattr(node.series[0],"data"):
            if var_id in node.variables and node.variables[var_id].data is not None and len(node.variables[var_id].data):
                data = node.variables[var_id].data.reset_index().rename(columns={"index":"timestart"}) # .plot(y="valor")
                if timestart is not None:
                    data = data[data["timestart"] >= timestart]
                if timeend is not None:
                    data = data[data["timestart"] <= timeend]
                # data = node.series[0].data.reset_index() # .plot(y="valor")
                # data.plot(kind="scatter",x="timestart",y="valor",title=node.name, figsize=(20,8),grid=True)
                fig, ax = plt.subplots(figsize=(20,8))
                grouped = data.groupby('tag')
                for key, group in grouped:
                    group.plot(ax=ax,kind='scatter', x='timestart', y='valor', label=key,title=node.name, figsize=(20,8),grid=True, color=color_map[key])
                # data.plot.line(x="timestart",y="valor",ax=ax)
                original_data = node.variables[var_id].original_data.reset_index().rename(columns={"index":"timestart"})
                if len(original_data.dropna()["valor"]):
                    logging.debug("Add original data to plot at node %s" % str(node.name))
                    original_data.plot(ax=ax,kind='line', x='timestart', y='valor', label="analysis",title=node.name, figsize=(20,8),grid=True, color=color_map["analysis"])
                else:
                    logging.warn("Missing original data at node %s variable %i" % (node.name, var_id))
                if node.variables[var_id].series_sim is not None and len(node.variables[var_id].series_sim):
                    sim_colors = list(Color("orange").range_to(Color("red"),len(node.variables[var_id].series_sim)))
                    for i, serie_sim in enumerate(node.variables[var_id].series_sim):
                        if serie_sim.data is not None and len(serie_sim.data.dropna()["valor"]):
                            logging.debug("Add sim data to plot at node %s, series_sim %i" % (str(node.name),i))
                            data_sim = serie_sim.data.reset_index().rename(columns={"index":"timestart"})
                            label = "sim_%i" % serie_sim.series_id
                            data_sim.plot(ax=ax,kind='line', x='timestart', y='valor', label=label,title=node.name, figsize=(20,8),grid=True, color=sim_colors[i].get_hex())
                if hasattr(node,"max_obs_date"):
                    plt.axvline(node.max_obs_date, color='k', linestyle='--')
                if output is not None:
                    pdf.savefig()
                plt.close()
            else:
                logging.warn("topology.plotVariable: Skipping node %s" % str(node.id))
        if output is not None:
            pdf.close()
        else:
            plt.show()
    def plotProno(self,output_dir:str=None,figsize=None,title=None,markersize=None,obs_label=None,tz=None,prono_label=None,footnote=None,errorBandLabel=None,obsLine=None,prono_annotation=None,obs_annotation=None,forecast_date_annotation=None,ylim=None,datum_template_string=None,title_template_string=None,x_label=None,y_label=None,xlim=None,text_xoffset=None) -> None:
        output_dir = getParamOrDefaultTo("output_dir",output_dir,self.plot_params)
        footnote = getParamOrDefaultTo("footnote",footnote,self.plot_params)
        figsize = getParamOrDefaultTo("figsize",figsize,self.plot_params)
        markersize = getParamOrDefaultTo("markersize",markersize,self.plot_params)  
        prono_annotation = getParamOrDefaultTo("prono_annotation",prono_annotation,self.plot_params)  
        obsLine = getParamOrDefaultTo("obsLine",obsLine,self.plot_params)
        obs_annotation = getParamOrDefaultTo("obs_annotation",obs_annotation,self.plot_params)
        forecast_date_annotation = getParamOrDefaultTo("forecast_date_annotation",forecast_date_annotation,self.plot_params)
        output_dir = getParamOrDefaultTo("output_dir",output_dir,self.plot_params)
        ylim = getParamOrDefaultTo("ylim",ylim,self.plot_params)
        errorBandLabel = getParamOrDefaultTo("errorBandLabel",errorBandLabel,self.plot_params)
        obs_label = getParamOrDefaultTo("obs_label",obs_label,self.plot_params)
        tz = getParamOrDefaultTo("tz",tz,self.plot_params)
        prono_label = getParamOrDefaultTo("prono_label",prono_label,self.plot_params)
        title = getParamOrDefaultTo("title",title,self.plot_params)
        datum_template_string = getParamOrDefaultTo("datum_template_string",datum_template_string,self.plot_params)
        title_template_string = getParamOrDefaultTo("title_template_string",title_template_string,self.plot_params)
        x_label = getParamOrDefaultTo("x_label",x_label,self.plot_params)
        y_label = getParamOrDefaultTo("y_label",y_label,self.plot_params)
        xlim = getParamOrDefaultTo("xlim",xlim,self.plot_params)
        text_xoffset = getParamOrDefaultTo("text_xoffset",text_xoffset,self.plot_params)
        for node in self.nodes:
            node.plotProno(output_dir,figsize=figsize,title=title,markersize=markersize,obs_label=obs_label,tz=tz,prono_label=prono_label,footnote=footnote,errorBandLabel=errorBandLabel,obsLine=obsLine,prono_annotation=prono_annotation,obs_annotation=obs_annotation,forecast_date_annotation=forecast_date_annotation,ylim=ylim,datum_template_string=datum_template_string,title_template_string=title_template_string,x_label=x_label,y_label=y_label,xlim=xlim,text_xoffset=text_xoffset)
    def printReport(self) -> dict:
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
                            "series_id": serie.metadata.series_id,
                            "cal_id": serie.metadata.cal_id,
                            "forecast_date": serie.metadata.forecast_date.isoformat(),
                            "len": len(serie.data),
                            "outliers": [(x[0].isoformat(), x[1], x[2]) for x in list(serie.outliers_data.itertuples(name=None))] if serie.outliers_data is not None else None,
                            "jumps": [(x[0].isoformat(), x[1], x[2]) for x in list(serie.jumps_data.itertuples(name=None))] if serie.jumps_data is not None else None,
                            "nulls": int(serie.data["valor"].isna().sum()),
                            "tag_counts": serie.data.groupby("tag").size().to_dict(),
                            "min_date": serie_notnull.index[0].isoformat() if len(serie_notnull) else None,
                            "max_date": serie_notnull.index[-1].isoformat() if len(serie_notnull) else None,
                            "adjust_results": {
                                "quant_Err": serie.adjust_results["quant_Err"].to_dict(),
                                "r2": serie.adjust_results["r2"],
                                "coef": [x for x in serie.adjust_results["coef"]],
                                "intercept": serie.adjust_results["intercept"]
                            } if serie.adjust_results is not None else None
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
    def printGraph(self,nodes=None,output_file=None) -> None:
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
    def exportGraph(self,nodes=None,output_file=None) -> str:
        DG = self.toGraph(nodes)
        # NLD = nx.node_link_data(DG)
        if output_file is not None:
            with open(output_file,"w") as f:
                f.write(json.dumps(json_graph.node_link_data(DG),indent=4)) # json.dumps(NLD,indent=4))
                f.close()
        else:
            return json.dumps(json_graph.node_link_data(DG),indent=4)
