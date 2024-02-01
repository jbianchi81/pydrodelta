from pydrodelta.procedures.hosh4p1l import HOSH4P1LProcedureFunction
from pydrodelta.model_parameter import ModelParameter
from numpy import inf
from typing import Union

class HOSH4P1LNashProcedureFunction(HOSH4P1LProcedureFunction):
    _parameters = [
        ModelParameter(name="maxSurfaceStorage", constraints=(5,10,50,80)),
        ModelParameter(name="maxSoilStorage", constraints=(30,75,260,400)),
        ModelParameter(name="k", constraints=(0.2,0.5,8,25)),
        ModelParameter(name="n", constraints=(1,1,5,8))
    ]

    def setParameters(self, parameters: Union[list,tuple] = []):
        super().setParameters(parameters)
        self.maxSurfaceStorage = self.parameters["maxSurfaceStorage"]
        self.maxSoilStorage = self.parameters["maxSoilStorage"]
        self.k = self.parameters["k"]
        self.n = self.parameters["n"]