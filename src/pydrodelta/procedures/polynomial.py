from ..procedure_function import ProcedureFunction, ProcedureFunctionResults
from ..validation import getSchemaAndValidate
from ..function_boundary import FunctionBoundary
from ..a5 import createEmptyObsDataFrame
from typing import Union, List, Tuple
from pandas import DataFrame

class PolynomialTransformationProcedureFunction(ProcedureFunction):
    """Polynomial transformation procedure"""

    _boundaries = [
        FunctionBoundary({"name": "input"})
    ]

    _outputs = [
        FunctionBoundary({"name": "output"})
    ]
    
    @property
    def coefficients(self) -> List[float]:
        """coefficients : list of float of length >= 1 - first is the linear coefficient, second is the quadratic"""
        return self.parameters["coefficients"]
    
    @property
    def intercept(self) -> float:
        """intercept : float - default 0"""
        return self.parameters["intercept"] if "intercept" in self.parameters else 0

    def __init__(
        self,
        parameters : Union[dict,list,tuple],
        **kwargs
        ):
        """_summary_

        Arguments:
        ----------
        parameters (Union[dict,list,tuple]): Model parameters
            
            Properties:
            - coefficients : list of float of length >= 1 - first is the linear coefficient, second is the quadratic coefficient, and so on
            - intercept : float - default 0
        
        \**kwargs : see ..procedure_function.ProcedureFunction
        """
        super().__init__(parameters = parameters, **kwargs)
        getSchemaAndValidate(dict(kwargs, parameters = parameters),"PolynomialTransformationProcedureFunction")
    
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
        input : List[DataFrame] = None
        ) -> Tuple[List[DataFrame],ProcedureFunctionResults]:
        """Run the function procedure
        
        Parameters:
        -----------
        input : list of DataFrames
            Boundary conditions. If None, runs .loadInput

        Returns:
        Tuple[List[DataFrame],ProcedureFunctionResults] : first element is the procedure function output (list of DataFrames), while second is a ProcedureFunctionResults object"""
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