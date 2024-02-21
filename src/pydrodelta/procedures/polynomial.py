# import pandas as pd
# from datetime import datetime, timedelta
# import numpy as np
# import matplotlib.pyplot as plt
# import os
from pydrodelta.procedure_function import ProcedureFunction, ProcedureFunctionResults
# from pathlib import Path
# import jsonschema
# import yaml
from pydrodelta.validation import getSchemaAndValidate
from pydrodelta.function_boundary import FunctionBoundary
from pydrodelta.a5 import createEmptyObsDataFrame

class PolynomialTransformationProcedureFunction(ProcedureFunction):
    _boundaries = [
        FunctionBoundary({"name": "input"})
    ]
    _outputs = [
        FunctionBoundary({"name": "output"})
    ]
    def __init__(
        self,
        **kwargs
        ):
        super().__init__(**kwargs)
        getSchemaAndValidate(kwargs,"PolynomialTransformationProcedureFunction")
        self.coefficients = self.parameters["coefficients"]
        self.intercept = self.parameters["intercept"] if "intercept" in self.parameters else 0
    def transformation_function(
        self,
        value : float
        ) -> float:
        """Return polynomial function result. self.intercept + self.coefficients[0] * value [ + self.coefficients[1] * value**2 + and so on ]
        
        Parameters:
        -----------
        value : float
            value of the independent variable
        
        Returns:
        --------
        float"""
        if value is None:
            return None
        result = self.intercept * 1
        exponent = 1
        for c in self.coefficients:
            result = result + value**exponent * c
            exponent = exponent + 1
        return result
    def run(
        self,
        input : list = None
        ) -> tuple:
        if input is None:
            input = self._procedure.loadInput(inplace=False,pivot=False)
        output  = []
        results_data = createEmptyObsDataFrame() # output_obs[["output"]].rename(columns={"output":"obs"})
        for i, serie in enumerate(input):
            output_serie = serie.copy()
            output_serie.valor = [self.transformation_function(valor) for valor in output_serie.valor]
            output.append(output_serie)
            colname = "input_%i" % (i + 1)
            results_data = results_data.join(serie.rename(columns={"valor": colname}))
            colname = "output_%i" % (i + 1)
            tagcolname = "tag_output_%i"  % (i + 1)
            results_data = results_data.join(output_serie.rename(columns={"valor": colname, "tag": tagcolname}))
        # data_for_stats = results_data[["obs","output_1"]].rename(columns={"output_1": "sim"}).dropna
        return (
            output, 
            ProcedureFunctionResults(
                data = results_data,
                parameters = {
                    "coefficients": self.coefficients,
                    "intercept": self.intercept
                }
            )
        )