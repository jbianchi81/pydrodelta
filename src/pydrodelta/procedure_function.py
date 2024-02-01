from pydrodelta.procedure_boundary import ProcedureBoundary
from pydrodelta.procedure_function_results import ProcedureFunctionResults
from typing import Optional
# import logging

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
    _parameters = []
    """ use this attribute to set parameter constraints. Must be a list of <pydrodelta.model_parameter.ModelParameter>"""
    _states = []
    """ use this attribute to set state constraints. Must be a list of <pydrodelta.model_state.ModelState>"""
    def __init__(self,params : dict,procedure):
        # logging.debug("Running ProcedureFunction constructor")
        self._procedure = procedure
        self.parameters = params["parameters"] if "parameters" in params else []
        self.initial_states = params["initial_states"] if "initial_states" in params else []
        self.boundaries = []
        self.setBoundaries(params["boundaries"])
        self.outputs = []
        self.setOutputs(params["outputs"])
        self.input = None
        self.extra_pars = params["extra_pars"] if "extra_pars" in params else dict()
    def toDict(self) -> dict:
        return {
            "type": type(self).__name__,
            "parameters": self.parameters,
            "initial_states": self.initial_states,
            "boundaries": [b.toDict() for b in self.boundaries],
            "outputs": [o.toDict() for o in self.outputs],
            "extra_pars": self.extra_pars
        }
    def setBoundaries(self,boundaries : dict={}):
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
    def setOutputs(self,outputs : dict={}):
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
    
    def rerun(self,input : list=None, parameters:list|tuple=None, initial_states:list|tuple=None):
        if parameters is not None:
            self.setParameters(parameters)
        if initial_states is not None:
            self.setInitialStates(initial_states)
        return self.run(input)

    def run(self,input : list=None):
        """
        To be overwritten by actual procedure function

        :param input: array of seriesData
        :returns [seriesData], procedureFunctionResults, JSONSerializable
        """
        if input is None:
            input = self._procedure.loadInput(inplace=False)
        # data = self._plan.topology.pivotData(nodes=self.output_nodes,include_tag=False,use_output_series_id=False,use_node_id=True)
        return input, ProcedureFunctionResults({"initial_states": input})
    
    def makeSimplex(self,sigma=0.25,limit=True,ranges:Optional[list]=None):
        if not len(self._parameters):
            raise Exception("_parameters not set for this class")
        points = []
        for i in range(len(self._parameters)+1):
            point = []
            for j, p in enumerate(self._parameters):
                if ranges is not None and len(ranges) - 1 >= j:
                    if len(ranges[j]) < 2:
                        raise ValueError("ranges must be a list of 2-tuples")
                    range_min = ranges[j][0]
                    range_max = ranges[j][1]
                else:
                    range_min = None
                    range_max = None
                point.append(p.makeRandom(sigma=sigma, limit=limit, range_min=range_min, range_max=range_max))
            points.append(point)
        return points

    def setParameters(self,parameters:list|tuple=[]):
        """
        Generic self.parameters setter. If self._parameters is not empty, uses name of each item to set self.paramters as a dict. Else will set a list
        """
        if len(self._parameters):
            self.parameters = {}
            for i, p in enumerate(self._parameters):
                if len(parameters) - 1 < i:
                    raise ValueError("parameters list is too short: %i item is missing" % i)
                self.parameters[p.name] = parameters[i]
        else:
            self.parameters = list(parameters)

    def setInitialStates(self,states:list|tuple=[]):
        """
        Generic self.initial_states setter. If self._states is not empty, uses name of each item to set self.initial_states as a dict. Else will set a list
        """
        if len(self._states):
            self.initial_states = {}
            for i, p in enumerate(self._states):
                if len(states) - 1 < i:
                    raise ValueError("states list is too short: %i item is missing" % i)
                self.initial_states[p.name] = states[i]
        else:
            self.initial_states = list(states)
