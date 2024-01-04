from pydrodelta.procedure_boundary import ProcedureBoundary
from pydrodelta.procedure_function_results import ProcedureFunctionResults

class ProcedureFunction:
    """
    Abstract class to represent the transformation function of the procedure. It is instantiation, 'params' should be a dictionary which may contain an array of numerical or string 'parameters', an array of numerical or string 'initial_states', whereas 'procedure' must be the Procedure element which contains the function. The .run() method should accept an optional array of seriesData as 'input' and return an array of seriesData and a procedureFunctionResults object. When extending this class, any additional parameters may be added to 'params'.
    """
    _boundaries = [] 
    """ static list of function boundaries (of class function_boundary.FunctionBoundary)
    """
    _outputs = [] 
    """ static list of function outputs (of class function_boundary.FunctionBoundary)
    """
    _additional_boundaries = False
    """ set to true to allow for additional boundaries """
    _additional_outputs = False
    """ set to true to allow for additional outputs"""
    def __init__(self,params,procedure):
        self._procedure = procedure
        self.parameters = params["parameters"] if "parameters" in params else []
        self.initial_states = params["initial_states"] if "initial_states" in params else []
        self.boundaries = []
        self.setBoundaries(params["boundaries"])
        self.outputs = []
        self.setOutputs(params["outputs"])
        self.input = None
        self.extra_pars = params["extra_pars"] if "extra_pars" in params else dict()
    def setBoundaries(self,boundaries:dict={}):
        self.boundaries = []
        for b in self.__class__._boundaries:
            if b.name in [boundary["name"] for boundary in boundaries]:
                # if len(boundaries[b.name]) < 3:
                #     boundaries[b.name].append(b.name)
                # print("%s" % str(boundaries[b.name]))
                boundary = [boundary for boundary in boundaries if boundary["name"] == b.name][0]
                self.boundaries.append(ProcedureBoundary(boundary,self._procedure._plan,b.optional,b.warmup_only))
            else:
                raise Exception("Missing NodeVariableIdTuple for boundary %s of procedure %s" % (str(b.name), str(self._procedure.id)))
        if self.__class__._additional_boundaries:
            for key in [boundary["name"] for boundary in boundaries]:
                if key not in [b.name for b in self.boundaries]:
                    # if len(boundaries[key]) < 3:
                    #     boundaries[key].append(key)
                    boundary = [boundary for boundary in boundaries if boundary["name"] == key][0]
                    self.boundaries.append(ProcedureBoundary(boundary,self._procedure._plan))
    def setOutputs(self,outputs:dict={}):
        for b in self.__class__._outputs:
            if b.name in [o["name"] for o in outputs]:
                # if len(outputs[b.name]) < 3:
                #     outputs[b.name].append(b.name)
                output = [o for o in outputs if o["name"] == b.name][0]
                self.outputs.append(ProcedureBoundary(output,self._procedure._plan,b.optional,compute_statistics=b.compute_statistics))
            else:
                raise Exception("Missing nodeVariable for output %s of procedure %s" % (str(b.name), str(self._procedure.id)))
        if self.__class__._additional_outputs:
            for key in [o["name"] for o in outputs]:
                if key not in [o.name for o in self.outputs]:
                    # if len(outputs[key]) < 3:
                    #     outputs[key].append(key)
                    output = [o for o in outputs if o["name"] == key][0]
                    self.outputs.append(ProcedureBoundary(output,self._procedure._plan))
    def run(self,input=None):
        """
        Placeholder dummy method to be overwritten by actual procedures

        :param input: array of seriesData
        :returns [seriesData], procedureFunctionResults, JSONSerializable
        """
        if input is None:
            input = self._procedure.loadInput(inplace=False)
        # data = self._plan.topology.pivotData(nodes=self.output_nodes,include_tag=False,use_output_series_id=False,use_node_id=True)
        return input, ProcedureFunctionResults({"initial_states": input})
    