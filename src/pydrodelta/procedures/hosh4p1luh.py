from pydrodelta.procedures.hosh4p1l import HOSH4P1LProcedureFunction
from pydrodelta.model_parameter import ModelParameter
from numpy import inf
from typing import Union

class HOSH4P1LUHProcedureFunction(HOSH4P1LProcedureFunction):
    """Modelo Operacional de Transformación de Precipitación en Escorrentía de 4 parámetros (estimables). Hidrología Operativa Síntesis de Hidrograma. Método NRCS, perfil de suelo con 2 reservorios de retención (sin efecto de base).
    
    Routing with triangular hydrograph"""
    _parameters = [
        ModelParameter(name="maxSurfaceStorage", constraints=(0.001,5,1200,inf)),
        ModelParameter(name="maxSoilStorage", constraints=(0.001,5,1200,inf)),
        ModelParameter(name="T", constraints=(0.2,0.5,8,25))
    ]
    """Model parameters: maxSurfaceStorage, maxSoilStorage, T base time of triangular hydrograph"""

    def setParameters(
        self, 
        parameters : Union[list,tuple] = []
        ) -> None:
        super().setParameters(parameters)
        self.maxSurfaceStorage = self.parameters["maxSurfaceStorage"]
        self.maxSoilStorage = self.parameters["maxSoilStorage"]
        self.T = self.parameters["T"]
