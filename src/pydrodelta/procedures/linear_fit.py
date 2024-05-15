from ..procedure_function import ProcedureFunction, ProcedureFunctionResults
from ..validation import getSchemaAndValidate
from ..function_boundary import FunctionBoundary
from ..util import adjustSeries
import math
from ..descriptors.int_descriptor import IntDescriptor
from ..descriptors.dict_descriptor import DictDescriptor
from ..descriptors.bool_descriptor import BoolDescriptor
from ..descriptors.string_descriptor import StringDescriptor
from typing import Tuple

class LinearFitProcedureFunction(ProcedureFunction):
    """Procedure function that fits a linear function between an independent variable (input) and a response and then applies the resulting function to the input values to produce the output"""

    _boundaries = [
        FunctionBoundary({"name": "input", "optional":True})
    ]
    """input: independent (explanatory) variable"""

    _additional_boundaries = True

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

    use_forecast_range = BoolDescriptor()
    """Fit using only pairs where sim is within forecasted range of values"""

    @property
    def sim_range(self) -> Tuple[float,float]:
        """Inmutable. Values range used for fit"""
        return self._sim_range

    type = StringDescriptor()

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

        if "use_forecast_range" in self.extra_pars:
            self.use_forecast_range = self.extra_pars["use_forecast_range"]
        else:
            self.use_forecast_range = False

        self._sim_range = None

        self.type = "linear"

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
        self._sim_range = self.getSimRange(input_data, 0.1) if self.use_forecast_range else None
        covariables = ["valor"]
        if len(input) > 1:
            for i in range(1,len(input)):
                b_name = "valor_%i" % i
                input_data = input_data.join(input[i][["valor"]].rename(columns={"valor":b_name}))
                covariables.append(b_name)
        if self.type == "exponential":
            if self.sim_range is not None:
                sim_range = (
                    math.log(self.sim_range[0]),
                    math.log(self.sim_range[1])
                )
            else:
                sim_range = self.sim_range
            input_data["valor"] = input_data["valor"].apply(lambda x: math.log(x))
        else:
            sim_range = self.sim_range
        response_data = output_obs[0].copy()
        try:
            (output_serie,output_tag_serie,stats) = adjustSeries(
                input_data,
                response_data,
                warmup=self.warmup_steps,
                tail=self.tail_steps,
                sim_range=sim_range,
                covariables=covariables
            )
        except ValueError as e:
            raise ValueError("Adjust series error at procedure %s: %s" % (self._procedure.id if self._procedure is not None else "unknown", str(e)))
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

    def getSimRange(self, data, expand : float = None) -> Tuple[float,float]:
        """Get values range of data in the forecasted period

        Args:
            data (DataFrame): Series DataFrame
            expand (float, optional): Expand the range by this fraction (of max - min). Defaults to None.

        Returns:
            Tuple[float,float]: (lower bound, upper bound)
        """
        sim_range = (
            data.loc[data.index >= self._procedure._plan.forecast_date]["valor"].min(),
            data.loc[data.index >= self._procedure._plan.forecast_date]["valor"].max()
        )
        if expand is not None:
            abs_range = sim_range[1] - sim_range[0]
            if abs_range > 0:
                return (
                    sim_range[0] - expand * abs_range,
                    sim_range[1] + expand * abs_range
                )
        return sim_range