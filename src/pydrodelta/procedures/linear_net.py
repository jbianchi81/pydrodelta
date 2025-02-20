from ..procedure_function import ProcedureFunction, ProcedureFunctionResults
from ..function_boundary import FunctionBoundary
from ..pydrology import LinearNet
from ..descriptors.int_descriptor import IntDescriptor 
from ..model_parameter import ModelParameter
from ..procedure_boundary import ProcedureBoundary
from ..types.procedure_boundary_dict import ProcedureBoundaryDict
from ..types.enhanced_typed_list import EnhancedTypedList
import numpy as np
from typing import List

# schemas, resolver = getSchema("UHLinearChannelProcedureFunction","schemas/json")
# schema = schemas["UHLinearChannelProcedureFunction"]

class LinearNetProcedureFunction(ProcedureFunction):
    """
    LinearNet procedure function with any number of input nodes. See ..pydrology.LinearNet
    """
    
    _boundaries = [
        FunctionBoundary({"name": "input_1", "warmup_only": False}),
        FunctionBoundary({"name": "input_2", "warmup_only": False})
    ]
    """input nodes"""

    _additional_boundaries = [
        FunctionBoundary({"name": "input_3", "warmup_only": False}),
        FunctionBoundary({"name": "input_4", "warmup_only": False}),
        FunctionBoundary({"name": "input_5", "warmup_only": False}),
        FunctionBoundary({"name": "input_6", "warmup_only": False}),
        FunctionBoundary({"name": "input_7", "warmup_only": False}),
        FunctionBoundary({"name": "input_8", "warmup_only": False}),
        FunctionBoundary({"name": "input_9", "warmup_only": False}),
        FunctionBoundary({"name": "input_10", "warmup_only": False})
    ]
    """additional input nodes"""

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
       ModelParameter(name="n_3", constraints=(1,1,5,8)),
       ModelParameter(name="k_4", constraints=(0.2,0.5,8,25)),
       ModelParameter(name="n_4", constraints=(1,1,5,8)),
       ModelParameter(name="k_5", constraints=(0.2,0.5,8,25)),
       ModelParameter(name="n_5", constraints=(1,1,5,8)),
       ModelParameter(name="k_6", constraints=(0.2,0.5,8,25)),
       ModelParameter(name="n_6", constraints=(1,1,5,8)),
       ModelParameter(name="k_7", constraints=(0.2,0.5,8,25)),
       ModelParameter(name="n_7", constraints=(1,1,5,8)),
       ModelParameter(name="k_8", constraints=(0.2,0.5,8,25)),
       ModelParameter(name="n_8", constraints=(1,1,5,8)),
       ModelParameter(name="k_9", constraints=(0.2,0.5,8,25)),
       ModelParameter(name="n_9", constraints=(1,1,5,8)),
       ModelParameter(name="k_10", constraints=(0.2,0.5,8,25)),
       ModelParameter(name="n_10", constraints=(1,1,5,8))
    ]

    @property
    def coefficients(self):
        """Linear net coefficients (list of 2-tuples)"""
        result = [
            (self.parameters["k_1"], self.parameters["n_1"]),
            (self.parameters["k_2"], self.parameters["n_2"])
        ]
        for i in range(2,len(self.boundaries)):
            # if "k_%i" % i not in self.parameters:
            #     return result
            result.append(
                (self.parameters["k_%i" % i], self.parameters["n_%i" % i])
            )
        return result

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
        input_colnames = []
        for i in range(len(input)):
            data = input[i][["valor"]].rename(columns={"valor":"input"}) if data is None else data.join(input[i][["valor"]].rename(columns={"valor":"input"}))
            if not len(data.dropna().index):
                raise Exception("Procedure %s: Missing input data: no valid values found at boundary %i" % (self._procedure.id, i))
            last_date = max(data.dropna().index)
            if True in np.isnan(data[data.index <= last_date]["input"].values):
                raise Exception("NaN values found in input before last date %s" % last_date.isoformat())
            data = data.rename(columns={"input": "input_%i" % (i + 1)})
            input_colnames.append("input_%i" % (i + 1))
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