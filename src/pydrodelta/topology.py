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

schema = open("%s/data/schemas/json/topology.json" % os.environ["PYDRODELTA_DIR"])
#schema = open("%s/data/schemas/yaml/topology.yml" % os.environ["PYDRODELTA_DIR"])
schema = yaml.load(schema,yaml.CLoader)
base_path = Path("%s/data/schemas/json" % os.environ["PYDRODELTA_DIR"])
resolver = jsonschema.validators.RefResolver(
    base_uri=f"{base_path.as_uri()}/",
    referrer=True,
)

config_file = open("%s/config/config.yml" % os.environ["PYDRODELTA_DIR"]) # "src/pydrodelta/config/config.json")
config = yaml.load(config_file,yaml.CLoader)
config_file.close()

input_crud = Crud(config["input_api"])
output_crud = Crud(config["output_api"])

class Topology():
    def __init__(self,params,plan=None):
        jsonschema.validate(
            instance=params,
            schema=schema,
            resolver=resolver)
        self.timestart = tryParseAndLocalizeDate(params["timestart"])
        self.timeend = tryParseAndLocalizeDate(params["timeend"])
        self.forecast_timeend = tryParseAndLocalizeDate(params["forecast_timeend"]) if "forecast_timeend" in params else None
        self.time_offset_start = interval2timedelta(params["time_offset_start"]) if "time_offset_start" in params else interval2timedelta(params["time_offset"]) if "time_offset" in params else timedelta(hours=0)
        self.time_offset_end = interval2timedelta(params["time_offset_end"]) if "time_offset_end" in params else interval2timedelta(params["time_offset"]) if "time_offset" in params else timedelta(hours=self.timeend.hour)
        self.timestart = self.timestart.replace(hour=0,minute=0,second=0,microsecond=0) + self.time_offset_start if type(params["timestart"]) == dict else self.timestart
        self.timeend = self.timeend.replace(hour=0,minute=0,second=0,microsecond=0) + self.time_offset_end if type(params["timeend"]) == dict else self.timeend
        if self.timestart >= self.timeend:
            raise("Bad timestart, timeend parameters. timestart must be before timeend")
        self.interpolation_limit = None if "interpolation_limit" not in params else interval2timedelta(params["interpolation_limit"]) if isinstance(params["interpolation_limit"],dict) else params["interpolation_limit"]
        self.nodes = []
        for node in params["nodes"]:
            self.nodes.append(Node(params=node,timestart=self.timestart,timeend=self.timeend,forecast_timeend=self.forecast_timeend,plan=plan,time_offset=self.time_offset_start,topology=self))
        self.cal_id = params["cal_id"] if "cal_id" in params else None
        self.plot_params = params["plot_params"] if "plot_params" in params else None
        self.report_file = params["report_file"] if "report_file" in params else None
        self._plan = plan
    def __repr__(self):
        nodes_str = ", ".join(["%i: Node(id: %i, name: %s)" % (self.nodes.index(n), n.id, n.name) for n in self.nodes])
        return "Topology(timestart: %s, timeend: %s, nodes: [%s])" % (self.timestart.isoformat(), self.timeend.isoformat(), nodes_str)
    def addNode(self,node,plan=None):
        self.nodes.append(Node(params=node,timestart=self.timestart,timeend=self.timeend,forecast_timeend=self.forecast_timeend,plan=plan,time_offset=self.time_offset_start,topology=self))
    def batchProcessInput(self,include_prono=False):
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
        self.interpolate(limit=self.interpolation_limit)
        self.setOutputData()
        self.plotProno()
        if(self.report_file is not None):
            report = self.printReport()
            f = open(self.report_file,"w")
            json.dump(report,f,indent=2)
            f.close()
    def loadData(self,include_prono=True):
        for node in self.nodes:
            # logging.debug("loadData timestart: %s, timeend: %s, time_interval: %s" % (self.timestart.isoformat(), self.timeend.isoformat(), str(node.time_interval)))
            timestart = self.timestart
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
    def removeOutliers(self):
        found_outliers = False
        for node in self.nodes:
            found_outliers_ = node.removeOutliers()
            found_outliers = found_outliers_ if found_outliers_ else found_outliers
        return found_outliers
    def detectJumps(self):
        found_jumps = False
        for node in self.nodes:
            found_jumps_ = node.detectJumps()
            found_jumps = found_jumps_ if found_jumps_ else found_jumps
        return found_jumps
    def applyMovingAverage(self):
        for node in self.nodes:
            node.applyMovingAverage()
    def applyOffset(self):
        for node in self.nodes:
            node.applyOffset()
    def regularize(self,interpolate=False):
        for node in self.nodes:
            node.regularize(interpolate=interpolate)
    def fillNulls(self):
        for node in self.nodes:
            node.fillNulls()
    def derive(self):
        for node in self.nodes:
            node.derive()
    def adjust(self):
        for node in self.nodes:
            node.adjust()
            node.apply_linear_combination()
            node.adjustProno()
    def concatenateProno(self):
        for node in self.nodes:
            for variable in node.variables.values():
                if variable.series_prono is not None:
                    variable.concatenateProno()
    def interpolate(self,limit=None):
        for node in self.nodes:
            node.interpolate(limit=limit)
    def setOutputData(self):
        for node in self.nodes:
            node.setOutputData()
    def toCSV(self,pivot=False):
        if pivot:
            data = self.pivotData()
            data["timestart"] = [x.isoformat() for x in data.index]
            # data.reset_index(inplace=True)
            return data.to_csv(index=False)    
        header = ",".join(["timestart","valor","tag","series_id"])
        return header + "\n" + "\n".join([node.toCSV(True,False) for node in self.nodes])
    def outputToCSV(self,pivot=False):
        if pivot:
            data = self.pivotOutputData()
            data["timestart"] = [x.isoformat() for x in data.index]
            # data.reset_index(inplace=True)
            return data.to_csv(index=False)    
        header = ",".join(["timestart","valor","tag","series_id"])
        return header + "\n" + "\n".join([node.outputToCSV(False) for node in self.nodes])
    def toSeries(self,use_node_id=False):
        """
        returns list of Series objects. Same as toList(flatten=True)
        """
        return self.toList(use_node_id=use_node_id,flatten=False)
    def toList(self,pivot=False,use_node_id=False,flatten=True):
        """
        returns list of all data in nodes[0..n].data
        
        pivot: boolean              pivot observations on index (timestart)
        use_node_id: boolean    uses node.id as series_id instead of node.output_series[0].id
        flatten: boolean        if set to false, returns list of series objects:[{"series_id":int,observaciones:[obs,obs,...]},...] (ignored if pivot=True)
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
    def outputToList(self,pivot=False,flatten=False):
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
    def saveData(self,file : str,format="csv",pivot=False):
        f = open(file,"w")
        if format == "json":
            obs_json = json.dumps(self.toList(pivot),ensure_ascii=False)
            f.write(obs_json)
            f.close()
            return
        f.write(self.toCSV(pivot))
        f.close
        return
    def saveOutputData(self,file : str,format="csv",pivot=False):
        f = open(file,"w")
        if format == "json":
            obs_json = json.dumps(self.outputToList(pivot),ensure_ascii=False)
            f.write(obs_json)
            f.close()
            return
        f.write(self.outputToCSV(pivot))
        f.close
        return
    def uploadData(self,include_prono):
        """
        Uploads analysis data of all nodes as a5 observaciones
        """
        created = []
        for node in self.nodes:
            obs_created = node.uploadData(include_prono=include_prono)
            if obs_created is not None and len(obs_created):
                created.extend(obs_created)
        return created
    def uploadDataAsProno(self,include_obs=True,include_prono=False):
        """
        Uploads analysis data of all nodes as a5 pronosticos
        """
        if self.cal_id is None:
            if self._plan is not None:
                 cal_id = self._plan.id
            else:
                raise Exception("Missing required parameter cal_id")
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

    def pivotData(self,include_tag=True,use_output_series_id=True,use_node_id=False,nodes=None):
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
    def pivotOutputData(self,include_tag=True):
        i = 0
        data = None
        for node in self.nodes:
            i = i+1
            node_data = node.pivotOutputData(include_tag=include_tag)
            data = node_data if i == 1 else pandas.concat([data,node_data],axis=1)
        # data = data.replace({np.NaN:None})
        return data
    def plotNodes(self,timestart:datetime=None,timeend:datetime=None):
        for node in self.nodes:
            # if hasattr(node.series[0],"data"):
            if node.data is not None and len(node.data):
                data = node.data.reset_index() # .plot(y="valor")
                if timestart is not None:
                    data = data[data["timestart"] >= timestart]
                if timeend is not None:
                    data = data[data["timestart"] <= timeend]
                # data = node.series[0].data.reset_index() # .plot(y="valor")
                ax = data.plot(kind="scatter",x="timestart",y="valor",title=node.name, figsize=(20,8),grid=True)
                # data.plot.line(x="timestart",y="valor",ax=ax)
                if hasattr(node,"max_obs_date"):
                    ax.axvline(node.max_obs_date, color='k', linestyle='--')
        plt.show()
    def plotProno(self,output_dir:str=None,figsize=None,title=None,markersize=None,obs_label=None,tz=None,prono_label=None,footnote=None,errorBandLabel=None,obsLine=None,prono_annotation=None,obs_annotation=None,forecast_date_annotation=None,ylim=None,datum_template_string=None,title_template_string=None,x_label=None,y_label=None,xlim=None,text_xoffset=None):
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
    def printReport(self):
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
    def printGraph(self,nodes=None,output_file=None):
        DG = self.toGraph(nodes)
        nx.draw_shell(DG, with_labels=True, font_weight='bold')
        if output_file is not None:
            plt.savefig(output_file, format='png')
            plt.close()
    def toGraph(self,nodes=None):
        if nodes is None:
            nodes = self.nodes
        DG = nx.DiGraph()
        for node in nodes:
            DG.add_node(node.id,object=node)
            if node.downstream_node is not None:
                if type(node.downstream_node) == "list":
                    for id in node.downstream_node:
                        DG.add_edge(node.id,id)
                else:
                    DG.add_edge(node.id,node.downstream_node)
        return DG
