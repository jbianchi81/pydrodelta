from ..procedure import Procedure
from ..procedure_function_results import ProcedureFunctionResults
from ..function_boundary import FunctionBoundary
from ..pydrology import LinearNet
from ..descriptors.int_descriptor import IntDescriptor 
from ..model_parameter import ModelParameter
import numpy as np
from ..types import ExecInput
from ..types.procedure_init_kwargs import ProcedureInitKwargs
from pandas import DataFrame
from typing_extensions import TypedDict, Unpack
from typing import Optional

class LinearNet3ParametersDict(TypedDict):
    k_1 : float
    n_1 : int
    k_2 : float
    n_2 : int
    k_3 : float
    n_3 : int

class ExtraParsDict(TypedDict, total=False):
    # calculation timestep
    dt: float

# schemas, resolver = getSchema("UHLinearChannelProcedureFunction","schemas/json")
# schema = schemas["UHLinearChannelProcedureFunction"]

class LinearNet3Procedure(Procedure):
    """
    LinearNet procedure function with 3 input nodes. See ..pydrology.LinearNet
    """
    
    _boundaries = [
        FunctionBoundary({"name": "input_1", "warmup_only": False}),
        FunctionBoundary({"name": "input_2", "warmup_only": False}),
        FunctionBoundary({"name": "input_3", "warmup_only": False})
    ]
    """input nodes"""

    _outputs = [
        FunctionBoundary({"name": "output"})
    ]
    """output node"""

    _parameters = [
       ModelParameter(name="k_1", constraints=(0.2,0.5,8,25)),
       ModelParameter(name="n_1", constraints=(1,1,5,8)),
       ModelParameter(name="k_2", constraints=(0.2,0.5,8,25)),
       ModelParameter(name="n_2", constraints=(1,1,5,8)),
       ModelParameter(name="k_3", constraints=(0.2,0.5,8,25)),
       ModelParameter(name="n_3", constraints=(1,1,5,8))
    ]

    @property
    def coefficients(self):
        """Linear net coefficients (list of 2-tuples)"""
        if isinstance(self.parameters, list):
            return [
                (self.parameters[0],self.parameters[1]),
                (self.parameters[2],self.parameters[3]),
                (self.parameters[4],self.parameters[5])
            ]
        return [
            (self.parameters["k_1"], self.parameters["n_1"]),
            (self.parameters["k_2"], self.parameters["n_2"]),
            (self.parameters["k_3"], self.parameters["n_3"])
        ]

    @property
    def Proc(self):
        """Fixed: Nash"""
        return "Nash"

    dt = IntDescriptor()
    """computation time step"""

    def __init__(
        self,
        parameters : LinearNet3ParametersDict,
        extra_pars : Optional[ExtraParsDict] = None,
        **kwargs : Unpack[ProcedureInitKwargs]):
        """
        parameters : LinearNet3ParametersDict
        /**kwargs : keyword arguments

        Keyword arguments:
        ------------------
        extra_pars : dict
            properties:
            dt : float 
                calculation timestep
        """
        super().__init__(parameters=parameters, extra_pars=extra_pars, **kwargs)
        self.dt = self.extra_pars["dt"] if "dt" in self.extra_pars else 1
 
    def exec(
        self,
        input : ExecInput = None
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
        if isinstance(input, DataFrame):
            input = [input]
        data = None
        input_colnames = []
        i = 0
        for i in range(3):
            data = input[i][["valor"]].rename(columns={"valor":"input"}) if data is None else data.join(input[i][["valor"]].rename(columns={"valor":"input"}))
            if not len(data.dropna().index):
                raise Exception("Procedure %s: Missing input data: no valid values found at boundary %i" % (self.id, i))
            last_date = max(data.dropna().index)
            if True in np.isnan(data[data.index <= last_date]["input"].values):
                raise Exception("NaN values found in input before last date %s" % last_date.isoformat())
            data = data.rename(columns={"input": "input_%i" % (i + 1)})
            input_colnames.append("input_%i" % (i + 1))
        if data is None:
            raise ValueError("Input has no length")
        input_data = data.dropna()
        linear_net_input = [ input_data[input_colname].values for input_colname in input_colnames ]

        self.engine = LinearNet(self.coefficients,linear_net_input,self.Proc,self.dt)
        self.engine.computeOutflow()
        output = list(self.engine.Outflow[:len(input[i])])
        while len(output) < len(input[i]):
            output.append(np.nan)
        data["output"] = output
        return (
            [data[["output"]].rename(columns={"output":"valor"})],
            ProcedureFunctionResults(
                parameters = {
                    "coefficients": list(self.coefficients),
                    "dt": self.dt,
                },       
                data = data
            )
        )