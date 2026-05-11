from ..procedures.junction import JunctionProcedure
from ..function_boundary import FunctionBoundary
from typing import Optional, List, Union
from pandas import DataFrame

class DifferenceProcedure(JunctionProcedure):
    """Procedure function that substracts second boundary from the first"""

    _boundaries = [
        FunctionBoundary({"name": "input_1", "warmup_only": True}),
        FunctionBoundary({"name": "input_2", "warmup_only": True})
    ]
    """Second element (input_2) is substracted from the first element (input_1)"""
    def exec(
        self,
        input : Optional[Union[List[DataFrame], DataFrame]] = None
        ) -> tuple:
        """Run the procedure
        
        Parameters:
        -----------
        input : list of DataFrames
            Procedure function input (boundary conditions). If None, loads using .loadInput()

        Returns:
        --------
        2-tuple : first element is the procedure function output (list of DataFrames), while second is a ProcedureFunctionResults object"""
        if isinstance(input, DataFrame):
            input  = [input]
        return self.runJunction(input=input,substract=True,truncate_negative=True)
