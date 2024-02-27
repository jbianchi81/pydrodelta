from ..procedure_function import ProcedureFunction, ProcedureFunctionResults
from ..validation import getSchemaAndValidate
from ..pydrology import MuskingumChannel
from pandas import DataFrame
from ..function_boundary import FunctionBoundary
from ..model_parameter import ModelParameter
from numpy import inf
from typing import Union
import logging

class MuskingumChannelProcedureFunction(ProcedureFunction):
    """Método de tránsito hidrológico de la Oficina del río Muskingum. Parámetros: Tiempo de Tránsito (K) y Factor de forma (X). Condiciones de borde: Hidrograma en nodo superior de tramo."""

    _boundaries = [
        FunctionBoundary({"name": "input"})
    ]
    """input: discharge at upstream node"""
    
    _outputs = [
        FunctionBoundary({"name": "output"})
    ]
    """output: discharge at dowstream node"""
    
    _parameters = [
        #  id  | model_id | nombre | lim_inf | range_min | range_max | lim_sup  | orden 
        # -----+----------+--------+---------+-----------+-----------+----------+-------
        ModelParameter(name="K", constraints=(0,1,5,inf)),
        #  296 |       49 | K      |         |         1 |         5 | Infinity |     1
        ModelParameter(name="X", constraints=(0,0.1,0.5,inf))
        #  297 |       49 | x1c    |         |       0.1 |       0.5 | Infinity |     2
    ]
    """K: transit time. X: shape factor"""
    
    @property
    def K(self) -> float:
        """Model parameter: transit time"""
        return self.parameters["K"]
    
    @property
    def X(self) -> float:
        """Model parameter: shape factor"""
        return self.parameters["X"]

    @property
    def Proc(self) -> str:
        """Routing procedure"""
        return self.extra_pars["Proc"] if "Proc" in self.extra_pars else "Muskingum" # NOT USED
        
    @property
    def engine(self) -> MuskingumChannel:
        """Reference to the MuskingumChannel procedure engine"""
        return self._engine
    
    def __init__(
        self,
        parameters : dict,
        initial_states : Union[list,dict] = [0],
        **kwargs):
        """
        Arguments:
            parameters : dict

                Properties:

                - K : float - transit time
                
                - X : float - shape factor

            initial_states : list - Initial discharge at the output. Defaults to [0]
        
        Keyword arguments:
            See ..procedure_function.ProcedureFunction
        """
        super().__init__(**kwargs, parameters = parameters, initial_states = initial_states)
        getSchemaAndValidate(
            dict(
                kwargs, 
                parameters = parameters,
                initial_states = initial_states
            ),
            "MuskingumChannelProcedureFunction")
        self._engine = None

    def run(
        self,
        input : list = None
        ) -> tuple:
        """Runs the procedure
        
        input[0]: hidrograma en borde superior del tramo (DataFrame con index:timestamp y valor:float)
        
        Parameters:
        -----------
        input : list of DataFrames
            Procedure function input (boundary conditions). If None, loads using .loadInput()

        Returns:
        --------
        2-tuple : first element is the procedure function output (list of DataFrames), while second is a ProcedureFunctionResults object"""
        if input is None:
            input = self._procedure.loadInput(inplace=False,pivot=False)
        # logging.debug(input)
        # if self.initial_states is None:
        #     self.initial_states = [input[0].dropna().valor[0], input[1].dropna().valor[0]]
        self.setEngine(input[0])
        self._engine.computeOutFlow()
        data = DataFrame({"valor": self._engine.Outflow},index=input[0].index)
        data_ = data[["valor"]].rename(columns={"valor":"output"}).join(input[0][["valor"]].rename(columns={"valor":"input"}))
        return (
            [data], 
            ProcedureFunctionResults(
                data = data_
            )
        )
    
    def setEngine(
        self, 
        input : DataFrame
        ) -> None:
        """Initialize MuskingumChannel procedure engine using provided input. Takes column "valor" from  input as upstream boundary condition
        
        Args:
            input : DataFrame - The Procedure boundary"""
        self._engine = MuskingumChannel(
            [self.K, self.X], 
            input["valor"].to_list(),
            self.initial_states,
            self.Proc) 
    
    def setParameters(
        self, 
        parameters: Union[list,tuple] = ...
        ) -> None:
        """
        Setter for self.parameters.

        Parameters:
        -----------
        parameters : list or tuple

            Muskingum procedure function parameters to set (K : float, X : float)
        """
        super().setParameters(parameters)
    
    def setInitialStates(
        self,
        states : list = []
        ) -> None:
        """
        Setter for self.initial_states.

        Parameters:
        -----------
        states : list or tuple
            Muskingum procedure function parameters to set (initial_output_q : float)
        """
        self.initial_states = states
        