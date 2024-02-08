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

    def setParameters(
        self, 
        parameters : Union[list,tuple] = []
        ) -> None:
        super().setParameters(parameters)
        self.maxSurfaceStorage = self.parameters["maxSurfaceStorage"]
        self.maxSoilStorage = self.parameters["maxSoilStorage"]
        self.k = self.parameters["k"]
        self.n = self.parameters["n"]