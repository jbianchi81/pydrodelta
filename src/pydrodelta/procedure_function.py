from .procedure_boundary import ProcedureBoundary
from .procedure_function_results import ProcedureFunctionResults
from typing import Optional, Union, Tuple, List
from .types.procedure_boundary_dict import ProcedureBoundaryDict
from .descriptors.list_descriptor import ListDescriptor
from .descriptors.dict_descriptor import DictDescriptor
from .descriptors.list_or_dict_descriptor import ListOrDictDescriptor
from .descriptors.string_descriptor import StringDescriptor
from pydrodelta.descriptors.datetime_descriptor import DatetimeDescriptor
from numpy import array
from pandas import DataFrame
from datetime import datetime
from .types.typed_list import TypedList
from .types.enhanced_typed_list import EnhancedTypedList
from .function_boundary import FunctionBoundary
from .util import getInputListFromDataFrame
# import logging

class ProcedureFunction:
    """
    Abstract class to represent the transformation function of the procedure. It is instantiation, 'params' should be a dictionary which may contain an array of numerical or string 'parameters', an array of numerical or string 'initial_states', whereas 'procedure' must be the Procedure element which contains the function. The .run() method should accept an optional array of seriesData as 'input' and return an array of seriesData and a procedureFunctionResults object. When extending this class, any additional parameters may be added to 'params'.
    """

    _boundaries = TypedList(FunctionBoundary)
    """ static list of function boundaries (of class function_boundary.FunctionBoundary)
    """
    
    _outputs = TypedList(FunctionBoundary) 
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
        self.__boundaries = EnhancedTypedList(
            ProcedureBoundary, 
            *boundaries,
            unique_id_property="name",
            valid_items_list=[b.__dict__() for b in self.__class__._boundaries],
            allow_additional_ids=self.__class__._additional_boundaries,
            allow_missing=False,
            plan = self._procedure._plan if self._procedure is not None else None
        )
    
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
        self.__outputs = EnhancedTypedList(
            ProcedureBoundary, 
            *outputs,
            unique_id_property="name",
            valid_items_list=[b.__dict__() for b in self.__class__._outputs],
            allow_additional_ids=self.__class__._additional_outputs,
            allow_missing=False,
            plan = self._procedure._plan if self._procedure is not None else None
        )
    
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

    forecast_date = DatetimeDescriptor()
    """Forecast date. By default, copies value from plan"""

    save_results = StringDescriptor()

    def __init__(
        self,
        procedure = None,
        parameters : Union[list, dict] = [],
        initial_states : Union[list, dict] = [],
        boundaries : list = [],
        outputs : list = [],
        extra_pars : dict = dict(),
        forecast_date : datetime = None,
        save_results : str = None,
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
        
            Additional (non-calibratable) parameters
            
        save_results : str = None
            save results into file. Defaults to save_results of plan
        """
        # logging.debug("Running ProcedureFunction constructor")
        self._procedure = procedure
        self.parameters = parameters
        self.initial_states = initial_states
        self.boundaries = boundaries
        self.outputs = outputs
        self.input = None
        self.extra_pars = extra_pars
        if forecast_date is not None:
            self.forecast_date = forecast_date
        elif self._procedure is not None and self._procedure._plan is not None and self._procedure._plan.forecast_date is not None:
            self.forecast_date = self._procedure._plan.forecast_date
        else:
            self.forecast_date = None
        if save_results is not None:
            self.save_results = save_results
        elif self._procedure is not None:
            self.save_results = self._procedure.save_results
        else:
            self.save_results = None

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
        parameters : Union[list,tuple] = [],
        reset : bool = True
        ) -> None:
        """
        Generic self.parameters setter. If self._parameters is not empty, uses name of each item to set self.parameters as a dict. Else will set a list

        Parameters:
        -----------
        parameters : list or tuple
            Procedure function parameters to set
        reset : bool = True
            Start new parameter set from empty dict
        """
        if len(self._parameters):
            if reset:
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

    def extractListsFromInput(self, input : List[DataFrame], allow_na : List[bool]=[False]) -> List[List[float]]:
        while len(allow_na) < len(input):
            allow_na.append(False)
        return [ getInputListFromDataFrame(df,allow_na[i], self._procedure.id if self._procedure is not None else None) for i, df in enumerate(input) ]
    
    def pivotInputOutput(self, input : List[DataFrame], output : List[DataFrame] = [], other : dict = None) -> DataFrame:
        if not len(input):
            raise ValueError("input must be of length 1 or greater")
        result = input[0][["valor"]].rename(columns={"valor": self._boundaries[0].name})
        for i in range(1,len(self._boundaries)):
            result = result.join(input[i][["valor"]].rename(columns={"valor": self._boundaries[i].name}))
        for i in range(0,len(self._outputs)):
            if type(output[i]) == DataFrame:
                result = result.join(output[i][["valor"]].rename(columns={"valor": self._outputs[i].name}))
            else:
                result[self._outputs[i].name] = output[i]
        if other is not None:
            # must be a a dict where key is the column name and value is the list of values
            for name, values in other.items():
                result[name] = values
        return result