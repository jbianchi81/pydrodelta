from pydrodelta.node_serie import NodeSerie
import logging
from pydrodelta.a5 import Crud, observacionesListToDataFrame, createEmptyObsDataFrame
from pydrodelta.node_serie_prono_metadata import NodeSeriePronoMetadata
from pydrodelta.config import config
from datetime import datetime

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
        self._metadata = NodeSeriePronoMetadata(**metadata) if metadata is not None else None
    
    def __init__(
        self,
        cal_id : int,
        qualifier : str = None,
        adjust : bool = False,
        plot_params : dict = None,
        upload : bool = True,
        cor_id : int = None,
        **kwargs):
        super().__init__(**kwargs)        
        self.cal_id : int = cal_id
        """Identifier of simulation procedure configuration at the source (input api)"""
        self.qualifier :str = qualifier
        """Forecast qualifier at the source. Used to identify multiple timeseries of the same variable at the same node simulated by the same procedure. For example, the members of an ensemble simulation."""
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
    def loadData(
        self,
        timestart : datetime,
        timeend : datetime,
        input_api_config : dict = None
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
            - proxy_dict : dict"""
        logging.debug("Load prono data for series_id: %i, cal_id: %i, cor_id: %s" % (self.series_id, self.cal_id, str(self.cor_id) if self.cor_id is not None else "last"))
        crud = Crud(**input_api_config) if input_api_config is not None else input_crud
        metadata = crud.readSerieProno(self.series_id,self.cal_id,timestart,timeend,qualifier=self.qualifier, cor_id = self.cor_id)
        if len(metadata["pronosticos"]):
            self.data = observacionesListToDataFrame(metadata["pronosticos"],tag="prono")
        else:
            logging.warning("No data found for series_id=%i, cal_id=%i" % (self.series_id, self.cal_id))
            self.data = createEmptyObsDataFrame()
        self.original_data = self.data.copy(deep=True)
        del metadata["pronosticos"]
        self.metadata = metadata
    def setData(self,data):
        self.data = data
