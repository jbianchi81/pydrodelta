from ..procedure_function import ProcedureFunction, ProcedureFunctionResults
from ..validation import getSchemaAndValidate
from ..function_boundary import FunctionBoundary
from ..util import adjustSeries
import math
from ..descriptors.int_descriptor import IntDescriptor
from ..descriptors.dict_descriptor import DictDescriptor

class ExponentialFitProcedureFunction(ProcedureFunction):
    """Procedure function that fits an exponential function between an independent variable (input) and a response and then applies the resulting function to the input values to produce the output"""

    _boundaries = [
        FunctionBoundary({"name": "input"})
    ]
    """input: independent (explanatory) variable"""

    _outputs = [
        FunctionBoundary({"name": "output"})
    ]
    """output: dependent variable (response)"""

    warmup_steps = IntDescriptor()
    """Skip this number of initial steps for fit procedure"""

    tail_steps = IntDescriptor()
    """Use only this number of final steps for fit procedure"""

    linear_model = DictDescriptor()
    """Results of the fit procedure"""

    def __init__(
        self,
        **kwargs):
        """
        
        \**kwargs : keyword arguments (see ProcedureFunction)
        """
        super().__init__(**kwargs)
        if "warmup_steps" in self.extra_pars:
            self.warmup_steps = self.extra_pars["warmup_steps"]
        else:
            self.warmup_steps = None
        if "tail_steps" in self.extra_pars:
            self.tail_steps = self.extra_pars["tail_steps"]
        else:
            self.tail_steps = None
        self.linear_model = None


    def run(
        self,
        input : list = None
        ) -> tuple:
        """
        Ejecuta la función. Si input es None, ejecuta self._procedure.loadInput para generar el input. input debe ser una lista de objetos SeriesData
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
            input = self._procedure.loadInput(inplace=False,pivot=False)
        output_obs = self._procedure.output_obs if self._procedure.output_obs is not None else self._procedure.loadOutputObs()
        input_data = input[0].copy()
        input_data["valor"] = input_data["valor"].apply(lambda x: math.log(x))
        response_data = output_obs[0].copy()
        (output_serie,output_tag_serie,stats) = adjustSeries(
            input_data,
            response_data,
            warmup=self.warmup_steps,
            tail=self.tail_steps
        )
        output_data = input_data.copy()
        output_data["valor"] = output_serie
        self.linear_model = stats
        output_data["inferior"] = output_serie - self.linear_model["quant_Err"][0.950]
        output_data["superior"] = output_serie + self.linear_model["quant_Err"][0.950]
        return (
            [output_data],
            ProcedureFunctionResults(
                border_conditions = input,
                data = input[0][["valor"]].rename(columns={"valor":"input"}).join(output_obs[0][["valor"]].rename(columns={"valor": "output_obs"})).join(output_data[["valor"]].rename(columns={"valor":"output"})),
                extra_pars = self.extra_pars
            )
        )