from ..procedure_function import ProcedureFunction, ProcedureFunctionResults
from ..function_boundary import FunctionBoundary
from ..pydrology import LinearNet
from ..descriptors.int_descriptor import IntDescriptor 
from ..model_parameter import ModelParameter
import numpy as np

# schemas, resolver = getSchema("UHLinearChannelProcedureFunction","schemas/json")
# schema = schemas["UHLinearChannelProcedureFunction"]

class LinearNet3ProcedureFunction(ProcedureFunction):
    """
    LinearNet procedure function with 3 input nodes. See ..pydrology.LinearNet
    """
    
    _boundaries = [
        FunctionBoundary({"name": "input_1", "warmup_only": True}),
        FunctionBoundary({"name": "input_2", "warmup_only": True}),
        FunctionBoundary({"name": "input_3", "warmup_only": True})
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
        parameters : dict,
        **kwargs):
        """
        /**kwargs : keyword arguments

        Keyword arguments:
        ------------------
        extra_pars : dict
            properties:
            dt : float 
                calculation timestep
        """
        super().__init__(parameters=parameters, **kwargs)
        self.dt = self.extra_pars["dt"] if "dt" in self.extra_pars else 1
 
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
        data = None
        linear_net_input = []
        for i in range(3):
            data = input[i][["valor"]].rename(columns={"valor":"input"}) if data is None else data.join(input[i][["valor"]].rename(columns={"valor":"input"}))
            if not len(data.dropna().index):
                raise Exception("Procedure %s: Missing input data: no valid values found at boundary %i" % (self._procedure.id, i))
            last_date = max(data.dropna().index)
            linear_net_input.append(data[data.index <= last_date]["input"].values)
            if True in np.isnan(linear_net_input[i]):
                raise Exception("NaN values found in input before last date %s" % last_date.isoformat())
            data = data.rename(columns={"input": "input_%i" % (i + 1)})
        self.engine = LinearNet(self.coefficients,linear_net_input,self.Proc,self.dt)
        self.engine.computeOutflow()
        output = list(self.engine.Outflow[:len(input[i])])
        while len(output) < len(input[i]):
            output.append(np.NaN)
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