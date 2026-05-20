from ..procedure_function_results import ProcedureFunctionResults
from ..procedure import Procedure
from ..function_boundary import FunctionBoundary
from a5client import createEmptyObsDataFrame
from typing import Union, List, Tuple, Any, Mapping, TypedDict, Optional
from typing_extensions import Unpack, NotRequired
from ..types.procedure_init_kwargs import ProcedureInitKwargs
from pandas import DataFrame
from ..types import ExecInput

class PolynomialParsDict(TypedDict):
    coefficients : List[float]
    """coefficients : list of float of length >= 1 - first is the linear coefficient, second is the quadratic"""
    intercept : NotRequired[float]

class PolynomialExtraParsDict(TypedDict, total=False):
    allow_na : bool
    """allow for null values in input. Defaults to False"""

class PolynomialTransformationProcedure(Procedure):
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
        if isinstance(self.parameters, list):
            return self.parameters[0]
        return self.parameters["coefficients"]
    
    @property
    def intercept(self) -> float:
        """intercept : float - default 0"""
        if isinstance(self.parameters, list):
            return self.parameters[1]
        return self.parameters["intercept"] if "intercept" in self.parameters else 0
    
    @property
    def allow_na(self) -> bool:
        """allow for null values in input. Defaults to False"""
        return self.extra_pars["allow_na"] if "allow_na" in self.extra_pars else False

    def __init__(
        self,
        parameters : Union[List[float], PolynomialParsDict],
        extra_pars : Optional[PolynomialExtraParsDict] = None,
        **kwargs : Unpack[ProcedureInitKwargs]
        ):
        """Polynomial procedure

        Arguments:
        ----------
        parameters (Union[List[float], PolynomialParsDict): Model parameters
            
            Properties:
            - coefficients : list of float of length >= 1 - first is the linear coefficient, second is the quadratic coefficient, and so on
            - intercept : float - default 0
        
        extra_pars: Optional[PolynomialExtraParsDict] = None

            Properties:
            - allow_na : bool - allow for null values in input. Defaults to False
        
        **kwargs : see ..procedure_function.Procedure
        """
        super().__init__(parameters = parameters, extra_pars = extra_pars, **kwargs)
        if self.allow_na:
            self.boundaries[0].optional = True
    
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
    def exec(
        self,
        input : ExecInput = None
        ) -> Tuple[List[DataFrame],ProcedureFunctionResults]:
        """Run the function procedure
        
        Parameters:
        -----------
        input : list of DataFrames
            Boundary conditions. If None, runs .loadInput

        Returns:
        Tuple[List[DataFrame],ProcedureFunctionResults] : first element is the procedure function output (list of DataFrames), while second is a ProcedureFunctionResults object"""
        if input is None:
            input = self.loadInput(inplace=False,pivot=False)
        elif isinstance(input, DataFrame):
            input = [input]
        output  = []
        results_data = createEmptyObsDataFrame() # output_obs[["output"]].rename(columns={"output":"obs"})
        for i, serie in enumerate(input):
            output_serie = serie.copy()
            output_serie["valor"] = [self.transformation_function(valor) for valor in output_serie.valor]
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