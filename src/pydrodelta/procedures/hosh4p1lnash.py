from pydrodelta.procedures.hosh4p1l import HOSH4P1LProcedureFunction
from pydrodelta.model_parameter import ModelParameter
from numpy import inf
from typing import Union

class HOSH4P1LNashProcedureFunction(HOSH4P1LProcedureFunction):
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
    def Proc(self) -> str:
        """Routing procedure (model parameter)"""
        return "Nash"

    def __init__(
            self,
            parameters : Union[list,tuple,dict],
            **kwargs
        ):
        """
        parameters : 
        
            Model parameters. Ordered list or dict

            Properties:
            - maxSurfaceStorage
            - maxSoilStorage
            - k of Nash cascade
            - n of Nash cascade
        
        \**kwargs : keyword arguments (see [..hosh4p1l.HOSH4P1L][])"""
        super().__init__(parameters = parameters, **kwargs)

    def setParameters(
        self, 
        parameters : Union[list,tuple] = []
        ) -> None:
        """Parameters setter
        
        Parameters:
        -----------
        parameters : Union[list,tuple] = []
        
            (maxSurfaceStorage : float, maxSoilStorage : float, k : float, n : float)"""
        super().setParameters(parameters)
        # self.maxSurfaceStorage = self.parameters["maxSurfaceStorage"]
        # self.maxSoilStorage = self.parameters["maxSoilStorage"]
        # self.k = self.parameters["k"]
        # self.n = self.parameters["n"]