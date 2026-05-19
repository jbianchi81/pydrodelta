from pydrodelta.procedures.hosh4p1l import HOSH4P1LProcedure, HOSH4P1LParsDict, HOSHExtraParsDict, HOSHInitialStatesDict
from pydrodelta.model_parameter import ModelParameter
from numpy import inf
from typing import Union, TypedDict, Literal, List, Optional, Tuple, Mapping, Any
from typing_extensions import Unpack
from ..types.procedure_init_kwargs import ProcedureInitKwargs

class HOSH4P1LNashParsDict(TypedDict):
    maxSurfaceStorage : float
    """Maximum surface storage (model parameter)"""
    maxSoilStorage : float
    """Maximum soil storage (model parameter)"""
    k : float
    """Nash linear channel coefficient k (model parameter)"""
    n : float
    """Nash linear channel number of reservoirs n (model parameter)"""

class HOSH4P1LNashProcedure(HOSH4P1LProcedure):
    """Modelo Operacional de Transformación de Precipitación en Escorrentía de 4 parámetros (estimables). Hidrología Operativa Síntesis de Hidrograma. Método NRCS, perfil de suelo con 2 reservorios de retención (sin efecto de base).
    
    Routing with Nash cascade"""
    _parameters = [
        ModelParameter(name="maxSurfaceStorage", constraints=(5,10,50,80)),
        ModelParameter(name="maxSoilStorage", constraints=(30,75,260,400)),
        ModelParameter(name="k", constraints=(0.2,0.5,8,25)),
        ModelParameter(name="n", constraints=(1,1,5,8))
    ]
    """Model parameters: maxSurfaceStorage, maxSoilStorage, k of Nash cascade, n  of Nash cascade"""

    @property
    def Proc(self) -> Literal['Nash', 'UH']:
        """Routing procedure (model parameter)"""
        return "Nash"

    def __init__(
            self,
            parameters : Union[List[float],HOSH4P1LNashParsDict],
            initial_states: Union[List[float], HOSHInitialStatesDict],
            extra_pars: Optional[HOSHExtraParsDict],
            **kwargs : Unpack[ProcedureInitKwargs]
        ):
        """
        parameters : 
        
            Model parameters. Ordered list or dict

            Properties:
            - maxSurfaceStorage
            - maxSoilStorage
            - k of Nash cascade
            - n of Nash cascade
        
        \\**kwargs : keyword arguments (see [..hosh4p1l.HOSH4P1L][])"""
        if isinstance(parameters, dict):
            pars : HOSH4P1LParsDict = {
                **parameters,
                "Proc": "Nash"
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
        keys : Optional[List[str]]=None
        ) -> None:
        """Parameters setter
        
        Parameters:
        -----------
        parameters : Union[List,Tuple,Mapping[str, Any]] = []
        
            (maxSurfaceStorage : float, maxSoilStorage : float, k : float, n : float)"""
        super().setParameters(parameters)
        # self.maxSurfaceStorage = self.parameters["maxSurfaceStorage"]
        # self.maxSoilStorage = self.parameters["maxSoilStorage"]
        # self.k = self.parameters["k"]
        # self.n = self.parameters["n"]