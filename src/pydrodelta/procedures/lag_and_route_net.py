from ..procedure_function import ProcedureFunction, ProcedureFunctionResults
from ..function_boundary import FunctionBoundary
from ..pydrology import LagAndRoute
from ..descriptors.int_descriptor import IntDescriptor 
from ..model_parameter import ModelParameter
from ..procedure_boundary import ProcedureBoundary
from ..types.procedure_boundary_dict import ProcedureBoundaryDict
from ..types.enhanced_typed_list import EnhancedTypedList
import numpy as np
from typing import List

# schemas, resolver = getSchema("UHLinearChannelProcedureFunction","schemas/json")
# schema = schemas["UHLinearChannelProcedureFunction"]

class LagAndRouteNetProcedureFunction(ProcedureFunction):
    """
    LagAndRouteNet procedure function with any number of input nodes. See ..pydrology.LagAndRoute
    """
    
    _boundaries = [
        FunctionBoundary({"name": "input_1", "warmup_only": False}),
    ]
    """input nodes"""

    _additional_boundaries = [
        FunctionBoundary({"name": "input_2", "warmup_only": False}),
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
       ModelParameter(name="lag_1", constraints=(0,0.5,8,25)),
       ModelParameter(name="k_1", constraints=(0.2,0.5,8,25)),
       ModelParameter(name="n_1", constraints=(1,1,5,8)),
       ModelParameter(name="lag_2", constraints=(0,0.5,8,25)),
       ModelParameter(name="k_2", constraints=(0.2,0.5,8,25)),
       ModelParameter(name="n_2", constraints=(1,1,5,8)),
       ModelParameter(name="lag_3", constraints=(0,0.5,8,25)),
       ModelParameter(name="k_3", constraints=(0.2,0.5,8,25)),
       ModelParameter(name="n_3", constraints=(1,1,5,8)),
       ModelParameter(name="lag_4", constraints=(0,0.5,8,25)),
       ModelParameter(name="k_4", constraints=(0.2,0.5,8,25)),
       ModelParameter(name="n_4", constraints=(1,1,5,8)),
       ModelParameter(name="lag_5", constraints=(0,0.5,8,25)),
       ModelParameter(name="k_5", constraints=(0.2,0.5,8,25)),
       ModelParameter(name="n_5", constraints=(1,1,5,8)),
       ModelParameter(name="lag_6", constraints=(0,0.5,8,25)),
       ModelParameter(name="k_6", constraints=(0.2,0.5,8,25)),
       ModelParameter(name="n_6", constraints=(1,1,5,8)),
       ModelParameter(name="lag_7", constraints=(0,0.5,8,25)),
       ModelParameter(name="k_7", constraints=(0.2,0.5,8,25)),
       ModelParameter(name="n_7", constraints=(1,1,5,8)),
       ModelParameter(name="lag_8", constraints=(0,0.5,8,25)),
       ModelParameter(name="k_8", constraints=(0.2,0.5,8,25)),
       ModelParameter(name="n_8", constraints=(1,1,5,8)),
       ModelParameter(name="lag_9", constraints=(0,0.5,8,25)),
       ModelParameter(name="k_9", constraints=(0.2,0.5,8,25)),
       ModelParameter(name="n_9", constraints=(1,1,5,8)),
       ModelParameter(name="lag_10", constraints=(0,0.5,8,25)),
       ModelParameter(name="k_10", constraints=(0.2,0.5,8,25)),
       ModelParameter(name="n_10", constraints=(1,1,5,8))
    ]

    @property
    def coefficients(self):
        """Lag and route net coefficients (list of 3-tuples)"""
        result = [
            (self.parameters["lag_1"],self.parameters["k_1"], self.parameters["n_1"]),
            (self.parameters["lag_2"],self.parameters["k_2"], self.parameters["n_2"]),
        ]
        for i in range(2,len(self.boundaries)):
            # if "k_%i" % i not in self.parameters:
            #     return result
            result.append(
                (self.parameters["lag_%i" % i],self.parameters["k_%i" % i], self.parameters["n_%i" % i])
            )
        return result

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

    @property
    def pars_list(self) -> list:
        pars_list = []
        for i, boundary in enumerate(self.boundaries):
            lag_key = "lag_%i" % (i + 1)
            if lag_key not in self.parameters:
                raise ValueError("Missing parameter %s" % lag_key)
            k_key = "k_%i" % (i + 1)
            if k_key not in self.parameters:
                raise ValueError("Missing parameter %s" % k_key)
            n_key = "n_%i" % (i + 1)
            if n_key not in self.parameters:
                raise ValueError("Missing parameter %s" % n_key)
            pars_list.append(
                [
                    self.parameters[lag_key],
                    self.parameters[k_key],
                    self.parameters[n_key]
                ]
            )
        return pars_list

    @property
    def engine(self) -> LagAndRoute:
        """Reference to instance of GR4J procedure engine"""
        return self._engine

    def setEngine(
        self,
        input : List[List[float]]
        ) -> None:
        """Instantiate procedure engine using input as Boundaries. Each boundary starts one engine as inflow (no leakages)
        
        Args:
        input : List[float] - Boundary conditions: list of (pmad : float, etpd : float)"""
        self._engine = [
                LagAndRoute(
                pars= self.pars_list[i],
                Boundaries=[boundary],
                InitialConditions=self.initial_states[i] if self.initial_states is not None and len(self.initial_states) - 1 >= i else [0],
                dt = self.dt)
            for i, boundary in enumerate(input)]

    def run(
        self,
        input : list = None
        ) -> tuple:
        if input is None:
            input = self._procedure.loadInput(inplace=False)
        input_list = self.extractListsFromInput(input, allow_na=[False,True])
        self.setEngine(input_list)
        outflows = []
        for i, engine in enumerate(self.engine):
            engine.executeRun()
            outflow = list(engine.Q[:len(input[0])])
            while len(outflow) < len(input[0]):
                outflow.append(np.nan)
            outflows.append(outflow)
        outflow_sum = [sum(x) for x in zip(*outflows)]
        dict_outflows = {
                "outflow_%i" % (i + 1): outflow
            for i, outflow in enumerate(outflows) 
        }
        data = self.pivotInputOutput(input, [outflow_sum], other=dict_outflows)
        
        return (
            [data[["output"]].rename(columns={"output":"valor"})], 
            ProcedureFunctionResults(
                parameters = self.parameters,
                data = data
            )
        )
