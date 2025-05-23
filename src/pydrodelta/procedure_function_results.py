from pydrodelta.result_statistics import ResultStatistics
from pydrodelta.config import config
from pandas import DataFrame
import numpy as np
import logging
from typing import Optional, Union, List
import os
import json

class ProcedureFunctionResults:
    """The results of a ProcedureFunction run"""
    def __init__(
        self,
        border_conditions : Union[List[DataFrame],DataFrame] = None,
        initial_states : Union[list,dict] = None,
        states : Union[list,DataFrame] = None,
        parameters : Union[list,dict] = None,
        statistics : Union[list,dict] = None,
        statistics_val : list = None,
        data : DataFrame = None,
        extra_pars : dict = None,
        adjust_results :dict = None
        ):
        """
        border_conditions : Union[List[DataFrame],DataFrame] = None

            Border conditions timeseries

        initial_states : Union[list,dict] = None

            Initial states

        states : Union[List[DataFrame],DataFrame] = None

            States timeseries

        parameters : Union[list,dict] = None

            Procedure function calibratable parameters

        statistics : Union[list,dict] = None

            Result statistics

        statistics_val : list = None

            Validation result statistics

        data : DataFrame = None

            Procedure function pivoted table. May include boundaries, states and/or outputs

        extra_pars : dict = None

            Additional, non-calibratable parameters

        adjust_results = None

            Results of adjustment (lfit or arima model properties)

        """
        self.border_conditions : Union[list,DataFrame,None] = border_conditions
        """Border conditions timeseries"""
        self.initial_states = initial_states
        """Initial states"""
        self.states = states
        """State timeseries"""
        self.parameters : Union[list,dict] = parameters
        """Procedure function calibratable  parameters"""
        self.statistics : Optional[list] = [ResultStatistics(**x) for x in statistics] if isinstance(statistics,(list,tuple)) else [ResultStatistics(**statistics)] if statistics is not None else None
        """Result statistics"""
        self.statistics_val : Optional[list] = [ResultStatistics(**x) for x in statistics_val] if isinstance(statistics_val,(list,tuple)) else [ResultStatistics(**statistics_val)] if statistics_val is not None else None
        """Validation results statistics"""
        self.data : Optional[DataFrame] = DataFrame(data) if data is not None else None
        """Procedure function pivoted table including boundaries, states and outputs"""
        self.extra_pars : Optional[dict] = extra_pars
        """Additional, non-calibratable parameters"""
        self.adjust_results = adjust_results
    # def toJSON(self):
    #     return json.dumps(self, default=lambda o: o.__dict__, 
    #         sort_keys=True, indent=4)
    def setStatistics(
        self,
        result_statistics : Optional[list] = None
        ) -> None:
        """Set .statistics from result_statistics"""
        self.statistics = [ ResultStatistics(**x) if type(x) == dict else x for x in result_statistics] if result_statistics is not None else None
    def setStatisticsVal(
        self,
        result_statistics : Optional[list] = None
        ) -> None:
        """Set .statistics_val from result_statistics"""
        self.statistics_val = [ ResultStatistics(**x) if type(x) == dict else x  for x in result_statistics] if result_statistics is not None else None
    def save(
        self,
        output : str
        ) -> None:
        """Save procedure function data as csv file
        
        Parameters:
        -----------
        output : str
                
            Path of csv file to write"""   
        if self.data is None:
            logging.warning("Procedure function produced no result to save. File %s not saved" % output)
            return
        try:
            with open(
                os.path.join(
                    config["PYDRODELTA_DIR"],
                    output
                ),
                'w') as f:
                self.data.to_csv(f)
            logging.info("Procedure function results saved into %s" % output)
        except IOError as e:
            logging.error(f"Couldn't write to file (%s)" % str(e))
    def saveDict(self, output : str):
        try:
            with open(
                os.path.join(
                    config["PYDRODELTA_DIR"],
                    output
                ),
                'w') as f:
                json.dump(self.toDict(), f)
            logging.info("Procedure function results saved into %s" % output)
        except IOError as e:
            # logging.ERROR(f"Couldn't write to file ({e})")
            raise e
    def toDict(self) -> dict:
        """Convert procedure function results to dict"""
        # logging.debug({
        #     "border_conditions": self.border_conditions.replace({np.nan:None}).to_dict("records") if self.border_conditions is not None and type(self.border_conditions) == DataFrame else [df.replace({np.nan:None}).to_dict("records") if type(df) == DataFrame else df for df in self.border_conditions] if self.border_conditions is not None and type(self.border_conditions) == list else self.border_conditions,
        #     "initial_states": self.initial_states,
        #     "states": self.states.replace({np.nan:None}).to_dict("records") if self.states is not None and type(self.states) == DataFrame else self.states,
        #     "parameters": self.parameters if type(self.parameters) == dict or type(self.parameters) == list else self.parameters.toDict() if self.parameters is not None else None,
        #     "extra_pars": self.extra_pars,
        #     "statistics": [x.toDict() for x in self.statistics] if self.statistics is not None else None,
        #     "statistics_val": [x.toDict() for x in self.statistics_val] if self.statistics_val is not None else None,
        #     "data": self.data.replace({np.nan:None}).to_dict("records") if self.data is not None and type(self.data) == DataFrame else [df.replace({np.nan:None}).to_dict("records") for df in self.data] if self.data is not None else None
        #     # .apply(lambda c: list(c) if isinstance(c[0], np.ndarray) else c)
        # })
        return {
            "border_conditions": self.border_conditions.replace({np.nan:None}).to_dict("records") if self.border_conditions is not None and type(self.border_conditions) == DataFrame else [df.replace({np.nan:None}).to_dict("records") if type(df) == DataFrame else df for df in self.border_conditions] if self.border_conditions is not None and type(self.border_conditions) == list else self.border_conditions,
            "initial_states": self.initial_states,
            "states": self.states.replace({np.nan:None}).to_dict("records") if self.states is not None and type(self.states) == DataFrame else self.states,
            "parameters": self.parameters if type(self.parameters) == dict or type(self.parameters) == list else self.parameters.toDict() if self.parameters is not None else None,
            "extra_pars": self.extra_pars,
            "statistics": [x.toDict() for x in self.statistics] if self.statistics is not None else None,
            "statistics_val": [x.toDict() for x in self.statistics_val] if self.statistics_val is not None else None,
            "data": self.data.replace({np.nan:None}).to_dict("records") if self.data is not None and type(self.data) == DataFrame else [df.replace({np.nan:None}).to_dict("records") for df in self.data] if self.data is not None else None,
            "adjust_results": self.adjust_results_dict
        }

    def setAdjustResults(self, adjust_results : dict):
        self.adjust_results = adjust_results

    @property
    def adjust_results_dict(self) -> dict:
        if self.adjust_results is not None:
            return {
                "method": self.adjust_results["method"] if "method" in self.adjust_results else None,
                "r2": self.adjust_results["r2"] if "r2" in self.adjust_results else None,
                "coef": self.adjust_results["coef"].tolist() if "coef" in self.adjust_results else None,
                "quant_Err": self.adjust_results["quant_Err"].to_list() if "quant_Err" in self.adjust_results else None,
                "intercept": self.adjust_results["intercept"] if "intercept" in self.adjust_results else None,
                "train": [ [ r[0].isoformat(), *r[1:]] for r in self.adjust_results["train"].reset_index().values] if "train" in self.adjust_results else None,
                "coefficients": self.adjust_results["coefficients"] if "coefficients" in self.adjust_results else None
            }
        else:
            return None

