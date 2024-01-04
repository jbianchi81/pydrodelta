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
    # def toJSON(self):
    #     return json.dumps(self, default=lambda o: o.__dict__, 
    #         sort_keys=True, indent=4)
    def setStatistics(self,result_statistics:list|None=None):
        self.statistics = [ x if type(x) == ResultStatistics else ResultStatistics(x) for x in result_statistics] if result_statistics is not None else None
    def save(self,output):   
        if self.data is None:
            logging.warn("Procedure function produced no result to save. Skipping")
            return
        try:
            with open(output, 'w') as f:
                self.data.to_csv(f)
        except IOError as e:
            print(f"Couldn't write to file ({e})")

