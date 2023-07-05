from pydrodelta.procedure_boundary import ProcedureBoundary
from pydrodelta.procedure_function_results import ProcedureFunctionResults

class ProcedureFunction:
    """ static list of function boundaries (of class pydrodelta.function_boundary)
    """
    _boundaries = [] 
    """ static list of function outputs (of class pydrodelta.function_boundary)
    """
    _outputs = [] 
    """
    Abstract class to represent the transformation function of the procedure. It is instantiation, 'params' should be a dictionary which may contain an array of numerical or string 'parameters', an array of numerical or string 'initial_states', whereas 'procedure' must be the Procedure element which contains the function. The .run() method should accept an optional array of seriesData as 'input' and return an array of seriesData and a procedureFunctionResults object. When extending this class, any additional parameters may be added to 'params'.
    """
    def __init__(self,params,procedure):
        self._procedure = procedure
        self.parameters = params["parameters"] if "parameters" in params else []
        self.initial_states = params["initial_states"] if "initial_states" in params else []
        self.boundaries = []
        self.setBoundaries(params["boundaries"])
        self.outputs = []
        self.setOutputs(params["outputs"])
        self.input = None
    def setBoundaries(self,boundaries:dict={}):
        self.boundaries = []
        for b in self.__class__._boundaries:
            if b.name in boundaries:
                self.boundaries.append(ProcedureBoundary(boundaries[b.name],self._procedure._plan,b.optional))
            else:
                raise Exception("Missing NodeVariableIdTuple for boundary %i" % b.name)
    def setOutputs(self,outputs:dict={}):
        for b in self.__class__._outputs:
            if b.name in outputs:
                self.outputs.append(ProcedureBoundary(outputs[b.name],self._procedure._plan,b.optional))
            else:
                raise Exception("Missing nodeVariable for output %i" % b.name)
    def run(self,input=None):
        """
        Placeholder dummy method to be overwritten by actual procedures

        :param input: array of seriesData
        :returns [seriesData], procedureFunctionResults
        """
        if input is None:
            input = self._procedure.loadInput(inline=False)
        # data = self._plan.topology.pivotData(nodes=self.output_nodes,include_tag=False,use_output_series_id=False,use_node_id=True)
        return input, ProcedureFunctionResults({"init_states": input})
    