from ..procedure_function_results import ProcedureFunctionResults
from ..procedure import Procedure
from ..function_boundary import FunctionBoundary
from typing import Union, List, Optional
from pandas import DataFrame
import math
from ..types.procedure_full_init_kwargs import ProcedureFullInitKwargs
from typing_extensions import Unpack
import logging

class ExpressionProcedure(Procedure):
    """Procedure function that evaluates an arbitrary expression where 'value' is replaced with the values of input"""
    _boundaries = [
        FunctionBoundary({"name": "input"})
    ]
    """Only one input allowed"""
    _outputs = [
        FunctionBoundary({"name": "output"})
    ]
    """Only one output allowed"""

    @property
    def allow_na(self) -> bool:
        """allow for null values in input. Defaults to False"""
        return self.extra_pars["allow_na"] if "allow_na" in self.extra_pars else False

    def __init__(
        self,
        expression : str,
        **kwargs : Unpack[ProcedureFullInitKwargs]):
        """
        expression :str

            Expression to evaluate. For each step of input, 'value' is replaced with the value of input and the expression is evaluated
        
        \\**kwargs : keyword arguments (see ProcedureFunction)
        """
        super().__init__(expression=expression, **kwargs)
        # getSchemaAndValidate(
        #     dict(
        #         kwargs, 
        #         expression = expression),
        #     "ExpressionProcedureFunction")
        self.expression = expression
        if self.allow_na:
            self.boundaries[0].optional = True

    def transformation_function(
        self,
        value : float
        ) -> float:
        """Evaluates self.expression replacing 'value' with value
        
        Parameters:
        -----------
        value : float
            The value to use in the expression
            
        Returns:
        --------
        float"""
        if value is None:
            return None
        result = eval(self.expression)
        return result
    def exec(
        self,
        input : Optional[Union[List[DataFrame], DataFrame]] = None
        ) -> tuple:
        """
        Ejecuta la función. Si input es None, ejecuta self.loadInput para generar el input. input debe ser una lista de objetos SeriesData
        Devuelve una lista de objetos SeriesData y opcionalmente un objeto ProcedureFunctionResults
        
        Parameters:
        -----------
        input : list of DataFrames
            Procedure function input (boundary conditions). If None, loads using .loadInput()

        Returns:
        --------
        2-tuple : first element is the procedure function output (list of DataFrames), while second is a ProcedureFunctionResults object
        """
        if input is None:
            input = self.loadInput(inplace=False,pivot=False)
        output  = []
        if isinstance(input, DataFrame):
            input = [input]
        for in_df in input:
            out_df = in_df.copy()
            if hasattr(out_df, "map"):
                out_df[out_df.select_dtypes(include=["int8", "int16", "int32", "int64", "uint8", "uint16", "uint32", "uint64", "float16", "float32", "float64", "complex64", "complex128", "Int64"]).columns] = out_df.select_dtypes(include=["int8", "int16", "int32", "int64", "uint8", "uint16", "uint32", "uint64", "float16", "float32", "float64", "complex64", "complex128", "Int64"]).map(self.evaluate)
            else:
                out_df[out_df.select_dtypes(include=["int8", "int16", "int32", "int64", "uint8", "uint16", "uint32", "uint64", "float16", "float32", "float64", "complex64", "complex128", "Int64"]).columns] = out_df.select_dtypes(include=["int8", "int16", "int32", "int64", "uint8", "uint16", "uint32", "uint64", "float16", "float32", "float64", "complex64", "complex128", "Int64"]).applymap(self.evaluate)
            output.append(out_df)
        return (
            output, 
            ProcedureFunctionResults()
        )
    
    def evaluate(self, value : float) -> float:
        try:
            return eval(self.expression)
        except Exception as e:
            logging.error(f"Error evaluating expression for value={value}")
            logging.error(f"Expression: {self.expression}")
            raise ValueError(e)