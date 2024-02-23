from ..procedure_function import ProcedureFunction, ProcedureFunctionResults
from ..validation import getSchemaAndValidate
from ..function_boundary import FunctionBoundary
import numpy as np
from typing import List
from pandas import DataFrame

class JunctionProcedureFunction(ProcedureFunction):
    """Procedure function that represents the addition of two or more inputs"""
    
    _boundaries = [
        FunctionBoundary({"name": "input_1"}),
        FunctionBoundary({"name": "input_2"})
    ]
    """input_1 and input_2 are added together. Additional boundaries (input_3, input_4, etc..) are allowed."""
    
    _additional_boundaries = True
    """Allow for additional boundaries"""
    
    _outputs = [
        FunctionBoundary({"name": "output"})
    ]
    """One output of the procedure"""
    
    @property
    def truncate_negative(self) -> bool:
        """Replace negative output values to zero"""
        return bool(self.extra_pars["truncate_negative"]) if "truncate_negative" in self.extra_pars else False

    def __init__(
        self,
        extra_pars : dict = None,
        **kwargs):
        """
        extra_pars :dict

            Properties:
            - truncate_negative : bool = False

                Replace negative output values to zero

        \**kwargs (see [..procedure_function.ProcedureFunction][])
        """        
        super().__init__(extra_pars = extra_pars, **kwargs)
        getSchemaAndValidate(dict(kwargs,extra_pars = extra_pars),"JunctionProcedureFunction")

    def run(
        self,
        input : List[DataFrame] = None
        ) -> tuple[List[DataFrame],ProcedureFunctionResults]:
        """Run the procedure
        
        Arguments:
        -----------
        input : list of DataFrames
            Procedure function input (boundary conditions). If None, loads using .loadInput()

        Returns:
        --------
        tuple[List[DataFrame],ProcedureFunctionResults] : first element is the procedure function output (list of DataFrames), while second is a ProcedureFunctionResults object"""
        return self.runJunction(input=input,substract=False)
    def runJunction(
        self,
        input : list[DataFrame] = None,
        substract : bool = False,
        truncate_negative : bool = None
        ) -> tuple[List[DataFrame],ProcedureFunctionResults]:
        """Run junction procedure

        Args:
            input (list[DataFrame], optional): Input series. Defaults to None.
            substract (bool, optional): Instead of adding, substract second input series from first. Defaults to False.
            truncate_negative (bool, optional): Set negative results to zero. Defaults to None.

        Returns:
            tuple[List[DataFrame],ProcedureFunctionResults]: first element is the procedure function output (list of DataFrames), while second is a ProcedureFunctionResults object
        """
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
            ProcedureFunctionResults(
                border_conditions = input,
                data = output.rename(columns={"valor":"output","valor_1":"input_1"})
            )
        )