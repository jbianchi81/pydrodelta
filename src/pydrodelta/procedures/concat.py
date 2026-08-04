from ..procedure_function_results import ProcedureFunctionResults
from ..procedure import Procedure
from ..function_boundary import FunctionBoundary
import numpy as np
from typing import List, Tuple, Optional, TypedDict, Any
from pandas import DataFrame
from ..types import ExecInput
from typing_extensions import Unpack, cast
from ..types.procedure_init_kwargs import ProcedureInitKwargs
from ..util import serieFillNulls, adjustSeries

class ConcatParsDict(TypedDict, total=False):
    fill_value : Optional[float]
    shift_by : Optional[int]
    bias : Optional[float]
    extend : Optional[bool]

class ConcatProcedure(Procedure):
    """Procedure that concatenates two or more inputs"""
    
    _boundaries = [
        FunctionBoundary({"name": "input_1", "optional": True}),
        FunctionBoundary({"name": "input_2", "optional": True})
    ]
    """input_1 and input_2 are concatenated. Additional boundaries (input_3, input_4, etc..) are allowed."""
    
    _additional_boundaries = True
    """Allow for additional boundaries"""
    
    _outputs = [
        FunctionBoundary({"name": "output"})
    ]
    """One output of the procedure"""
    
    @property
    def fill_value(self) -> Optional[float]:
        return self.extra_pars["fill_value"] if "fill_value" in self.extra_pars else None

    @property
    def shift_by(self) -> int:
        return self.extra_pars["shift_by"] if "shift_by" in self.extra_pars else 0

    @property
    def bias(self) -> float:
        return self.extra_pars["bias"] if "bias" in self.extra_pars else 0

    @property
    def extend(self) -> bool:
        return self.extra_pars["extend"] if "extend" in self.extra_pars else False



    def __init__(
        self,
        extra_pars : ConcatParsDict = {},
        **kwargs : Unpack[ProcedureInitKwargs]):
        """
        extra_pars :dict

            Properties:
            - adjust : bool = False

                Adjust linearly second(, third, etc) input to first

        \\**kwargs (see [..procedure_function.ProcedureFunction][])
        """        
        super().__init__(
            extra_pars = extra_pars, 
            **kwargs)

    def exec(
        self,
        input : ExecInput = None
        ) -> Tuple[List[DataFrame],ProcedureFunctionResults]:
        """Run the procedure
        
        Arguments:
        -----------
        input : list of DataFrames
            Procedure function input (boundary conditions). If None, loads using .loadInput()

        Returns:
        --------
        Tuple[List[DataFrame],ProcedureFunctionResults] : first element is the procedure function output (list of DataFrames), while second is a ProcedureFunctionResults object"""
        if isinstance(input, DataFrame):
            input = [input]
        return self.runConcat(input=input)
    
    def runConcat(
        self,
        input : Optional[List[DataFrame]] = None,
        adjust : Optional[bool] = None,
        fill_value : Optional[float]=None,
        shift_by : Optional[int]=None,
        bias : Optional[float]=None,
        extend : Optional[bool]=None
        ) -> Tuple[List[DataFrame],ProcedureFunctionResults]:
        """Run concat procedure

        Args:
            input (List[DataFrame], optional): Input series. Defaults to None.
            adjust (bool, optional): Adjust linearly second(, third, etc) input to first

        Returns:
            Tuple[List[DataFrame],ProcedureFunctionResults]: first element is the procedure function output (list of DataFrames), while second is a ProcedureFunctionResults object
        """
        adjust = adjust if adjust is not None else self.adjust
        fill_value = fill_value if fill_value is not None else self.fill_value
        shift_by = shift_by if shift_by is not None else self.shift_by
        bias = bias if bias is not None else self.bias
        extend = extend if extend is not None else self.extend
        if input is None:
            input = self.loadInput(inplace=False,pivot=False)
        output = input[0][["valor"]]
        for i, serie in enumerate(input):
            if i == 0:
                continue
            data = serie.copy()
            if adjust:
                (serie_, none, model) = adjustSeries(
                    data,
                    output,
                    warmup=self.warmup_steps,
                    tail=self.tail_steps,
                    drop_warmup=self.drop_warmup
                )
                data["valor"] = serie_
            output = serieFillNulls(
                output, 
                data[["valor"]], 
                fill_value=fill_value, 
                shift_by=shift_by, 
                bias=bias, 
                extend=extend)
        return (
            [output[["valor"]]], 
            ProcedureFunctionResults(
                border_conditions = input,
                data = output
            )
        )