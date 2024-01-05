from pydrodelta.procedure_function import ProcedureFunction, ProcedureFunctionResults
from pydrodelta.validation import getSchema, validate
from pydrodelta.function_boundary import FunctionBoundary
from pydrodelta.pydrology import LinearChannel
import numpy as np

# schemas, resolver = getSchema("UHLinearChannelProcedureFunction","data/schemas/json")
# schema = schemas["UHLinearChannelProcedureFunction"]

class GenericLinearChannelProcedureFunction(ProcedureFunction):
    _boundaries = [
        FunctionBoundary({"name": "input", "warmup_only": True})
    ]
    _outputs = [
        FunctionBoundary({"name": "output"})
    ]
    def __init__(self,params,procedure):
        """
        Generic linear channel. Abstract class

        params:
        dt: calculation timestep
        """
        super().__init__(params,procedure)
        # validate(params,schema,resolver)
        self.dt = params["dt"] if "dt" in params else 1
        self.Proc = None
        self.coefficients = list()
    def run(self,input=None):
        """
        Ejecuta la función. Si input es None, ejecuta self._procedure.loadInput para generar el input. input debe ser una lista de objetos SeriesData
        Devuelve una lista de objetos SeriesData y opcionalmente un objeto ProcedureFunctionResults
        """
        if input is None:
            input = self._procedure.loadInput(inplace=False,pivot=False)
        data = input[0][["valor"]].rename(columns={"valor":"input"})
        last_date = max(data.dropna().index)
        linear_channel_input = data[data.index <= last_date]["input"].values
        if True in np.isnan(linear_channel_input):
            raise Exception("NaN values found in input before last date %s" % last_date.isoformat())
        linear_channel = LinearChannel(self.coefficients,linear_channel_input,self.Proc,self.dt)
        linear_channel.computeOutFlow()
        output = list(linear_channel.Outflow[:len(data)])
        while len(output) < len(data):
            output.append(np.NaN)
        data["output"] = output
        return (
            [data[["output"]].rename(columns={"output":"valor"})],
            ProcedureFunctionResults({
                "parameters": {
                    "coefficients": self.coefficients,
                    "dt": self.dt,
                },       
                "data": data
            })
        )