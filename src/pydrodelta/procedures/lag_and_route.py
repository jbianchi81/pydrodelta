from pydrodelta.procedure_function import ProcedureFunctionResults
from pydrodelta.validation import getSchemaAndValidate
from pydrodelta.function_boundary import FunctionBoundary
from pydrodelta.pydrology import LagAndRoute
from pydrodelta.procedure_function import ProcedureFunction
from pydrodelta.model_parameter import ModelParameter
import numpy as np
from typing import Union, List

class LagAndRouteProcedureFunction(ProcedureFunction):
    """LagAndRoute"""

    _parameters = [
        ModelParameter(name="lag", constraints=(0,0,10,50)),
        ModelParameter(name="k", constraints=(0.2,0.5,8,25)),
        ModelParameter(name="n", constraints=(2,2,5,8))
    ]
    """Model parameters: lag, k, n"""

    _boundaries = [
        FunctionBoundary({"name": "input_1", "warmup_only": True}),
        FunctionBoundary({"name": "input_2", "optional": True})
    ]
    """input node"""

    _outputs = [
        FunctionBoundary({"name": "output"})
    ]
    """output node"""

    @property
    def engine(self) -> LagAndRoute:
        """Reference to instance of GR4J procedure engine"""
        return self._engine

    @property
    def pars_list(self) -> list:
        if "n" in self.parameters:
            return [
                self.parameters["lag"],
                self.parameters["k"],
                self.parameters["n"]
            ]
        else:
            return [
                self.parameters["lag"],
                self.parameters["k"]
            ]

    def __init__(
        self,
        parameters : Union[dict,list,tuple],
        **kwargs
        ):
        """
        Lag and Route

        Parameters:
        -----------
        parameters : dict

            properties:
            lag : int celerity in steps (0 = no lag)
            k : float residence time
            n : float number of reservoirs
        
        /**kwargs : keyword arguments

        Keyword arguments:
        ------------------
        extra_pars: dict
            properties
            dt : float calculation timestep
        """
        super().__init__(parameters = parameters, **kwargs)
        getSchemaAndValidate(dict(kwargs,parameters = parameters),"LagAndRouteProcedureFunction")
        self.dt = self.extra_pars["dt"] if "dt" in self.extra_pars else 1

    def setEngine(
        self,
        input : List[List[float]]
        ) -> None:
        """Instantiate GR4J procedure engine using input as Boundaries
        
        Args:
        input : List[float] - Boundary conditions: list of (pmad : float, etpd : float)"""
        self._engine = LagAndRoute(
            pars= self.pars_list,
            Boundaries=input,
            InitialConditions=self.initial_states,
            dt = self.dt)

    def run(
        self,
        input : list = None
        ) -> tuple:
        if input is None:
            input = self._procedure.loadInput(inplace=False)
        input_list = self.extractListsFromInput(input)
        self.setEngine(input_list)
        self.engine.executeRun()
        outflow = list(self.engine.Q[:len(input[0])])
        while len(outflow) < len(input[0]):
            outflow.append(np.nan)
        data = self.pivotInputOutput(input, [outflow])
        
        return (
            [data[["output"]].rename(columns={"output":"valor"})], 
            ProcedureFunctionResults(
                parameters = self.parameters,
                data = data
            )
        )
