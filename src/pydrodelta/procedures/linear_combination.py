import pandas
# from datetime import datetime, timedelta
# import numpy as np
# import matplotlib.pyplot as plt
# import os
import logging
from pydrodelta.procedure_function import ProcedureFunction, ProcedureFunctionResults
# from pathlib import Path
# import jsonschema
# import yaml
from pydrodelta.validation import getSchemaAndValidate
from pydrodelta.function_boundary import FunctionBoundary

class BoundaryCoefficients():
    def __init__(self,params,procedure_function):
        self.name = params["name"] # str
        if len(params["values"]) < procedure_function.lookback_steps:
            raise Exception("Length of values list of boundary %i is shorter than procedure function lookback_steps (%i)" % (len(params["values"]), procedure_function.lookback_steps))
        if len(params["values"]) > procedure_function.lookback_steps:
            raise Exception("Length of values list of boundary %i is longer than procedure function lookback_steps (%i)" % (len(params["values"]), procedure_function.lookback_steps))
        self.values = params["values"] # list of numbers
    def toDict(self):
        return {
            "name": self.name,
            "values": self.values
        }

class ForecastStep():
    def __init__(self,params,procedure_function):
        self.intercept = params["intercept"]
        self.boundaries = list()
        for boundary in params["boundaries"]:
            if str(boundary["name"]) not in [b.name for b in procedure_function.boundaries]:
                raise Exception("Boundary %s not found in procedure.boundaries: " % (str(boundary["name"]), str([b.name for b in procedure_function.boundaries])))
            self.boundaries.append(BoundaryCoefficients(boundary,procedure_function))
    def toDict(self):
        return {
            "intercept": self.intercept,
            "boundaries": [ x.toDict() for x in self.boundaries ]
        }

class LinearCombinationProcedureFunction(ProcedureFunction):
    """Multivariable linear combination procedure function - one linear combination for each forecast horizon. Being x [, y, ...] the boundary series, for each forecast time step t it returns intercept[t] + [ x[-l] * coefficients[t]boundaries['x'][l] for l in 1..lookback_steps ] and so on for additional boundaries and lookback steps."""
    _boundaries = [
        FunctionBoundary({"name": "input_1", "warmup_only": True}),
        # FunctionBoundary({"name": "input_2", "optional": True})
    ]
    _additional_boundaries = True
    _outputs = [
        FunctionBoundary({"name": "output"})
    ]
    _additional_outputs = False
    def __init__(
        self,
        **kwargs
        ):
        super().__init__(**kwargs)
        getSchemaAndValidate(kwargs,"LinearCombinationProcedureFunction")
        self.forecast_steps = self.parameters["forecast_steps"]
        self.lookback_steps = self.parameters["lookback_steps"]
        self.coefficients = list()
        if len(self.parameters["coefficients"]) < self.forecast_steps:
            raise Exception("length of coefficients is shorter than forecast_steps")
        if len(self.parameters["coefficients"]) > self.forecast_steps:
            raise Exception("length of coefficients exceeds forecast_steps")
        for forecast_step in self.parameters["coefficients"]:
            self.coefficients.append(ForecastStep(forecast_step,self))
    # def transformation_function(self,value:float):
    #     if value is None:
    #         return None
    #     result = self.intercept * 1
    #     exponent = 1
    #     for c in self.coefficients:
    #         result = result + value**exponent * c
    #         exponent = exponent + 1
    #     return result
    def run(
        self,
        input : list = None
        ) -> tuple:
        if input is None:
            input = self._procedure.loadInput(inplace=False,pivot=False)
        output = []
        for t_index, forecast_step in enumerate(self.coefficients):
            forecast_date = self._procedure._plan.forecast_date + t_index * self._procedure._plan.time_interval
            result = 1 * forecast_step.intercept
            for b_index, boundary in enumerate(forecast_step.boundaries):
                for c_index, coefficient in enumerate(boundary.values):
                    lookback_date = self._procedure._plan.forecast_date - c_index * self._procedure._plan.time_interval
                    if lookback_date not in input[b_index].index:
                        raise Exception("Procedure %s: missing index at %s for %s" % (str(self._procedure.id),str(lookback_date), boundary.name))
                    if input[b_index].at[lookback_date,"valor"] is None:
                        raise Exception("Procedure %s: missing value at %s for %s" % (str(self._procedure.id),str(lookback_date), boundary.name))
                    result = result + coefficient * float(input[b_index].at[lookback_date,"valor"])
            output.append({
                "timestart": forecast_date,
                "valor": result 
            })
        output = pandas.DataFrame(output)
        output = output.set_index("timestart")
        results_data = output[["valor"]] # .join(output_obs.rename(columns={"valor_1": "obs"}),how="outer")
        for i, input_ in enumerate(input):
            colname = "input_%i" % (i + 1)
            results_data = results_data.join(input_[["valor"]].rename(columns={"valor": colname}),how="outer")
        return [output], ProcedureFunctionResults(
            data = results_data,
            parameters = {
                "forecast_steps": self.forecast_steps,
                "lookback_steps": self.lookback_steps,
                "coefficients": [x.toDict() for x in self.coefficients]
            }
        )