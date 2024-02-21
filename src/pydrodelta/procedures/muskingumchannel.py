from pydrodelta.procedure_function import ProcedureFunction, ProcedureFunctionResults
from pydrodelta.validation import getSchemaAndValidate
from pydrodelta.pydrology import MuskingumChannel
from pandas import DataFrame
from pydrodelta.function_boundary import FunctionBoundary
from pydrodelta.model_parameter import ModelParameter
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
    def __init__(
        self,
        **kwargs):
        """
        Instancia la clase. Lee la configuración del dict params, opcionalmente la valida contra un esquema y los guarda los parámetros y estados iniciales como propiedades de self.
        Guarda procedure en self._procedure (procedimiento al cual pertenece la función)

        Parameters:
        -----------
        input : list of DataFrames
            Procedure function input (boundary conditions). If None, loads using .loadInput()

        Returns:
        --------
        2-tuple : first element is the procedure function output (list of DataFrames), while second is a ProcedureFunctionResults object
        """
        super().__init__(**kwargs)
        getSchemaAndValidate(kwargs,"MuskingumChannelProcedureFunction")
        self.K : float = self.parameters["K"]
        """Model parameter: transit time"""
        self.X : float = self.parameters["X"]
        """Model parameter: shape factor"""
        self.Proc : str = self.extra_pars["Proc"] if "Proc" in self.extra_pars else "Muskingum" # NOT USED
        self.initial_states : list = self.initial_states if self.initial_states is not None and len(self.initial_states) else [0] # None
        """Model initial states: initial discharge at the downstreams node"""
        self.engine : MuskingumChannel = None

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
        self.engine = MuskingumChannel([self.K, self.X], input[0]["valor"].to_list(),self.initial_states,self.Proc)
        self.engine.computeOutFlow()
        data = DataFrame({"valor": self.engine.Outflow},index=input[0].index)
        data_ = data[["valor"]].rename(columns={"valor":"output"}).join(input[0][["valor"]].rename(columns={"valor":"input"}))
        return (
            [data], 
            ProcedureFunctionResults(
                data = data_
            )
        )
    
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
        self.K = self.parameters["K"]
        self.X = self.parameters["X"]
    
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
        