from pydrodelta.result_statistics import ResultStatistics
from pandas import DataFrame
import logging

class ProcedureFunctionResults:
    def __init__(self,params:dict={}):
        self.border_conditions = params["border_conditions"] if "border_conditions" in params else None
        self.initial_states = params["initial_states"] if "initial_states" in params else None
        self.states = params["states"] if "states" in params else None
        self.parameters = params["parameters"] if "parameters" in params else None
        self.statistics = [ResultStatistics(x) for x in params["statistics"]] if "statistics" in params and type(params["statistics"]) == list else [ResultStatistics(params["statistics"])] if "statistics" in params else None
        self.data = DataFrame(params["data"]) if "data" in params else None
        self.extra_pars = params["extra_pars"] if "extra_pars" in params else None
    # def toJSON(self):
    #     return json.dumps(self, default=lambda o: o.__dict__, 
    #         sort_keys=True, indent=4)
    def setStatistics(self,result_statistics:list|None=None):
        self.statistics = [ x if type(x) == ResultStatistics else ResultStatistics(x) for x in result_statistics] if result_statistics is not None else None
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
        return {
            "border_conditions": self.border_conditions.to_dict("records") if self.border_conditions is not None else None,
            "initial_states": self.initial_states,
            "states": self.states.to_dict("records") if self.states is not None else None,
            "parameters": self.parameters,
            "extra_pars": self.extra_pars,
            "statistics": [x.toDict() for x in self.statistics] if self.statistics is not None else None,
            "data": self.data.to_dict("records") if self.data is not None else None
        }

