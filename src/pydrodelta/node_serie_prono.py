from .node_serie import NodeSerie
import logging
from .a5 import Crud, observacionesListToDataFrame, createEmptyObsDataFrame
from .node_serie_prono_metadata import NodeSeriePronoMetadata
from .config import config
from datetime import datetime
from .descriptors.string_descriptor import StringDescriptor
from .descriptors.datetime_descriptor import DatetimeDescriptor
from .descriptors.int_descriptor import IntDescriptor
from .descriptors.list_descriptor import ListDescriptor
from .util import coalesce

input_crud = Crud(**config["input_api"])
# output_crud = Crud(**config["output_api"])


class NodeSerieProno(NodeSerie):
    """Forecasted timeseries"""

    @property
    def metadata(self) -> dict:
        """series metadata"""
        return self._metadata.to_dict() if self._metadata is not None else None
    @metadata.setter
    def metadata(
        self,
        metadata : dict
    ) -> None:
        if metadata is not None:
            if "id" in metadata:
                metadata["series_id"] = metadata["id"]
                del metadata["id"]
            if "tipo" in metadata:
                metadata["series_table"] = self.getSeriesTable()
                del metadata["tipo"]
        self._metadata = NodeSeriePronoMetadata(**metadata) if metadata is not None else None
    
    main_qualifier = StringDescriptor()
    """If qualifier == 'all', select this qualifier as the main qualifier"""

    previous_runs_timestart = DatetimeDescriptor()
    """If set, retrieves previous forecast runs with forecast_date posterior to the chosen date and concatenates the results into a single series"""
    
    forecast_timestart = DatetimeDescriptor()
    """Begin date of last forecast run. If last forecast date is older than this value, it raises an error"""

    @property
    def adjust_results_string(self) -> str:
        return "r2: %.04f, y = %.05f + %.05f x" % (self.adjust_results["r2"], self.adjust_results["intercept"], self.adjust_results["coef"][0]) if self.adjust_results is not None else None
    
    warmup = IntDescriptor()

    tial = IntDescriptor()

    sim_range = ListDescriptor()

    def __init__(
        self,
        cal_id : int,
        qualifier : str = None,
        adjust : bool = False,
        plot_params : dict = None,
        upload : bool = True,
        cor_id : int = None,
        main_qualifier : str = None,
        previous_runs_timestart : datetime = None,
        forecast_timestart : datetime = None,
        warmup : int = None,
        tail : int = None,
        sim_range : int = None,
        **kwargs):
        super().__init__(**kwargs)        
        self.cal_id : int = cal_id
        """Identifier of simulation procedure configuration at the source (input api)"""
        self.qualifier :str = qualifier
        """Forecast qualifier at the source. Used to identify multiple timeseries of the same variable at the same node simulated by the same procedure. For example, the members of an ensemble simulation."""
        self.main_qualifier = main_qualifier
        self.adjust : bool = adjust
        """By means of a linear regression, adjust the forecasted timeseries to the observations (if available)"""
        self.cor_id : int = cor_id
        """Identifier of simulation procedure run"""
        self.forecast_date : datetime = None
        """Date of production of the simulation"""
        self.adjust_results : dict = None
        """Model resultant of the adjustment procedure"""
        self.name : str = "cal_id: %i, %s" % (self.cal_id if self.cal_id is not None else 0, self.qualifier if self.qualifier is not None else "main")
        """Name of the forecasted series"""
        self.plot_params : dict = plot_params
        """Plot configuration parameters"""
        self.metadata : dict = None
        """Forecasted series metadata"""
        self.upload : bool = bool(upload)
        """If True, include this series when uploading the analysis results to the output api"""
        self.previous_runs_timestart = previous_runs_timestart
        self.forecast_timestart = forecast_timestart
        self.warmup = warmup
        self.tail = tail
        self.sim_range = sim_range

    def loadData(
        self,
        timestart : datetime,
        timeend : datetime,
        input_api_config : dict = None,
        tag : str = "sim",
        previous_runs_timestart : datetime = None,
        forecast_timestart : datetime = None 
        ) -> None:
        """Load forecasted data from source (input api). Retrieves forecast from input api using series_id, cal_id, timestart, and timeend
        
        Parameters:
        -----------
        timestart : datetime
            Begin time of forecast
        
        timeend : datetime
            End time of forecast
        
        input_api_config : dict
            Api connection parameters. Overrides global config.input_api
            
            Properties:
            - url : str
            - token : str
            - proxy_dict : dict
        
        tag : str = "sim"
            Tag forecast records with this string
        
        previous_runs_timestart = DatetimeDescriptor()
            If set, retrieves previous forecast runs with forecast_date posterior to the chosen date and concatenates the results into a single series
        
        forecast_timestart : datetime = None
            Forecast date must be greater or equal to this value"""
        previous_runs_timestart = coalesce(previous_runs_timestart,self.previous_runs_timestart)
        forecast_timestart = coalesce(forecast_timestart, self.forecast_timestart)
        if self.observations is not None or self.csv_file is not None or self.json_file is not None:
            super().loadData(timestart, timeend, tag = "sim")
            # self.data = observacionesListToDataFrame(self.observations, tag = "sim")
            self.metadata["cal_id"] = self.cal_id
            return
        else:
            logging.debug("Load prono data for series_id: %i, cal_id: %i, cor_id: %s" % (self.series_id, self.cal_id, str(self.cor_id) if self.cor_id is not None else "last"))
            crud = Crud(**input_api_config) if input_api_config is not None else self._variable._node._crud if self._variable is not None and self._variable._node is not None else input_crud
            if previous_runs_timestart is not None:
                metadata = crud.readSeriePronoConcat(
                    self.cal_id,
                    self.series_id,
                    forecast_timestart = previous_runs_timestart,
                    qualifier = self.qualifier)
            else:
                metadata = crud.readSerieProno(
                    self.series_id,
                    self.cal_id,
                    timestart = timestart,
                    timeend = timeend,
                    qualifier = self.qualifier, 
                    cor_id = self.cor_id,
                    forecast_timestart = forecast_timestart)
            if len(metadata["pronosticos"]):
                if self.qualifier is not None and self.qualifier == 'all':
                    main_qualifier_index = 0
                    if self.main_qualifier is not None:
                        for i, m in enumerate(metadata["pronosticos"]):
                            if m["qualifier"] == self.main_qualifier:
                                main_qualifier_index = i
                    if not len(metadata["pronosticos"]) or "pronosticos" not in metadata["pronosticos"][main_qualifier_index] or not len(metadata["pronosticos"][main_qualifier_index]["pronosticos"]):
                        logging.warn("No forecast values found for series_id %i, cal_id %i, timestart %s, timeend %s, cor_id %s, main qualifier index %i" % (self.series_id, self.cal_id, timestart.isoformat(), timeend.isoformat(), self.cor_id, main_qualifier_index))
                        self.data = createEmptyObsDataFrame()
                    else:
                        self.data = observacionesListToDataFrame(metadata["pronosticos"][main_qualifier_index]["pronosticos"],tag="prono")
                        for member in metadata["pronosticos"]:
                            self.data = self.data.join(observacionesListToDataFrame(member["pronosticos"]).rename(columns={"valor": member["qualifier"]}))
                else:
                    self.data = observacionesListToDataFrame(metadata["pronosticos"],tag="prono")
            else:
                logging.warning("No data found for series_id=%i, cal_id=%i" % (self.series_id, self.cal_id))
                self.data = createEmptyObsDataFrame()
            del metadata["pronosticos"]
            self.metadata = metadata
        self.original_data = self.data.copy(deep=True)
    
    def setData(self,data):
        self.data = data

