from pydrodelta.node_serie import NodeSerie
import logging
from pydrodelta.a5 import Crud, observacionesListToDataFrame, createEmptyObsDataFrame
from pydrodelta.node_serie_prono_metadata import NodeSeriePronoMetadata
from pydrodelta.config import config

input_crud = Crud(config["input_api"])
output_crud = Crud(config["output_api"])


class NodeSerieProno(NodeSerie):
    def __init__(self,params):
        super().__init__(params)        
        self.cal_id = params["cal_id"]
        self.qualifier = params["qualifier"] if "qualifier" in params else None
        self.adjust = params["adjust"] if "adjust" in params else False
        self.cor_id = None
        self.forecast_date = None
        self.adjust_results = None
        self.name = "cal_id: %i, %s" % (self.cal_id if self.cal_id is not None else 0, self.qualifier if self.qualifier is not None else "main")
        self.plot_params = params["plot_params"] if "plot_params" in params else None
        self.metadata = None
        self.upload = bool(params["upload"]) if "upload" in params else True
    def loadData(self,timestart,timeend):
        logging.debug("Load prono data for series_id: %i, cal_id: %i" % (self.series_id, self.cal_id))
        self.metadata = input_crud.readSerieProno(self.series_id,self.cal_id,timestart,timeend,qualifier=self.qualifier)
        if len(self.metadata["pronosticos"]):
            self.data = observacionesListToDataFrame(self.metadata["pronosticos"],tag="prono")
        else:
            logging.warning("No data found for series_id=%i, cal_id=%i" % (self.series_id, self.cal_id))
            self.data = createEmptyObsDataFrame()
        self.original_data = self.data.copy(deep=True)
        del self.metadata["pronosticos"]
        self.metadata = NodeSeriePronoMetadata(self.metadata)
    def setData(self,data):
        self.data = data
