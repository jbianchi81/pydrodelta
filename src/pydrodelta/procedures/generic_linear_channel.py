from pydrodelta.procedure_function import ProcedureFunction, ProcedureFunctionResults
from pydrodelta.function_boundary import FunctionBoundary
from pydrodelta.pydrology import LinearChannel
import numpy as np

# schemas, resolver = getSchema("UHLinearChannelProcedureFunction","data/schemas/json")
# schema = schemas["UHLinearChannelProcedureFunction"]

class GenericLinearChannelProcedureFunction(ProcedureFunction):
    """Método de tránsito hidrológico implementado sobre la base de teoría de sistemas lineales. Así, considera al tránsito de energía, materia o información como un proceso lineal desde un nodo superior hacia un nodo inferior. Específicamente, sea I=[I1,I2,...,IN] el vector de pulsos generados por el borde superior y U=[U1,U2,..,UM] una función de distribución que representa el prorateo de un pulso unitario durante el tránsito desde un nodo superior (borde) hacia un nodo inferior (salida), el sistema opera aplicando las propiedades de proporcionalidad y aditividad, de manera tal que es posible propagar cada pulso a partir de U y luego mediante la suma de estos prorateos obtener el aporte de este tránsito sobre el nodo inferior (convolución)."""
    _boundaries = [
        FunctionBoundary({"name": "input", "warmup_only": True})
    ]
    """input node"""
    _outputs = [
        FunctionBoundary({"name": "output"})
    ]
    """output node"""

    @property
    def coefficients(self):
        """Linear channel coefficients"""
        return []

    @property
    def Proc(self):
        """Linear channel procedure"""
        return None

    def __init__(
        self,
        **kwargs):
        """
        Generic linear channel. Abstract class

        Parameters:
        -----------
        /**kwargs : keyword arguments

        Keyword arguments:
        ------------------
        extra_pars : dict
            properties:
            dt : float 
                calculation timestep
        """
        super().__init__(**kwargs)
        self.dt = self.extra_pars["dt"] if "dt" in self.extra_pars else 1
        """computation time step"""
        # self.Proc = None
        # self.coefficients = list()
    def run(
        self,
        input : list = None
        ) -> tuple:
        """
        Ejecuta la función. Si input es None, ejecuta self._procedure.loadInput para generar el input. input debe ser una lista de objetos SeriesData
        Devuelve una lista de objetos SeriesData y opcionalmente un objeto ProcedureFunctionResults

        Parameters:
        -----------
        input : list of DataFrames
            Procedure function input (boundary conditions). If None, loads using .loadInput()

        Returns:
        --------
        2-tuple : first element is the procedure function output (list of DataFrames), while second is a ProcedureFunctionResults object
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
                    "coefficients": list(self.coefficients),
                    "dt": self.dt,
                },       
                "data": data
            })
        )