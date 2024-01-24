from pydrodelta.procedures.hosh4p1l import HOSH4P1LProcedureFunction
from pydrodelta.model_parameter import ModelParameter
from numpy import inf

class HOSH4P1LUHProcedureFunction(HOSH4P1LProcedureFunction):
    _parameters = [
        ModelParameter(name="maxSurfaceStorage", constraints=(0.001,5,1200,inf)),
        ModelParameter(name="maxSoilStorage", constraints=(0.001,5,1200,inf)),
        ModelParameter(name="T", constraints=(0.2,0.5,8,25))
    ]

    def setParameters(self, parameters: list | tuple = []):
        super().setParameters(parameters)
        self.maxSurfaceStorage = self.parameters["maxSurfaceStorage"]
        self.maxSoilStorage = self.parameters["maxSoilStorage"]
        self.T = self.parameters["T"]
