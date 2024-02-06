from pydrodelta.procedure_function import ProcedureFunction, ProcedureFunctionResults
from pydrodelta.validation import getSchema, validate
from pydrodelta.function_boundary import FunctionBoundary
import numpy as np

schemas, resolver = getSchema("JunctionProcedureFunction","data/schemas/json")
schema = schemas["JunctionProcedureFunction"]

class JunctionProcedureFunction(ProcedureFunction):
    _boundaries = [
        FunctionBoundary({"name": "input_1"}),
        FunctionBoundary({"name": "input_2"})
    ]
    _additional_boundaries = True
    _outputs = [
        FunctionBoundary({"name": "output"})
    ]
    def __init__(self,params,procedure):
        """
        Adds input_1 with input_2 (and input_3, etc... if present) and saves into output_2
        """
        super().__init__(params,procedure)
        validate(params,schema,resolver)
        """Option to replace negative values with zero"""
        self.truncate_negative = bool(self.extra_pars["truncate_negative"]) if "truncate_negative" in self.extra_pars else False

    def run(self,input=None):
        return self.runJunction(input=input,substract=False)
    def runJunction(self,input=None,substract=False,truncate_negative=None):
        truncate_negative = truncate_negative if truncate_negative is not None else self.truncate_negative
        sign = -1 if substract else 1
        if input is None:
            input = self._procedure.loadInput(inplace=False,pivot=False)
        output = input[0][["valor"]].rename(columns={"valor": "valor_1"})
        output["valor"] = output["valor_1"]
        for i, serie in enumerate(input):
            if i == 0:
                continue
            colname = "input_%i" % (i + 1)
            output = output.join(serie[["valor"]].rename(columns={"valor":colname}))
            output["valor"] = output.apply(lambda row: row['valor'] + sign * row[colname] if not np.isnan(row['valor']) and not np.isnan(row[colname]) else None, axis=1)
            if truncate_negative:
                output["valor"] = output.apply(lambda row: max(0,row['valor']) if not np.isnan(row['valor']) else None, axis=1)
        # results_data = output.join(output_obs[["valor_1"]].rename(columns={"valor_1":"valor_obs"}),how="outer")
        output_obs = self._procedure.loadOutputObs(False)
        output = output.join(output_obs[0][["valor"]].rename(columns={"valor":"output_obs"}))
        return (
            [output[["valor"]]], 
            ProcedureFunctionResults({
                "border_conditions": input,
                "data": output.rename(columns={"valor":"output","valor_1":"input_1"})
            })
        )