from pydrodelta.result_statistics import ResultStatistics
from pandas import DataFrame
import numpy as np
import logging

class ProcedureFunctionResults:
    def __init__(self,params:dict={}):
        self.border_conditions = params["border_conditions"] if "border_conditions" in params else None
        self.initial_states = params["initial_states"] if "initial_states" in params else None
        self.states = params["states"] if "states" in params else None
        self.parameters = params["parameters"] if "parameters" in params else None
        self.statistics = [ResultStatistics(x) for x in params["statistics"]] if "statistics" in params and type(params["statistics"]) == list else [ResultStatistics(params["statistics"])] if "statistics" in params else None
        self.statistics_val = [ResultStatistics(x) for x in params["statistics_val"]] if "statistics_val" in params and type(params["statistics_val"]) == list else [ResultStatistics(params["statistics_val"])] if "statistics_val" in params else None
        self.data = DataFrame(params["data"]) if "data" in params else None
        self.extra_pars = params["extra_pars"] if "extra_pars" in params else None
    # def toJSON(self):
    #     return json.dumps(self, default=lambda o: o.__dict__, 
    #         sort_keys=True, indent=4)
    def setStatistics(self,result_statistics:list|None=None):
        self.statistics = [ x if type(x) == ResultStatistics else ResultStatistics(x) for x in result_statistics] if result_statistics is not None else None
    def setStatisticsVal(self,result_statistics:list|None=None):
        self.statistics_val = [ x if type(x) == ResultStatistics else ResultStatistics(x) for x in result_statistics] if result_statistics is not None else None
    def save(self,output):   
        if self.data is None:
            logging.warn("Procedure function produced no result to save. File %s not saved" % output)
            return
        try:
            with open(output, 'w') as f:
                self.data.to_csv(f)
            logging.info("Procedure function results saved into %s" % output)
        except IOError as e:
            logging.ERROR(f"Couldn't write to file ({e})")
    def toDict(self):
        # logging.debug({ 
        #     "border_conditions": str(type(self.border_conditions)),
        #     "initial_states": str(type(self.initial_states)),
        #     "states": str(type(self.states)),
        #     "parameters": str(type(self.parameters)),
        #     "extra_pars": str(type(self.extra_pars)),
        #     "statistics": str(type(self.statistics)),
        #     "data": str(type(self.data))
        # })
        return {
            "border_conditions": self.border_conditions.replace({np.nan:None}).to_dict("records") if self.border_conditions is not None and type(self.border_conditions) == DataFrame else [df.replace({np.nan:None}).to_dict("records") if type(df) == DataFrame else df for df in self.border_conditions] if self.border_conditions is not None and type(self.border_conditions) == list else self.border_conditions,
            "initial_states": self.initial_states,
            "states": self.states.replace({np.nan:None}).to_dict("records") if self.states is not None and type(self.states) == DataFrame else self.states,
            "parameters": self.parameters if type(self.parameters) == dict or type(self.parameters) == list else self.parameters.toDict() if self.parameters is not None else None,
            "extra_pars": self.extra_pars,
            "statistics": [x.toDict() for x in self.statistics] if self.statistics is not None else None,
            "statistics_val": [x.toDict() for x in self.statistics_val] if self.statistics_val is not None else None,
            "data": self.data.replace({np.nan:None}).to_dict("records") if self.data is not None and type(self.data) == DataFrame else [df.replace({np.nan:None}).to_dict("records") for df in self.data] if self.data is not None else None
        }

