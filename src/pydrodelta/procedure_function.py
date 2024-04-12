from .procedure_boundary import ProcedureBoundary
from .procedure_function_results import ProcedureFunctionResults
from typing import Optional, Union, Tuple, List
from .types.procedure_boundary_dict import ProcedureBoundaryDict
from .descriptors.list_descriptor import ListDescriptor
from .descriptors.dict_descriptor import DictDescriptor
from .descriptors.list_or_dict_descriptor import ListOrDictDescriptor
from numpy import array
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
    
    _parameters : list = []
    """ use this attribute to set parameter constraints. Must be a list of <pydrodelta.model_parameter.ModelParameter>"""
    
    _states : list = []
    """ use this attribute to set state constraints. Must be a list of <pydrodelta.model_state.ModelState>"""

    parameters = ListOrDictDescriptor()
    """function parameter values. Ordered list or dict"""

    @property
    def parameter_list(self) -> list:
        """Get parameters list"""
        if type(self.parameters) == list:
            return self.parameters
        elif type(self.parameters) == dict:
            parlist = []
            for parameter in self._parameters:
                if parameter.name not in self.parameters:
                    raise Exception("Key %s missing from parameters" % parameter.name)
                parlist.append(self.parameters[parameter.name])
            return parlist
        else:
            raise TypeError("parameters must be a list or a dict. Instead, it is a %s " % type(self.parameters).__name__)


    initial_states = ListOrDictDescriptor()
    """list or dict of function initial state values"""
    
    @property
    def boundaries(self) -> List[ProcedureBoundary]:
        """List of boundary conditions. Each item is a dict with a name <string> and a node_variable tuple(node_id : int,variable_id : int). The node_variables must map to plan.topology.nodes[node_id].variables[variable_id] """
        return self.__boundaries
    @boundaries.setter
    def boundaries(
        self,
        boundaries : List[ProcedureBoundaryDict]
        ) -> None:
        """Setter of boundaries
        
        Parameters:
        ----------
        boundaries : list
            List of boundary conditions. Each item is a dict with a name <string> and a node_variable <NodeVariableIdTuple>. The node_variables must map to plan.topology.nodes[node_id].variables[variable_id]
        """
        self.__boundaries = []
        for b in self.__class__._boundaries:
            if b.name in [boundary["name"] for boundary in boundaries]:
                # if len(boundaries[b.name]) < 3:
                #     boundaries[b.name].append(b.name)
                # print("%s" % str(boundaries[b.name]))
                boundary = [boundary for boundary in boundaries if boundary["name"] == b.name][0]
                self.__boundaries.append(
                    ProcedureBoundary(
                        name = boundary["name"],
                        node_id = boundary["node_variable"][0],
                        var_id = boundary["node_variable"][1],
                        plan = self._procedure._plan,
                        optional = b.optional,
                        warmup_only = b.warmup_only
                    ))
            else:
                raise Exception("Missing NodeVariableIdTuple for boundary %s of procedure %s" % (str(b.name), str(self._procedure.id)))
        if self.__class__._additional_boundaries:
            for key in [boundary["name"] for boundary in boundaries]:
                if key not in [b.name for b in self.__boundaries]:
                    # if len(boundaries[key]) < 3:
                    #     boundaries[key].append(key)
                    boundary = [boundary for boundary in boundaries if boundary["name"] == key][0]
                    self.__boundaries.append(
                        ProcedureBoundary(
                            name = boundary["name"],
                            node_id = boundary["node_variable"][0],
                            var_id = boundary["node_variable"][1],
                            plan = self._procedure._plan
                        ))
    
    @property
    def outputs(self) -> List[ProcedureBoundary]:
        """list of procedure outputs. Each item is a dict with a name <string> and a node_variable tuple (node_id,variable_id). The node_variables must map to plan.topology.nodes[node_id].variables[variable_id] """
        return self.__outputs
    @outputs.setter
    def outputs(
        self,
        outputs : List[ProcedureBoundaryDict]
        ) -> None:
        """Setter for outputs
        
        Parameters:
        -----------
        outputs : list of dict
            list of procedure outputs. Each item is a dict with a name <string> and a node_variable tuple (node_id, variable_id). The node_variables must map to plan.topology.nodes[node_id].variables[variable_id]
        """
        self.__outputs = []
        for b in self.__class__._outputs:
            if b.name in [o["name"] for o in outputs]:
                # if len(outputs[b.name]) < 3:
                #     outputs[b.name].append(b.name)
                output = [o for o in outputs if o["name"] == b.name][0]
                self.__outputs.append(
                    ProcedureBoundary(
                        name = output["name"],
                        node_id = output["node_variable"][0],
                        var_id = output["node_variable"][1],
                        plan = self._procedure._plan,
                        optional = b.optional,
                        compute_statistics=b.compute_statistics
                    ))
            else:
                raise Exception("Missing nodeVariable for output %s of procedure %s" % (str(b.name), str(self._procedure.id)))
        if self.__class__._additional_outputs:
            for key in [o["name"] for o in outputs]:
                if key not in [o.name for o in self.__outputs]:
                    # if len(outputs[key]) < 3:
                    #     outputs[key].append(key)
                    output = [o for o in outputs if o["name"] == key][0]
                    self.__outputs.append(
                        ProcedureBoundary(
                            name = output["name"],
                            node_id = output["node_variables"][0],
                            var_id = output["node_variables"][1],
                            plan = self._procedure._plan
                        ))
    
    input = ListDescriptor()
    """Input of the procedure function"""

    extra_pars = DictDescriptor()
    """Additional (non-calibratable) parameters"""

    @property
    def limits(self) -> List[Tuple[float,float]]:
        """Parameter limits"""
        return [(float(x.min), float(x.max)) for x in self._parameters]

    _pivot_input : bool = False
    """Set to True if the run method requires a pivoted input"""

    @property
    def pivot_input(self) -> bool:
        """Read-only property. Specifies if the run method of the procedure function requires a pivoted input"""
        return self._pivot_input

    _no_sim : bool = False
    """Set to True if procedure function produces only forecast (no simulation)"""

    def __init__(
        self,
        procedure,
        parameters : Union[list, dict] = [],
        initial_states : Union[list, dict] = [],
        boundaries : list = [],
        outputs : list = [],
        extra_pars : dict = dict(),
        **kwargs
        ):
        """Initiate a procedure function
        
        Parameters:
        -----------
        procedure : Procedure
        
            Procedure containing this function
        
        parameters : list or dict of floats 
        
            function parameter values. Ordered list or dict
            
        initial_states : list or dict of floats
        
            list of function initial state values. Ordered list or dict
        
        boundaries : list of dict
        
            List of boundary conditions. Each item is a dict with a name <string> and a node_variable <NodeVariableIdTuple>
        
        outputs : list of dict
        
            list of procedure outputs. Each item is a dict with a name <string> and a node_variable tuple <NodeVariableIdTuple>
        
        extra_pars: dict
        
            Additional (non-calibratable) parameters"""
        # logging.debug("Running ProcedureFunction constructor")
        self._procedure = procedure
        self.parameters = parameters
        self.initial_states = initial_states
        self.boundaries = boundaries
        self.outputs = outputs
        self.input = None
        self.extra_pars = extra_pars
    def toDict(self) -> dict:
        """Convert this procedureFunction to a dict
        
        Returns:
        --------
        dict"""
        return {
            "type": type(self).__name__,
            "parameters": self.parameters,
            "initial_states": self.initial_states,
            "boundaries": [b.toDict() for b in self.boundaries],
            "outputs": [o.toDict() for o in self.outputs],
            "extra_pars": self.extra_pars
        }

    def rerun(
        self,
        input : list = None,
        parameters : Union[list,tuple] = None, 
        initial_states : Union[list,tuple] = None
        ) -> Tuple[list, dict]:
        """Execute the procedure function with the given parameters and initial_states
        
        Parameters:
        -----------
        input : list if DataFrames
            Procedure function input (boundary conditions). If None, loads using .loadInput()
        
        parameters : list or tuple
            Set procedure function parameters (self.parameters).
        
        initial_states : list or tuple
            Set initial states (self.initial_states)
        
        Returns:
        --------
        2-tuple : first element is the procedure function output (list of DataFrames), while second is a ProcedureFunctionResults object"""
        if parameters is not None:
            self.setParameters(parameters)
        if initial_states is not None:
            self.setInitialStates(initial_states)
        return self.run(input)

    def run(
        self,
        input : list = None
        ) -> Tuple[list, dict]:
        """
        Placeholder procedure function execution. To be overwritten in subclasses

        Parameters:
        -----------
        input : list of DataFrames
            Procedure function input (boundary conditions). If None, loads using .loadInput()

        Returns:
        --------
        2-tuple : first element is the procedure function output (list of DataFrames), while second is a ProcedureFunctionResults object
        """
        if input is None:
            input = self._procedure.loadInput(inplace=False)
        # data = self._plan.topology.pivotData(nodes=self.output_nodes,include_tag=False,use_output_series_id=False,use_node_id=True)
        return input, ProcedureFunctionResults(initial_states = input)
    
    def makeSimplex(
        self,
        sigma : float = 0.25,
        limit : bool = True,
        ranges : Optional[list] = None
        ) -> list:
        """Generate Simplex from procedure function parameters. 
        
        Generates a list of len(self._parameters)+1 parameter sets randomly using a normal distribution centered in the corresponding parameter range and with variance=sigma
        
        Parameters:
        -----------
        sigma : float (default 0.25)
            Variance of the normal distribution relative to the range(1 = max_range - min_range)
        
        limit : bool (default True)
            Truncate values outside of the min-max range
            
        ranges : list or None
            Override parameter ranges with these values. Length must be equal to self._parameters and each element of the list must be a 2-tuple (range_min, range_max) 
        
        Returns:
        --------
        list : list of  length = len(self._parameters) + 1 where each element is a list of floats of length = len(self._parameters)"""
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
            points.append(list(point))
        return points

    def setParameters(
        self,
        parameters : Union[list,tuple] = []
        ) -> None:
        """
        Generic self.parameters setter. If self._parameters is not empty, uses name of each item to set self.parameters as a dict. Else will set a list

        Parameters:
        -----------
        parameters : list or tuple
            Procedure function parameters to set
        """
        if len(self._parameters):
            self.parameters = {}
            for i, p in enumerate(self._parameters):
                if len(parameters) - 1 < i:
                    raise ValueError("parameters list is too short: %i item is missing" % i)
                self.parameters[p.name] = parameters[i]
        else:
            self.parameters = list(parameters)

    def setInitialStates(
        self,
        states : Union[list,tuple] = []
        ) -> None:
        """
        Generic self.initial_states setter. If self._states is not empty, uses name of each item to set self.initial_states as a dict. Else will set a list

        Parameters:
        states : list or tuple
            Procedure function initial states to set
        """
        if len(self._states):
            self.initial_states = {}
            for i, p in enumerate(self._states):
                if len(states) - 1 < i:
                    raise ValueError("states list is too short: %i item is missing" % i)
                self.initial_states[p.name] = states[i]
        else:
            self.initial_states = list(states)
