import yaml
from pydrodelta.a5 import Crud, Serie
from pydrodelta.node_serie import NodeSerie
from pydrodelta.node_serie_prono import NodeSerieProno
import os
from pydrodelta.util import interval2timedelta, adjustSeries, linearCombination, adjustSeries, serieFillNulls, interpolateData, getParamOrDefaultTo, plot_prono
import pandas
import logging
import json
from datetime import timedelta
import matplotlib.pyplot as plt
import isodate

config_file = open("%s/config/config.yml" % os.environ["PYDRODELTA_DIR"]) # "src/pydrodelta/config/config.json")
config = yaml.load(config_file,yaml.CLoader)
config_file.close()

input_crud = Crud(config["input_api"])
output_crud = Crud(config["output_api"])


class NodeVariable:
    def __init__(self,params,node):
        if "id" not in params:
            raise ValueError("id of variable must be defined. Node id %i" % node.id)
        self.id = params["id"]
        self.metadata = input_crud.readVar(self.id)
        self.fill_value = params["fill_value"] if "fill_value" in params else None
        self.series_output = [NodeSerie(x) for x in params["series_output"]] if "series_output" in params else [NodeSerie({"series_id": params["output_series_id"]})] if "output_series_id" in params else None
        self.series_sim = None
        if "series_sim" in params:
            self.series_sim = []
            for serie in params["series_sim"]:
                serie["cal_id"] = serie["cal_id"] if "cal_id" in serie else node._plan.id if node is not None and node._plan is not None else None
                self.series_sim.append(NodeSerieProno(serie))
        self.time_support = interval2timedelta(params["time_support"]) if "time_support" in params else None 
        if self.time_support is None and self.metadata is not None:
            self.time_support = interval2timedelta(self.metadata["timeSupport"])
        self.adjust_from = params["adjust_from"] if "adjust_from" in params else None
        self.linear_combination = params["linear_combination"] if "linear_combination" in params else None
        self.interpolation_limit = params["interpolation_limit"] if "interpolation_limit" in params else None # in rows
        self.extrapolate = params["extrapolate"] if "extrapolate" in params else False
        if self.interpolation_limit is not None and self.interpolation_limit <= 0:
            raise("Invalid interpolation_limit: must be greater than 0")
        self.data = None
        self.original_data = None
        self.adjust_results = None
        self._node = node
        self.name = "%s_%s" % (self._node.name, self.id)
        self.time_interval = interval2timedelta(params["time_interval"]) if "time_interval" in params else self._node.time_interval
    def __repr__(self):
        series_str = ", ".join(["Series(type: %s, id: %i)" % (s.type, s.series_id) for s in self.series])
        return "Variable(id: %i, name: %s, count: %i, series: [%s])" % (self.id, self.metadata["nombre"] if self.metadata is not None else None, len(self.data) if self.data is not None else 0, series_str)
    def toDict(self):
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
    def toJSON(self):
        return json.dumps(self.toDict())
    def dataAsDict(self):
        if self.data is None:
            return None
        data = self.data.reset_index().to_dict("records") 
        for row in data:
            row["timestart"] = row["timestart"].isoformat()
        return data
    def originalDataAsDict(self):
        if self.original_data is None:
            return None
        data = self.original_data.reset_index().to_dict("records") 
        for row in data:
            row["timestart"] = row["timestart"].isoformat()
        return data
    def getData(self,include_series_id=False):
        data = self.data[["valor","tag"]] # self.concatenateProno(inline=False) if include_prono else self.data[["valor","tag"]] # self.series[0].data            
        if include_series_id:
            data["series_id"] = self.series_output.series_id if type(self.series_output) == NodeSerie else self.series_output[0].series_id if type(self.series_output) == list else None
        return data
    def toCSV(self,include_series_id=False,include_header=True):
        """
        returns self.data as csv
        """
        data = self.getData(include_series_id=include_series_id)
        return data.to_csv(header=include_header) # self.series[0].toCSV()
    def mergeOutputData(self):
        """
        merges data of all self.series_output into a single dataframe
        """
        data = None
        i = 0
        for serie in self.series_output:
            i = i + 1
            series_data = serie.data[["valor","tag"]]
            series_data["series_id"] = serie.series_id
            data = series_data if i == 1 else pandas.concat([data,series_data],axis=0)
        return data
    def outputToCSV(self,include_header=True):
        """
        returns data of self.series_output as csv
        """
        data = self.mergeOutputData()
        return data.to_csv(header=include_header) # self.series[0].toCSV()
    def toSerie(self,include_series_id=False,use_node_id=False):
        """
        return node as Serie object using self.data as observaciones
        """
        observaciones = self.toList(include_series_id=include_series_id,use_node_id=use_node_id)
        series_id = self.series_output[0].series_id if not use_node_id else self._node.id
        return Serie({
            "tipo": self._node.tipo,
            "id": series_id,
            "observaciones": observaciones
        })
    def toList(self,include_series_id=False,use_node_id=False): #,include_prono=False):
        """
        returns self.data as list of dict
        """
        data = self.data[self.data.valor.notnull()].copy()
        data.loc[:,"timestart"] = data.index
        data.loc[:,"timeend"] = [x + self.time_support for x in data["timestart"]] if self.time_support is not None else data["timestart"]
        data.loc[:,"timestart"] = [x.isoformat() for x in data["timestart"]]
        data.loc[:,"timeend"] = [x.isoformat() for x in data["timeend"]]
        if len(data) and include_series_id:
            data.loc[:,"series_id"] = self._node.id if use_node_id else self.series_output[0].series_id if self.series_output is not None else None
        return data.to_dict(orient="records")
    def outputToList(self,flatten=True):
        """
        returns series_output as list of dict
        if flatten == True, merges observations into single list. Else, returns list of series objects: [{series_id:int, observaciones:[{obs1},{obs2},...]},...]
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
    def pronoToList(self,flatten=True):
        """
        return series_prono as list of dict
        if flatten == True, merges observations into single list. Else, returns list of series objects: [{series_id:int, observaciones:[{obs1},{obs2},...]},...]"""
        if self.series_prono is None:
            return None
        list = []
        for serie in self.series_prono:
            if flatten:
                prono_list = serie.toList(include_series_id=True,timeSupport=self.time_support,remove_nulls=True)
                list.extend(prono_list)
            else:
                series_dict = serie.toDict(timeSupport=self.time_support, as_prono=True, remove_nulls=True)
                list.append(series_dict)
        return list
    def adjust(self,plot=True,error_band=True):
        truth_data = self.series[self.adjust_from["truth"]].data
        sim_data = self.series[self.adjust_from["sim"]].data
        self.series[self.adjust_from["sim"]].original_data = sim_data.copy(deep=True)
        try:
            adj_serie, tags, model = adjustSeries(sim_data,truth_data,method=self.adjust_from["method"],plot=plot,tag_column="tag",title=self.name)
        except ValueError:
            logging.warning("No observations found to estimate coefficients. Skipping adjust")
            return
        # self.series[self.adjust_from["sim"]].data["valor"] = adj_serie
        self.data.loc[:,"valor"] = adj_serie
        self.data.loc[:,"tag"] = tags
        self.adjust_results = model
        if error_band:
            self.data.loc[:,"error_band_01"] = adj_serie + self.adjust_results["quant_Err"][0.001]
            self.data.loc[:,"error_band_99"] = adj_serie + self.adjust_results["quant_Err"][0.999]     
    def apply_linear_combination(self,plot=True,series_index=0):
        self.series[series_index].original_data = self.series[series_index].data.copy(deep=True)
        #self.series[series_index].data.loc[:,"valor"] = util.linearCombination(self.pivotData(),self.linear_combination,plot=plot)
        self.data.loc[:,"valor"],  self.data.loc[:,"tag"] = linearCombination(self.pivotData(),self.linear_combination,plot=plot,tag_column="tag")
    def applyMovingAverage(self):
        for serie in self.series:
            if isinstance(serie,NodeSerie) and serie.moving_average is not None:
                serie.applyMovingAverage()
    def adjustProno(self,error_band=True):
        if not self.series_prono or not len(self.series_prono) or not len(self.series) or self.series[0].data is None:
            return
        truth_data = self.series[0].data
        for serie_prono in [x for x in self.series_prono if x.adjust]:
            sim_data = serie_prono.data[serie_prono.data["tag"]=="prono"]
            # serie_prono.original_data = sim_data.copy(deep=True)
            try:
                adj_serie, tags , model = adjustSeries(sim_data,truth_data,method="lfit",plot=True,tag_column="tag",title="%s @ %s" % (serie_prono.name, self.name))
            except ValueError:
                logging.warning("No observations found to estimate coefficients. Skipping adjust")
                return
            # self.series[self.adjust_from["sim"]].data["valor"] = adj_serie
            serie_prono.data.loc[:,"valor"] = adj_serie
            serie_prono.data.loc[:,"tag"] = tags
            serie_prono.adjust_results = model
            if error_band:
                serie_prono.data.loc[:,"error_band_01"] = adj_serie + serie_prono.adjust_results["quant_Err"][0.001]
                serie_prono.data.loc[:,"error_band_99"] = adj_serie + serie_prono.adjust_results["quant_Err"][0.999]     
    def setOutputData(self):
        if self.series_output is not None:
            for serie in self.series_output:
                serie.data = self.data[["valor","tag"]]
                serie.applyOffset()
    def uploadData(self,include_prono=False):
        """
        Uploads series_output to a5 API
        """
        if self.series_output is not None:
            if self.series_output[0].data is None:
                self.setOutputData()
            obs_created = []
            for serie in self.series_output:
                obs_list = serie.toList(remove_nulls=True,max_obs_date=None if include_prono else self.max_obs_date if hasattr(self,"max_obs_date") else None) # include_series_id=True)
                try:
                    created = output_crud.createObservaciones(obs_list,series_id=serie.series_id)
                    obs_created.extend(created)
                except Exception as e:
                    logging.error(str(e))
            return obs_created
        else:
            logging.warning("Missing output series for node #%i, variable %i, skipping upload" % (self._node.id,self.id))
            return []
    def pivotData(self,include_prono=True):
        data = self.series[0].data[["valor",]]
        for serie in self.series:
            if len(serie.data):
                data = data.join(serie.data[["valor",]],how='outer',rsuffix="_%s" % serie.series_id,sort=True)
        if include_prono and self.series_prono is not None and len(self.series_prono):
            for serie in self.series_prono:
                data = data.join(serie.data[["valor",]],how='outer',rsuffix="_prono_%s" % serie.series_id,sort=True)
        del data["valor"]
        return data
    def pivotOutputData(self,include_tag=True):
        columns = ["valor","tag"] if include_tag else ["valor"]
        data = self.series_output[0].data[columns]
        for serie in self.series_output:
            if len(serie.data):
                data = data.join(serie.data[columns],how='outer',rsuffix="_%s" % serie.series_id,sort=True)
        for column in columns:
            del data[column]
        return data
    def seriesToDataFrame(self,pivot=False,include_prono=True):
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
    def saveSeries(self,output,format="csv",pivot=False):
        data = self.seriesToDataFrame(pivot=pivot)
        if format=="csv":
            return data.to_csv(output)
        else:
            return json.dump(data.to_dict(orient="records"),output)
    def concatenate(self,data: pandas.DataFrame, inline=True):
        """
        Concatenates self.data with data

        :param data: DataFrame
        :param inline: Boolean, save result into self.data 
        : returns: nothing is inline=True, else DataFrame
        """
        if self.data is None:
            raise Exception("NodeVariable.data is not defined. Can´t concatenate")
        data["tag"] = "sim"
        concatenated_data = serieFillNulls(self.data,data,extend=True,tag_column="tag")
        if inline:
            self.data = concatenated_data
            return
        else:
            return concatenated_data

    def concatenateProno(self,inline=True,ignore_warmup=True):
        """
        Fills nulls of data with prono 
        
        :param ignore_warmup: if True, ignores prono before last observation
        :type ignore_warmup: bool
        :param inline: if True, saves into self.data, else returns concatenated dataframe
        :type inline: bool
        :returns: dataframe of concatenated data if inline=False, else None
        """
        if self.series_prono is not None and len(self.series_prono) and len(self.series_prono[0].data):
            prono_data = self.series_prono[0].data[["valor","tag"]]
            self.max_obs_date = self.data[~pandas.isna(self.data["valor"])].index.max()
            if ignore_warmup: #self.forecast_timeend is not None and ignore_warmup:
                prono_data = prono_data[prono_data.index > self.max_obs_date]
            data = serieFillNulls(self.data,prono_data,extend=True,tag_column="tag")
            if inline:
                self.data = data
            else:
                return data
        else:
            logging.warning("No series_prono data found for node %i" % self.id)
            if not inline:
                return self.data
    def interpolate(self,limit : timedelta=None,extrapolate=None):
        extrapolate = extrapolate if extrapolate is not None else self.extrapolate
        interpolation_limit = int(limit.total_seconds() / self.time_interval.total_seconds()) if isinstance(limit,timedelta) else int(limit) if limit is not None else self.interpolation_limit 
        logging.info("interpolation limit:%s" % str(interpolation_limit))
        logging.info("extrapolate:%s" % str(extrapolate))
        if interpolation_limit is not None and interpolation_limit <= 0:
            return
        self.data = interpolateData(self.data,column="valor",tag_column="tag",interpolation_limit=interpolation_limit,extrapolate=extrapolate)
    def saveData(self,output,format="csv"): #,include_prono=False):
        """
        Saves nodevariable.data into file
        """
        # data = self.concatenateProno(inline=False) if include_prono else self.data
        if format=="csv":
            return self.data.to_csv(output)
        else:
            return json.dump(self.data.to_dict(orient="records"),output)
    def plot(self):
        data = self.data[["valor",]]
        pivot_series = self.pivotData()
        data = data.join(pivot_series,how="outer")
        plt.figure(figsize=(16,8))
        if self._node.timeend is not None:
            plt.axvline(x=self._node.timeend, color="black",label="timeend")
        if self._node.forecast_timeend is not None:
            plt.axvline(x=self._node.forecast_timeend, color="red",label="forecast_timeend")
        plt.plot(data)
        plt.legend(data.columns)
        plt.title(self.name if self.name is not None else self.id)
    def plotProno(self,output_dir=None,figsize=None,title=None,markersize=None,obs_label=None,tz=None,prono_label=None,footnote=None,errorBandLabel=None,obsLine=None,prono_annotation=None,obs_annotation=None,forecast_date_annotation=None,ylim=None,station_name=None,ydisplay=None,text_xoffset=None,xytext=None,datum_template_string=None,title_template_string=None,x_label=None,y_label=None,xlim=None):
        if self.series_prono is None:
            logging.warn("Missing series_prono, skipping variable")
            return
        for serie_prono in self.series_prono:
            output_file = getParamOrDefaultTo("output_file",None,serie_prono.plot_params,"%s/%s_%s.png" % (output_dir, self.name, serie_prono.cal_id) if output_dir is not None else None)
            if output_file is None:
                logging.warn("Missing output_dir or output_file, skipping serie")
                continue
            station_name = getParamOrDefaultTo("station_name",station_name,serie_prono.plot_params,self.series[0].metadata["estacion"]["nombre"] if self.series[0].metadata is not None else None)
            thresholds = self.series[0].getThresholds() if self.series[0].metadata is not None else None
            datum = self.series[0].metadata["estacion"]["cero_ign"] if self.series[0].metadata is not None else None
            error_band = ("error_band_01","error_band_99") if serie_prono.adjust_results is not None else None
            ylim = getParamOrDefaultTo("ylim",ylim,serie_prono.plot_params)
            ydisplay = getParamOrDefaultTo("ydisplay",ydisplay,serie_prono.plot_params)
            text_xoffset = getParamOrDefaultTo("text_xoffset",text_xoffset,serie_prono.plot_params)
            xytext = getParamOrDefaultTo("xytext",xytext,serie_prono.plot_params)
            title = getParamOrDefaultTo("title",title,serie_prono.plot_params)
            obs_label = getParamOrDefaultTo("obs_label",obs_label,serie_prono.plot_params)
            tz = getParamOrDefaultTo("tz",tz,serie_prono.plot_params)
            prono_label = getParamOrDefaultTo("prono_label",prono_label,serie_prono.plot_params)
            errorBandLabel = getParamOrDefaultTo("errorBandLabel",errorBandLabel,serie_prono.plot_params)
            obsLine = getParamOrDefaultTo("obsLine",obsLine,serie_prono.plot_params)
            footnote = getParamOrDefaultTo("footnote",footnote,serie_prono.plot_params)
            xlim = getParamOrDefaultTo("xlim",xlim,serie_prono.plot_params)
            plot_prono(self.data,serie_prono.data,output_file=output_file,title=title,markersize=markersize,prono_label=prono_label,obs_label=obs_label,forecast_date=serie_prono.metadata.forecast_date,errorBand=error_band,errorBandLabel=errorBandLabel,obsLine=obsLine,prono_annotation=prono_annotation,obs_annotation=obs_annotation,forecast_date_annotation=forecast_date_annotation,station_name=station_name,thresholds=thresholds,datum=datum,footnote=footnote,figsize=figsize,ylim=ylim,ydisplay=ydisplay,text_xoffset=text_xoffset,xytext=xytext,tz=tz,datum_template_string=datum_template_string,title_template_string=title_template_string,x_label=x_label,y_label=y_label,xlim=xlim)
