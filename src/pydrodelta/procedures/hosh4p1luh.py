from pydrodelta.procedures.hosh4p1l import HOSH4P1LProcedure, HOSH4P1LParsDict, HOSHExtraParsDict, HOSHInitialStatesDict
from pydrodelta.model_parameter import ModelParameter
from numpy import inf
from typing import Union, TypedDict, Literal, List, Optional, Tuple, Mapping, Any
from typing_extensions import Unpack
from ..types.procedure_init_kwargs import ProcedureInitKwargs

class HOSH4P1LUHParsDict(TypedDict):
    maxSurfaceStorage : float
    """Maximum surface storage (model parameter)"""
    maxSoilStorage : float
    """Maximum soil storage (model parameter)"""
    T : float
    """Triangular hydrogram time to peak (model parameter)"""

class HOSH4P1LUHProcedure(HOSH4P1LProcedure):
    """Modelo Operacional de Transformación de Precipitación en Escorrentía de 4 parámetros (estimables). Hidrología Operativa Síntesis de Hidrograma. Método NRCS, perfil de suelo con 2 reservorios de retención (sin efecto de base).
    
    Routing with triangular hydrograph"""
    _parameters = [
        ModelParameter(name="maxSurfaceStorage", constraints=(0.001,5,1200,inf)),
        ModelParameter(name="maxSoilStorage", constraints=(0.001,5,1200,inf)),
        ModelParameter(name="T", constraints=(0.2,0.5,8,25))
    ]
    """Model parameters: maxSurfaceStorage, maxSoilStorage, T base time of triangular hydrograph"""

    @property
    def Proc(self) -> Literal['Nash', 'UH']:
        """Routing procedure (model parameter)"""
        return "UH"
    
    def __init__(
            self,
            parameters : Union[List[float], HOSH4P1LUHParsDict],
            initial_states: Union[List[float], HOSHInitialStatesDict],
            extra_pars: Optional[HOSHExtraParsDict],
            **kwargs : Unpack[ProcedureInitKwargs]
        ):
        if isinstance(parameters, dict):
            pars : HOSH4P1LParsDict = {
                **parameters,
                "Proc": "UH"
            }
            super().__init__(
                parameters = pars, 
                initial_states = initial_states, 
                extra_pars = extra_pars,
                **kwargs)
        else:
            super().__init__(
                parameters = parameters, 
                initial_states = initial_states, 
                extra_pars = extra_pars,
                **kwargs)

    def setParameters(
        self, 
        parameters : Union[List,Tuple,Mapping[str, Any]] = [],
        reset : bool=False,
        keys : Optional[List[str]]=None        ) -> None:        
        """Setter for parameters

        Arguments:
        ----------
        parameters (Union[list,tuple], optional)
        
            (maxSurfaceStorage : float, maxSoilStorage : float, T : float). Defaults to [].
        """
        super().setParameters(parameters)
        # self.maxSurfaceStorage = self.parameters["maxSurfaceStorage"]
        # self.maxSoilStorage = self.parameters["maxSoilStorage"]
        # self.T = self.parameters["T"]
