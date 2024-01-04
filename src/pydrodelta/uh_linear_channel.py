from pydrodelta.procedure_function import ProcedureFunction, ProcedureFunctionResults
from pydrodelta.validation import getSchema, validate
from pydrodelta.function_boundary import FunctionBoundary
from pydrodelta.pydrology import LinearChannel
import numpy as np

schemas, resolver = getSchema("UHLinearChannelProcedureFunction","data/schemas/json")
schema = schemas["UHLinearChannelProcedureFunction"]

class UHLinearChannelProcedureFunction(ProcedureFunction):
    _boundaries = [
        FunctionBoundary({"name": "input", "warmup_only": True})
    ]
    _outputs = [
        FunctionBoundary({"name": "output"})
    ]
    def __init__(self,params,procedure):
        """
        Unit Hydrograph linear channel

        params:
        u: distribution function. list of floats 
        dt: calculation timestep
        """
        super().__init__(params,procedure)
        validate(params,schema,resolver)
        self.u = np.array(params["u"])
        self.dt = params["dt"] if "dt" in params else 1
        self.Proc = "UH"
    def run(self,input=None,output_obs=None):
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
        linear_channel = LinearChannel([self.k,self.n],linear_channel_input,self.Proc,self.dt)
        linear_channel.computeOutFlow()
        output = linear_channel.Outflow[:len(data)]
        while len(output) < len(data):
            output.append(np.NaN)
        data["output"] = output
        if output_obs is None:
            output_obs = self._procedure.loadOutputObs(inplace=False,pivot=True)
        return (
            [data[["output"]]],
            ProcedureFunctionResults({
                "border_conditions": input,
                "parameters": {
                    "k": self.k,
                    "n": self.n,
                    "dt": self.dt,
                },
                "statistics": {
                    "obs": output_obs["output"].values,
                    "sim": output,
                },       
                "data": data
            })
        )