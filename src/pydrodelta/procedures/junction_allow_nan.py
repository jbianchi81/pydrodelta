from ..procedures.junction import JunctionProcedure
from ..function_boundary import FunctionBoundary
from typing import Optional, List, Union
from pandas import DataFrame

class JunctionAllowNaNProcedure(JunctionProcedure):
    """Procedure that represents the addition of two or more inputs. At missing values of either of the inputs, writes a null value in the output"""

    _boundaries = [
        FunctionBoundary({"name": "input_1", "optional": True}),
        FunctionBoundary({"name": "input_2", "optional": True})
    ]

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
        return self.runJunction(input=input)
