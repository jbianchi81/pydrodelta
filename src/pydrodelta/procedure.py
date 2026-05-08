import logging
import json
from . import util
from a5client import createEmptyObsDataFrame
from .result_statistics import ResultStatistics, ResultStatisticsDict, ResultStatisticsShortDict
from .procedure_function_results import ProcedureFunctionResults
from .pydrology import testPlot
from .calibration.downhill_simplex_calibration import DownhillSimplexCalibration
from .calibration.linear_regression_calibration import LinearRegressionCalibration
from typing import Optional, Union, List, Tuple, Literal, overload, TypedDict, cast
from pandas import DataFrame
from .descriptors.int_descriptor import IntDescriptor
from .descriptors.bool_descriptor import BoolDescriptor
from .descriptors.bool_or_none_descriptor import BoolOrNoneDescriptor
from .descriptors.dict_descriptor import DictDescriptor
from .descriptors.string_descriptor import StringDescriptor
from pathlib import Path
from dateutil.relativedelta import relativedelta
from .observed_node_variable import ObservedNodeVariable
from .base import Base
from .procedure_boundary import ProcedureBoundary
from .procedure_function_results import ProcedureFunctionResults
from typing import Optional, Union, Tuple, List, cast, Any, Mapping, Dict, overload, TYPE_CHECKING
from .types.procedure_boundary_dict import ProcedureBoundaryDict
from .descriptors.list_descriptor import ListDescriptor
from .descriptors.list_or_dict_descriptor import ListOrDictDescriptor
from pydrodelta.descriptors.datetime_descriptor import DatetimeDescriptor
from numpy import array
from pandas import DataFrame
from datetime import datetime
from .types.typed_list import TypedList
from .types.enhanced_typed_list import EnhancedTypedList
from .function_boundary import FunctionBoundary
from .util import getInputListFromDataFrame, tvpListToDataFrame
from .model_parameter import ModelParameter
from a5client.util_types import TVPList
from pydrodelta.validation import getSchemaAndValidate

class StatsDict(TypedDict):
    procedure_id : Union[str,int]
    function_type : str
    results : Optional[List[Union[ResultStatisticsDict, ResultStatisticsShortDict, None]]] 
    results_val : Optional[List[Union[ResultStatisticsDict, ResultStatisticsShortDict, None]]] 

class Procedure(Base):
    """
    A Procedure defines a hydrological, hydrodinamic or static procedure which takes one or more NodeVariables from the Plan as boundary condition, one or more NodeVariables from the Plan as outputs and a ProcedureFunction. The input is read from the selected boundary NodeVariables and fed into the ProcedureFunction which produces an output, which is written into the output NodeVariables
    
    Parameters:
    ----------

    id : int or str
        Identifier of the procedure

    function : dict
        ProcedureFunction configuration dict (see ProcedureFunction)

    plan : Plan
        Plan containing this procedure

    initial_states : list or None
        List of procedure initial states. The order of the states is defined in .function._states

    parameters : list or None
        List of procedure parameters. The order of the parameters is defined in .function._model_parameters 

    time_interval : str or dict (time duration)
        Time step duration of the procedure

    time_offset : str or dict (time duration)
        Time offset duration of the procedure

    save_results : str or None
        Save procedure results into this file (csv pivoted table)

    save_dict : str or None
        Save procedure results into this file (json)

    overwrite : bool
        When exporting procedure results into the topology, overwrite observations in NodeVariable.data   

    overwrite_original : bool
        When exporting procedure results into the topology, overwrite observations in NodeVariable.original_data

    calibration : dict
        Configuration for calibration procedure (see Calibration)

    base_path : Union[str,Path,None]

    """

    _available_calibration_methods : dict = {
        "downhill-simplex": DownhillSimplexCalibration,
        "linear-regression": LinearRegressionCalibration
    }

    _calibration : Union[DownhillSimplexCalibration, LinearRegressionCalibration,None] = None

    @property
    def calibration(self) -> Union[DownhillSimplexCalibration, LinearRegressionCalibration,None]:
        return self._calibration
    @calibration.setter
    def calibration(self,calibration : Optional[dict]) -> None:
        if calibration is not None:
            if "method" not in calibration:
                raise KeyError("Required key 'method' missing from calibration argument")
            if calibration["method"] not in self._available_calibration_methods:
                raise ValueError("Calibration method '%s' not defined" % calibration["method"])
            kwargs = calibration.copy()
            del kwargs["method"]
            self._calibration = self._available_calibration_methods[calibration["method"]](procedure=self, **kwargs, base_path=self.base_path)
            """Configuration for calibration"""
        else:
            self._calibration = None

    adjust = BoolDescriptor()
    """Adjust output series using observations. Adjustment is performed after statistics computation"""

    warmup_steps = IntDescriptor()
    """For output adjustment, discard this number of initial rows"""

    tail_steps = IntDescriptor()
    """For output adjustment, use only this number of final rows"""

    linear_model = DictDescriptor()
    """Linear model fit results"""

    error_band = BoolOrNoneDescriptor()
    """Add error band series to adjusted result"""

    read_sim = BoolDescriptor()
    """Instead of reading .data from input node variables, read .series_sim[0].data """

    sim_index = IntDescriptor()
    """With read_sim, which series_sim index of node variables to read from"""

    adjust_method : Literal['lfit', 'arima']
    """Adjust method. Options: lfit (linear regression), arima (ARIMA)"""

    drop_warmup = BoolDescriptor()
    """Eliminate warmup steps of adjusted output"""

    @property
    def data(self) -> Optional[DataFrame]:
        try:
            return self.pivotInOut()
        except Exception:
            return None
    
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
    
    _parameters : List[ModelParameter] = []
    """ use this attribute to set parameter constraints. Must be a list of <pydrodelta.model_parameter.ModelParameter>"""
    
    _states : list = []
    """ use this attribute to set state constraints. Must be a list of <pydrodelta.model_state.ModelState>"""

    parameters = ListOrDictDescriptor() #  : Union[List[float], Dict[str, float]]
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


    initial_states : Union[List[float],Dict[str,float]] # = ListOrDictDescriptor()
    """list or dict of function initial state values"""
    
    @property
    def boundaries(self) -> EnhancedTypedList[ProcedureBoundary]:
        """List of boundary conditions. Each item is a dict with a name <string> and a node_variable tuple(node_id : int,variable_id : int). The node_variables must map to plan.topology.nodes[node_id].variables[variable_id] """
        return self.__boundaries
    
    @boundaries.setter
    def boundaries(
        self,
        boundaries : Union[List[ProcedureBoundaryDict],List[TVPList],List[DataFrame],DataFrame]
        ) -> None:
        """Setter of boundaries
        
        Parameters:
        ----------
        boundaries : list
            List of boundary conditions. Each item is a dict with a name <string> and a node_variable <NodeVariableIdTuple>. The node_variables must map to plan.topology.nodes[node_id].variables[variable_id]
        """
        if isinstance(boundaries, DataFrame):
            boundaries_ = self.dfToBoundaryDicts(boundaries)
        else:
            isdict = [isinstance(b, dict) for b in boundaries]
            if all(isdict):
                boundaries_ = cast(List[ProcedureBoundaryDict],boundaries)
            elif not any(isdict):
                boundaries_no_dict = cast(
                    list[TVPList] | list[DataFrame],
                    boundaries
                )
                boundaries_ = [self.tvpListToBoundaryDict(b, i) for (i, b) in enumerate(boundaries_no_dict)]
            else:
                raise TypeError("Boundaries must be all dict or all list, not mixed")
        self.__boundaries = EnhancedTypedList(
            ProcedureBoundary, 
            *boundaries_,
            unique_id_property="name",
            valid_items_list=[b.__dict__() for b in self.__class__._boundaries],
            allow_additional_ids=self.__class__._additional_boundaries,
            allow_missing=False,
            plan = self._plan
        )
    @property
    def outputs(self) -> EnhancedTypedList[ProcedureBoundary]:
        """list of procedure outputs. Each item is a dict with a name <string> and a node_variable tuple (node_id,variable_id). The node_variables must map to plan.topology.nodes[node_id].variables[variable_id] """
        return self.__outputs
    @outputs.setter
    def outputs(
        self,
        outputs : Union[List[ProcedureBoundaryDict],List[TVPList],List[DataFrame],DataFrame]
        ) -> None:
        """Setter for outputs
        
        Parameters:
        -----------
        outputs : list of dict
            list of procedure outputs. Each item is a dict with a name <string> and a node_variable tuple (node_id, variable_id). The node_variables must map to plan.topology.nodes[node_id].variables[variable_id]
        """
        if isinstance(outputs, DataFrame):
            outputs_ = self.dfToBoundaryDicts(outputs)
        else:
            isdict = [isinstance(b, dict) for b in outputs]
            if all(isdict):
                outputs_ = cast(List[ProcedureBoundaryDict],outputs)
            elif not any(isdict):
                outputs_no_dict = cast(
                    list[TVPList] | list[DataFrame],
                    outputs
                )
                outputs_ = [self.tvpListToBoundaryDict(b, i,is_output=True) for (i, b) in enumerate(outputs_no_dict)]
            else:
                raise TypeError("Outputs must be all dict or all list, not mixed")
        self.__outputs = EnhancedTypedList(
            ProcedureBoundary, 
            *outputs_,
            unique_id_property="name",
            valid_items_list=[b.__dict__() for b in self.__class__._outputs],
            allow_additional_ids=self.__class__._additional_outputs,
            allow_missing=False,
            plan = self._plan
        )
    
    input : Optional[Union[List[DataFrame],DataFrame]]
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

    save_results : Optional[Path]

    def __init__(
        self,
        id : Union[int, str],
        plan = None,
        initial_states : Union[list, dict] = [],
        parameters : Union[List[Any], Mapping[str, Any]] = [],
        time_interval : Optional[Union[float,util.IntervalDict]] = None,
        time_offset : Optional[Union[float,util.IntervalDict]] = None,
        save_results : Optional[str] = None,
        overwrite : bool = False,
        overwrite_original : bool = False,
        calibration : Optional[dict] = None,
        adjust : bool = False,
        adjust_method : Literal['lfit', 'arima'] = "lfit",
        warmup_steps : Optional[int] = None,
        tail_steps : Optional[int] = None,
        error_band : Optional[bool] = None,
        read_sim : bool = False,
        sim_index : int = 0,
        save_dict : Optional[str] = None,
        drop_warmup : bool = False,
        boundaries : Union[List[ProcedureBoundaryDict],List[TVPList],List[DataFrame],DataFrame] = [],
        outputs : Union[List[ProcedureBoundaryDict],List[TVPList],List[DataFrame],DataFrame] = [],
        extra_pars : dict = dict(),
        forecast_date : Optional[datetime] = None,
        **kwargs
        ):
        """A procedure
        
        Parameters:
        -----------
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
        if "type" in kwargs:
            del kwargs["type"]
        super().__init__(**kwargs)
        getSchemaAndValidate(
            {
                "id": id,
                "type": type(self).__name__,
                "plan": plan,
                "initial_states": initial_states,
                "parameters": parameters,
                "time_interval": time_interval,
                "time_offset": time_offset,
                "save_results": save_results,
                "overwrite": overwrite,
                "overwrite_original": overwrite_original,
                "calibration": calibration,
                "adjust": adjust,
                "adjust_method": adjust_method,
                "warmup_steps": warmup_steps,
                "tail_steps": tail_steps,
                "error_band": error_band,
                "read_sim": read_sim,
                "sim_index": sim_index,
                "save_dict": save_dict,
                "drop_warmup": drop_warmup,
                "boundaries": boundaries,
                "outputs": outputs,
                "extra_pars": extra_pars,
                "forecast_date": forecast_date,
            },
            "Procedure")
        
        self.id : Union[int,str] = id
        """Identifier of the procedure"""
        self._plan = plan
        """Plan containing this procedure"""
        self.save_results = self.resolve_path(save_results)
        """Save procedure results into this file (csv pivoted table)"""
        self.initial_states = initial_states
        """List of procedure initial states"""
        # if type(function) != dict:
        #     if type(function) != str:
        #         raise TypeError("Value of argument 'function' must be of type dict or str")
        #     function_file = function
        #     try:
        #         f = open(function_file)
        #     except IOError as e:
        #         raise IOError("Couldn´t open function file %s: %s" % (function_file, str(e)))
        #     try:
        #         function = json.load(f)
        #     except json.JSONDecodeError as e:
        #         raise json.JSONDecodeError("JSON decode error on parsing function file %s: %s" % (function_file, e.msg))
        #     f.close()
        self.parameters = dict(parameters) if isinstance(parameters, Mapping) else parameters
        """List of procedure parameters"""
        self.boundaries = boundaries
        self.outputs = outputs
        self.extra_pars = extra_pars
        if forecast_date is not None:
            self.forecast_date = forecast_date
        
        self.time_interval : Optional[relativedelta] = util.interval2timedelta(time_interval) if time_interval is not None else None
        """Time step duration of the procedure"""
        self.time_offset : Optional[relativedelta] = util.interval2timedelta(time_offset) if time_offset is not None else None
        """Time offset duration of the procedure"""
        self.input : Optional[Union[DataFrame,List[DataFrame]]] = None # <- boundary conditions
        """Ordered list of input DataFrames of the procedure (the boundary conditions). Run .loadInput(inplace=True) to populate"""
        self.output : Optional[Union[List[DataFrame],DataFrame]] = None # <- outputs
        """Ordered list of output DataFrames of the procedure. Run .run(inplace=True) to populate"""
        self.output_obs : Optional[Union[DataFrame,List[DataFrame]]] = None # <- observed values for error calculation
        """List of DataFrames of observed values for error calculation. Same order than .output. Run .loadOutputObs(inplace=True) to populate"""
        self.states : Optional[Union[DataFrame,list]] = None
        """Pivot DataFrame of procedure states. Byproduct of .run(inplace=True) execution"""
        self.procedure_function_results : Optional[ProcedureFunctionResults] = None
        """Results of the procedure function execution"""
        self.overwrite : bool = bool(overwrite)
        """When exporting procedure results into the topology, overwrite observations in NodeVariable.data"""
        self.overwrite_original : bool = bool(overwrite_original)
        """When exporting procedure results into the topology, overwrite observations in NodeVariable.original_data"""
        # self.simplex : list = None
        self.calibration = calibration
        """Configuration for calibration"""
        self.adjust = adjust
        self.warmup_steps = warmup_steps
        self.tail_steps = tail_steps
        self.linear_model = None
        self.error_band = error_band
        self.read_sim = read_sim
        self.sim_index = sim_index
        self.adjust_method = adjust_method
        self.save_dict = self.resolve_path(save_dict)
        self.drop_warmup = drop_warmup
    
    def getCalibrationPeriod(self) -> Union[tuple,None]:
        """Read the calibration period from the calibration configuration"""
        if self.calibration is not None:
            return self.calibration.calibration_period
        else:
            return None
    def getResultIndex(self) -> int:
        """Read the calibration index from the calibration configuration"""
        if self.calibration is not None:
            return self.calibration.result_index
        else:
            return 0
    def toDict(self) -> dict:
        """Convert this instance into a dict"""
        return {
            'id': self.id, 
            'initial_states': self.initial_states, 
            "type": type(self).__name__,
            "parameters": self.parameters,
            "boundaries": [b.toDict() for b in self.boundaries],
            "outputs": [o.toDict() for o in self.outputs],
            "extra_pars": self.extra_pars, 
            'time_interval': util.relativedelta_to_iso(self.time_interval) if self.time_interval is not None else None, 
            'time_offset': util.relativedelta_to_iso(self.time_offset) if self.time_offset is not None else None, 
            'input': [x.to_dict(orient="records") if isinstance(x, DataFrame) else x for x in self.input] if self.input is not None else None, 
            'output': [x.to_dict(orient="records") if isinstance(x, DataFrame) else x  for x in self.output] if self.output is not None else None, 
            'output_obs': [x.to_dict(orient="records")  if isinstance(x, DataFrame) else x for x in self.output_obs] if self.output_obs is not None else None, 
            'states': self.states.to_dict(orient="records") if isinstance(self.states,DataFrame) else self.states,
            'procedure_function_results': self.procedure_function_results.toDict() if self.procedure_function_results is not None else None, 
            'save_results': str(self.save_results) if self.save_results is not None else None, 
            'overwrite': self.overwrite, 
            'overwrite_original': self.overwrite_original, 
            'calibration': self.calibration.toDict() if self.calibration is not None else None
        }

    def loadInputDefault(self) -> None:
        """Loads input with default behaviour according to the procedure function"""
        if self.pivot_input:
            self.loadInput(
                inplace = True,
                pivot = True,
                use_boundary_name = True,
                tag_column = False
            )
        else:
            self.loadInput()

    @overload
    def loadInput(
        self,
        inplace : Literal[True] = True,
        pivot : bool = False,
        use_boundary_name : bool = False,
        tag_column : bool = True,
        read_sim : Optional[bool] = None,
        sim_index : Optional[int] = None
        ) -> None: ...
    @overload
    def loadInput(
        self,
        inplace : Literal[False],
        pivot : Literal[False] = False,
        use_boundary_name : bool = False,
        tag_column : bool = True,
        read_sim : Optional[bool] = None,
        sim_index : Optional[int] = None
        ) -> List[DataFrame]: ...
    @overload
    def loadInput(
        self,
        inplace : Literal[False],
        *,
        pivot : Literal[True],
        use_boundary_name : bool = False,
        tag_column : bool = True,
        read_sim : Optional[bool] = None,
        sim_index : Optional[int] = None
        ) -> DataFrame: ...
    def loadInput(
        self,
        inplace : bool = True,
        pivot : bool = False,
        use_boundary_name : bool = False,
        tag_column : bool = True,
        read_sim : Optional[bool] = None,
        sim_index : Optional[int] = None
        ) -> Union[List[DataFrame],DataFrame,None]:
        """
        Loads the boundary variables defined in self.boundaries. Takes .data from each element of self.boundaries and returns a list. If pivot=True, joins all variables into a single DataFrame

        Parameters:
        ----------

        inplace : bool = True
            If True, saves result into self.data and returns None
        
        pivot: bool = False
            If true, joins all variables into a single DataFrame

        use_boundary_name : bool = False
            When pivot=True, use boundary name as column name for "valor". If tag_column is True, boundary name will be suffixed to "tag_". If False, a concatenation of node_id and variable_id is used as suffix to the input column names
        
        tag_column : bool = True
            When pivot=True, create a tag column for each boundary

        read_sim : bool = False
            Instead of reading .data of input node variables, read .series_sim[0].data . Defaults to self.read_sim
        
        sim_index : int = 0
            read this series_sim index of boundary node variables (with read_sim) 
        """
        read_sim = read_sim if read_sim is not None else self.read_sim
        sim_index = sim_index if sim_index is not None else self.sim_index
        if pivot:
            data : DataFrame = createEmptyObsDataFrame(extra_columns={"tag":str}) if tag_column else createEmptyObsDataFrame()
            columns = ["valor","tag"] if tag_column else ["valor"] 
            for boundary in self.boundaries:
                boundary_data : DataFrame
                if boundary.data is not None:
                    use_boundary_name = True
                    boundary_data = boundary.data
                    boundary_data["tag"] = "inline"
                else:
                    if boundary._variable is None:
                        raise Exception("variable not set. data not set")
                    if read_sim and boundary._variable.series_sim is not None and len(boundary._variable.series_sim) >= sim_index + 1 and boundary._variable.series_sim[sim_index].data is not None and len(boundary._variable.series_sim[sim_index].data):
                        boundary_data = boundary._variable.series_sim[sim_index].data
                    elif boundary._variable.data is not None and len(boundary._variable.data):
                        boundary_data = boundary._variable.data
                    else:
                        continue
                if use_boundary_name:
                    data = data.join(
                        boundary_data[columns][boundary_data.valor.notnull()].rename(
                            columns={
                                "valor": boundary.name, 
                                "tag": "tag_%s" % boundary.name
                            }
                        ),
                        how='outer',
                        # rsuffix=rsuffix,
                        sort=True)
                else:
                    rsuffix = "_%s_%i" % (str(boundary.node_id), boundary.var_id)
                    data = data.join(
                        boundary_data[columns][boundary_data.valor.notnull()],
                        how='outer',
                        rsuffix=rsuffix,
                        sort=True)
            for column in columns:
                del data[column]
            # data = data.replace({np.nan:None})
            if inplace:
                self.input = data
            else:
                return data
        else:
            data_ : List[DataFrame]= []
            for boundary in self.boundaries:
                logging.debug("loading boundary: %s: node %i, variable %i, optional: %s, warmup_only: %s" % (boundary.name, boundary.node_id,boundary.var_id, str(boundary.optional), str(boundary.warmup_only)))
                if boundary.data is not None:
                    data_.append(boundary.data.copy())
                else:
                    if boundary._variable is None:
                        raise Exception("variable not set")
                    if not boundary.optional:
                        try:
                            warmup_only = boundary.warmup_only if boundary.warmup_only else False
                            boundary.assertNoNaN(warmup_only, read_sim, 0, boundary.warmup_steps)
                        except AssertionError as e:
                            raise Exception("load input error at procedure %s, node %i, variable, %i: %s" % (self.id, boundary.node_id, boundary.var_id, str(e)))
                    if read_sim:
                        if boundary._variable.series_sim is None:
                            raise RuntimeError("series_sim not set")
                        if boundary._variable.series_sim[sim_index].data is None:
                            raise Exception("load input error at procedure %s, node %i, variable %i: series_sim[%i].data is None" % (self.id, boundary.node_id, boundary.var_id, sim_index))
                        data_.append(boundary._variable.series_sim[sim_index].data.copy())
                    else:
                        data_.append(boundary._variable.data.copy())
            if inplace:
                self.input = data_
            else:
                return data_
        
    def getInputListFromDataFrame(self, df : DataFrame, allow_na : bool=False) -> List[float]:
        return util.getInputListFromDataFrame(df, allow_na, self.id)  

    @overload
    def loadOutputObs(
        self,
        inplace : Literal[False],
        pivot : Literal[True]
    ) -> DataFrame: ...
    @overload
    def loadOutputObs(
        self,
        inplace : Literal[True],
        pivot : Literal[False] = False
    ) -> None: ...
    @overload
    def loadOutputObs(
        self,
        inplace : Literal[False] = False,
        pivot : Literal[False] = False
    ) -> List[DataFrame]: ...
    @overload
    def loadOutputObs(
        self,
        inplace : Literal[True],
        pivot : Literal[True]
    ) -> None: ...
    def loadOutputObs(
        self,
        inplace : bool = True,
        pivot : bool = False
        ) -> Union[DataFrame,List[DataFrame],None]:
        """
        Load observed values of output variables defined in self.outputs. Used in error calculation.

        Parameters:
        -----------

        inplace : bool
            If True, saves result into self.output_obs and returns None
        
        pivot: bool
            If true, joins all variables into a single DataFrame
        """
        if pivot:
            data : DataFrame = createEmptyObsDataFrame()
            for i, output in enumerate(self.outputs):
                if output.data is not None:
                    colname = "valor_%i" % (i + 1) 
                    data = data.join(output.data[["valor"]].rename(columns={"valor": colname}).dropna(),how='outer',sort=True)
                else:
                    if output._variable is None:
                        raise Exception("Variable is not set")
                    if output._variable.data is not None and len(output._variable.data):
                        colname = "valor_%i" % (i + 1) 
                        data = data.join(output._variable.data[["valor"]].rename(columns={"valor": colname}).dropna(),how='outer',sort=True)
                    else:
                        logging.warning("loadOutputObs: Procedure: %s, output: %i, with no data. Skipped." % (self.id,i))
            # logging.debug("loadOutputObs: columns: %s" % (data.columns))
            if "valor" in data.columns:
                data.drop(columns="valor",inplace=True)
            if inplace:
                self.output_obs = data
            else:
                return data
        else:
            data_ : List[DataFrame] = []
            for output in self.outputs:
                if output.data is not None:
                    data_.append(output.data[["valor"]].dropna())
                else:
                    if output._variable is None:
                        raise Exception("Variable is not set")
                    data_.append(output._variable.data[["valor"]].dropna())
            if inplace:
                self.output_obs = data_
            else:
                return data_
            
    def computeStatistics(
        self, 
        obs : Optional[Union[List[DataFrame],DataFrame]] = None, 
        sim : Optional[Union[List[DataFrame],DataFrame]] = None,
        calibration_period : Optional[tuple]=None,
        result_index : int = 0,
        tail : Optional[int] = None,
        warmup : Optional[int] = None
        ) -> Tuple[List[ResultStatistics],List[ResultStatistics]]:
        """Compute statistics over procedure results.
        
        Parameters:
        ----------

        obs : list of DataFrames or None
            List of observation DataFrames
        
        sim : list of DataFrames or None
            List of simulated values. Must be of the same length as obs

        calibration_period : tuple or None
            start and end date for split statistics computations between calibration and validation periods

        Returns
        -------
        (calibration_results, validation_results) : 2-length tuple of lists of ResultStatistics. The length of the lists equals that of obs 
        """
        obs = obs if obs is not None else [self.output_obs] if isinstance(self.output_obs, DataFrame) else self.output_obs
        if obs is None:
            raise Exception("obs (self.output_obs) is not set") 
        sim = sim if sim is not None else self.output
        if sim is None:
            raise Exception("Sim (self.output) is not set") 
        tail = tail if tail is not None else self.tail_steps
        warmup = warmup if warmup is not None else self.warmup_steps
        result = list()
        result_val = list()
        # if len(obs) < len(sim):
        #     raise Exception("length of obs must be equal than length of sim")
        for i, o in enumerate(self.outputs):
            if len(sim) < i + 1:
                raise Exception("List of sim outputs is shorter than function.outputs (%i < %i" % (len(sim), len(self.outputs)))
            if len(obs) < i + 1:
                raise Exception("List of obs outputs is smaller than function.outputs (%i < %i" % (len(obs), len(self.outputs)))
            df_obs = obs[i].iloc[warmup:].copy() if warmup is not None else obs[i]
            df_obs = cast(DataFrame,df_obs.tail(tail)) if tail is not None else cast(DataFrame,df_obs)
            df_sim = sim[i].iloc[warmup:].copy() if warmup is not None else sim[i]
            df_sim = cast(DataFrame,df_sim.tail(tail)) if tail is not None else cast(DataFrame,df_sim)
            inner_join = df_sim[["valor"]].rename(mapper={"valor":"sim"},axis=1).join(df_obs[["valor"]].rename(mapper={"valor":"obs"},axis=1),how="inner").dropna()
            if calibration_period is not None:
                inner_join_cal, inner_join_val = util.groupByCalibrationPeriod(inner_join,calibration_period)
                if i == result_index and (inner_join_cal is None or not len(inner_join_cal)):
                    raise Exception("Invalid calibration period: no data found")
                result.append(ResultStatistics(
                    obs = inner_join_cal["obs"].values.tolist() if inner_join_cal is not None else [], 
                    sim = inner_join_cal["sim"].values.tolist() if inner_join_cal is not None else [], 
                    compute = o.compute_statistics, 
                    metadata = o.toDict(),
                    calibration_period = calibration_period,
                    group = "cal"
                ))
                if inner_join_val is not None and len(inner_join_val):
                    result_val.append(ResultStatistics(
                        obs = inner_join_val["obs"].values.tolist(), 
                        sim = inner_join_val["sim"].values.tolist(), 
                        compute = o.compute_statistics, 
                        metadata = o.toDict(),
                        calibration_period = calibration_period,
                        group = "val"
                    ))
                else:
                    logging.warning("No data found for validation")
            else:
                result.append(ResultStatistics(
                    obs = inner_join["obs"].values.tolist(), 
                    sim = inner_join["sim"].values.tolist(), 
                    compute = o.compute_statistics, 
                    metadata = o.toDict()
                ))
        if self.procedure_function_results is not None:
            self.procedure_function_results.setStatistics(result)
            if len(result_val):
                self.procedure_function_results.setStatisticsVal(result_val)
        return result, result_val
    
    @overload
    def read_statistics(
        self, 
        short : bool = False,
        *,
        as_dataframe : Literal[True]
        ) -> DataFrame: ...
    @overload
    def read_statistics(
        self, 
        short : bool = False,
        *,
        as_dataframe : Literal[False]=False
        ) -> StatsDict: ...
    def read_statistics(
        self, 
        short : bool = False,
        as_dataframe : bool = False
        ) -> Union[DataFrame,StatsDict]:
        """Get result statistics as a dict or DataFrame
        
        Args:
            short : bool = False
                Get statistics summary
            as_dataframe : bool = False
                return DataFrame instead of dict

        Returns
        -------
        statistics : dict of the form:
            {
                "procedure_id": int,
                "function_type": str,
                "results": List[dict]
            }
            where results is a list of dict, one per procedure output
        Or DataFrame with columns: n, rmse, r, nse, n_val, rmse_val, r_val, nse_val 
        """
        if as_dataframe:
            if self.procedure_function_results is None or self.procedure_function_results.statistics is None or not len(self.procedure_function_results.statistics) or self.procedure_function_results.statistics[0] is None:
                raise Exception("Statistics not found for procedure function")
            stats = self.procedure_function_results.statistics[0].toShortDict()
            stats_val = self.procedure_function_results.statistics_val[0].toShortDict() if self.procedure_function_results is not None and self.procedure_function_results.statistics_val is not None and len(self.procedure_function_results.statistics_val) and self.procedure_function_results.statistics_val[0] is not None else None
            return DataFrame([[
                stats["n"],
                stats["rmse"],
                stats["r"],
                stats["nse"],
                stats["kge"],
                stats_val["n"] if stats_val is not None else None,
                stats_val["rmse"] if stats_val is not None else None,
                stats_val["r"] if stats_val is not None else None,
                stats_val["nse"] if stats_val is not None else None,
                stats_val["kge"] if stats_val is not None else None
            ]], columns = ["n","rmse","r","nse","kge","n_val","rmse_val","r_val","nse_val","kge_val"])
        return {
            "procedure_id": self.id,
            "function_type": type(self).__name__,
            "results": [x.toShortDict() if x is not None and short else x.toDict() if x is not None else None for x in self.procedure_function_results.statistics] if self.procedure_function_results is not None and self.procedure_function_results.statistics is not None else None,
            "results_val": [x.toShortDict() if x is not None and short else x.toDict() if x is not None else None for x in self.procedure_function_results.statistics_val] if self.procedure_function_results is not None and self.procedure_function_results.statistics_val is not None else None
        }

    save_dict = StringDescriptor()
    """Save results as dict to this file"""

    def saveDict(self, output : Union[str, Path]):
        try:
            with open(output,'w') as f:
                json.dump(self.toDict(), f, indent=2)
                # logging.info("Procedure function results saved into %s" % output)
        except IOError as e:
            # logging.ERROR(f"Couldn't write to file ({e})")
            raise e
    
    def run(
        self,
        inplace : bool = True,
        save_results : Optional[Union[str,Path]] = None,
        parameters : Optional[Union[list,tuple]] = None, 
        initial_states : Optional[Union[list,tuple]] = None, 
        load_input : bool = True, 
        load_output_obs : bool = True,
        adjust : Optional[bool] = None,
        adjust_method : Optional[Literal['lfit', 'arima']] = None,
        warmup_steps : Optional[int] = None,
        tail_steps : Optional[int] = None,
        error_band : Optional[bool] = None,
        save_dict : Optional[Union[str,Path]] = None,
        drop_warmup : Optional[bool] = None
        ) -> Union[List[DataFrame], DataFrame, None]:
        """
        Run self.exec()

        Parameters:
        ----------

        inplace : bool
            If True, writes output to self.output, else returns output (array of seriesData)
        save_results : str or None
            Save procedure reuslts into this file
        parameters : list, tuple or None
            Procedure function parameters
        initial_states : list, tuple or None
            Procedure function initial states
        load_input : bool
            If True, load input using .loadInput. Else, reads from .input
        load_output_obs : bool
            If True, load observed output using .loadOutputObs. Else, reads from .output_obs
        adjust : bool = False
            Adjust results with observations by means of linear regression. Adjustment is performed after statistics computation
        warmup_steps : int = None
            For adjustment, skip this number of initial steps
        tail_steps : int = None
            For adjustment, user this number of final steps
        error_band : bool = True
            When adjusting, generate error band series from adjusted serie minus/plus linear model quant_error 95 %
        save_dict : str = None
            Save results as dict to this file
        drop_warmup : bool = None
            Eliminate warmup steps from adjusted output 
            
        Returns
        -------
        None if inplace=True, else
        list of DataFrames
        """
        save_results = save_results if save_results is not None else self.save_results
        save_dict = save_dict if save_dict is not None else self.save_dict
        adjust = adjust if adjust is not None else self.adjust
        adjust_method = adjust_method if adjust_method is not None else self.adjust_method
        warmup_steps = warmup_steps if warmup_steps is not None else self.warmup_steps
        tail_steps = tail_steps if tail_steps is not None else self.tail_steps
        error_band = util.coalesce(error_band,self.error_band,True)
        drop_warmup = drop_warmup if drop_warmup is not None else self.drop_warmup
        # loads input inplace
        if load_input:
            # logging.debug("Loading input")
            if self.pivot_input:
                input = self.loadInput(
                    inplace=inplace,
                    pivot=True,
                    use_boundary_name=True,
                    tag_column=False)
            else:
                input = self.loadInput(inplace)
        else:
            # logging.debug("Input already loaded")
            input = self.input
        # loads observed outputs
        if load_output_obs:
            # logging.debug("Loading output obs")
            output_obs = self.loadOutputObs(inplace)
        else:
            # logging.debug("Output obs already loaded")
            output_obs = self.output_obs
        # runs procedure function
        output, procedure_function_results = self.rerun(input = input, parameters = parameters, initial_states = initial_states)
        # sets procedure_function_results
        self.procedure_function_results = ProcedureFunctionResults(**procedure_function_results) if isinstance(procedure_function_results, dict) else procedure_function_results
        # sets states
        if self.procedure_function_results.states is not None:
            self.states = self.procedure_function_results.states
        # compute statistics
        if not self._no_sim:
            if inplace:
                self.output = output
                self.computeStatistics(
                    calibration_period=self.getCalibrationPeriod(),
                    result_index=self.getResultIndex())
            else:
                self.computeStatistics(
                    obs=output_obs,
                    sim=output,
                    calibration_period=self.getCalibrationPeriod(),
                    result_index=self.getResultIndex())
        else:
            if inplace:
                self.output = output
        # adjust
        if adjust:
            if self.output_obs is None:
                raise Exception("Can't adjust: missing observed outputs at procedure %s" % str(self.id))
            if self.output is None:
                raise Exception("Can't adjust: missing simulated outputs at procedure %s" % str(self.id))
            for i, o in enumerate(self.output):
                o = cast(DataFrame, o)
                if len(self.output_obs) < i + 1:
                    raise Exception("Can't adjust: missing observed output at index %i of procedure %s" % (i, str(self.id)))
                (adjusted, adjusted_tag, lm_stats) = util.adjustSeries(
                    o,
                    cast(DataFrame, self.output_obs[i]),
                    warmup = warmup_steps,
                    tail = tail_steps,
                    method = adjust_method,
                    return_df = True,
                    drop_warmup = drop_warmup)
                self.linear_model = lm_stats
                columns_drop = [ c for c in ["valor","valor_sim", "valor_obs"] if c in adjusted.columns ]
                adjusted = adjusted.drop(columns=columns_drop)
                if "adj" not in adjusted:
                    raise Exception("adj column missing in data")
                o["valor"] = adjusted["adj"] # .fillna(o["valor"])
                for col in adjusted.columns:
                    if col != "adj":
                        o[col] = adjusted[col]
                if error_band:
                    o["inferior"] = o["valor"] - self.linear_model["quant_Err"][0.950]
                    o["superior"] = o["valor"] + self.linear_model["quant_Err"][0.950]
                self.procedure_function_results.setAdjustResults(lm_stats)
        # saves results to file
        if bool(save_results):
            self.procedure_function_results.save(output=save_results)
        if bool(save_dict):
            self.saveDict(output=save_dict)
        # returns
        if inplace:
            return
        else:
            return output
    def getOutputNodeData(
        self,
        node_id : int,
        var_id : int,
        tag=None
        ) -> DataFrame:
        """
        Extracts single series from output using node id and variable id

        Parameters:
        ----------

        node_id : int
            Node identifier. Must be present in self.plan.topology.nodes
        var_id : int
            Variable identifier. Must be present in the selected node of self.plan.topology.nodes
        
        Returns
        ----------
        timeseries dataframe : DataFrame
        """
        index = 0
        for o in self.outputs:
            if o.var_id == var_id and o.node_id == node_id:
                if self.output is not None:
                    if isinstance(self.output,DataFrame):
                        return self.output
                    else:
                        if len(self.output) <= index + 1:
                            return self.output[index]
            index = index + 1
        raise Exception("Procedure.getOutputNodeData error: node with id: %s , var %i not found in output" % (str(node_id), var_id))

    def outputToNodes(
        self,
        overwrite : Optional[bool] = None,
        overwrite_original : Optional[bool] = None
        ) -> None:
        """Saves procedure output into the topology. Each element of self.output is concatenated into the .data property of the corresponding NodeVariable in self.plan.topology.nodes according the mapping defined in self.outputs. 
        
        Parameters:
        ----------

        overwrite : bool
            Overwrite observations in NodeVariable.data
        overwrite_original : bool
            Overwrite observations in NodeVariable.original_data
        """
        overwrite = overwrite if overwrite is not None else self.overwrite
        overwrite_original = overwrite_original if overwrite_original is not None else self.overwrite_original
        if self.output is None:
            logging.error("Procedure output is None, which means the procedure wasn't run yet. Can't perform outputToNodes.")
            return
        # output_columns = self.output.columns
        index = 0
        for o in self.outputs:
            if o._variable is None:
                raise Exception("variable is not set")
            if o._variable.series_sim is None:
                # logging.warning("series_sim not defined for output %s" % o.name)
                continue
            if index + 1 > len(self.output):
                logging.error("Procedure output for node %s variable %i not found in self.output. Skipping" % (str(o.node_id),o.var_id))
                continue
            if o.node is None:
                raise RuntimeError("node not set")
            output_data = self.setIndexOfDataFrame(self.output if isinstance(self.output, DataFrame) else self.output[index],time_interval = util.decimal_days_to_relativedelta(o.node.time_interval) if isinstance(o.node.time_interval,int) else o.node.time_interval)
            o._variable.concatenate(output_data,overwrite=overwrite,extend=True)
            if overwrite_original:
                data = self.output if isinstance(self.output, DataFrame) else self.output[index]
                if not isinstance(data, DataFrame):
                    raise RuntimeError("output item is not DataFrame")
                o._variable.concatenateOriginal(data,overwrite=overwrite_original)
            for serie in o._variable.series_sim:
                # logging.debug("output serie %i, data: %s" % (index, str(self.output[index])))
                serie.setData(data=self.output[index]) # self.getOutputNodeData(o.node_id,o.var_id))
                serie.applyOffset()
                # serie.metadata = {
                #     "procedure_id": self.id
                # }
            index = index + 1
    
    def setIndexOfDataFrame(
        self,
        data : DataFrame,
        time_interval : relativedelta,
    ) -> DataFrame:
        """Set index of data frame from topology begin and end dates and time_interval"""
        if self._plan is None:
            raise Exception("Plan is not set")
        data = util.serieRegular(
            data = data,
            time_interval  = time_interval if time_interval is not None else util.decimal_days_to_relativedelta(self._plan.time_interval) if isinstance(self._plan.time_interval,int) else self._plan.time_interval,
            timestart = self._plan.topology.timestart,
            timeend = self._plan.topology.forecast_timeend if self._plan.topology.forecast_timeend is not None else self._plan.topology.timeend,
            time_offset = self._plan.topology.time_offset_start,
            interpolation_limit=0,
            interpolate=False,
            tag_column = "tag" if "tag" in data else None)
        return data
    def testPlot(
        self,
        index : int = 0
        ) -> None:
        """Plot observed and simulated variable vs. time in the same chart.
        
        Parameters:
        ----------

        index : int (default 0)
            Which element of self.output to plot 
        """
        if self.output is None:
            raise Exception("Procedure output has not been generated. Execute run()")
        if self.output_obs is None:
            raise Exception("Procedure input has not been generated. Execute loadInput()")
        if index > len(self.output) - 1:
            raise IndexError("testPlot index out of range at procedure %s " % str(self.id))
        testPlot(self.output[index]["valor"].tolist(),self.output_obs[index]["valor"].tolist())
    
    def pivotInOut(self) -> Optional[DataFrame]:
        df = None
        if self.input is None:
            raise Exception("Input is not set")
        if isinstance(self.input, DataFrame):
            df = self.input.copy()
        else:
            for i, boundary in enumerate(self.boundaries):
                data_renamed = self.input[i][["valor"]].rename(columns={"valor":boundary.name})
                if df is None:
                    df = data_renamed
                else:
                    df = df.join(data_renamed)
        for i, boundary in enumerate(self.outputs):
            if self.output is None:
                raise Exception("output is not set")
            df_sim = self.output if isinstance(self.output,DataFrame) else self.output[i]
            data_renamed = df_sim[["valor"]].rename(mapper={"valor":boundary.name}, axis=1)
            if self.output_obs is None:
                raise Exception("output_obs is not set")
            df_obs = self.output_obs if isinstance(self.output_obs,DataFrame) else self.output_obs[i]
            data_obs_renamed = df_obs[["valor"]].rename(mapper={"valor":"%s_obs" % boundary.name}, axis=1)
            if df is None:
                df = data_renamed
            else:
                df = df.join(data_renamed)
                df = df.join(data_obs_renamed)
        return df
    
    def calibrate(
        self,
        inplace : bool = True
        ) -> Union[tuple, None]:
        """Run Nelder-Mead Downhill Simplex calibration procedure. Calibration configuration is read from self.calibration (set at class instantiation)
        
        Parameters:
        ----------

        inplace : bool
            If true, set resulting parameters in self.parameters. Else, returns resulting parameters 
        
        Returns
        -------
        if inplace = True
            None
        else:
            Tuple where first element is the list of resulting parameters and the second is the resulting objective function

        """
        if self.calibration is None:
            raise Exception("Calibration is not set")
        calibration_result = self.calibration.run(inplace=inplace)
        if inplace:
            # updates params
            if self.calibration.calibration_result is None:
                raise RuntimeError("calibration_result not set")
            self.setParameters(self.calibration.calibration_result[0])
            # runs procedure
            self.run(load_input=False, load_output_obs=False)
        else:
            return calibration_result
    
    def batchProcessInput(self, **kwargs):
        for boundary in self.boundaries:
            if isinstance(boundary.variable,ObservedNodeVariable):
                boundary.variable.batchProcessInput(**kwargs)
        for boundary in self.outputs:
            if isinstance(boundary.variable,ObservedNodeVariable):
                boundary.variable.batchProcessInput(**kwargs)

    ################ moved from procedure function ##################

    def setParameters(
        self,
        parameters : Union[List,Tuple] = [],
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
            if not isinstance(self.parameters, dict):
                raise RuntimeError("parameters must be a dict")
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

    def rerun(
        self,
        input : Optional[Union[DataFrame,List[DataFrame]]] = None,
        parameters : Optional[Union[list,tuple]] = None, 
        initial_states : Optional[Union[list,tuple]] = None
        ) -> Tuple[Union[DataFrame,List[DataFrame]], ProcedureFunctionResults]:
        """Execute the procedure with the given parameters and initial_states
        
        Parameters:
        -----------
        input : list if DataFrames
            Procedure input (boundary conditions). If None, loads using .loadInput()
        
        parameters : list or tuple
            Set procedure parameters (self.parameters).
        
        initial_states : list or tuple
            Set initial states (self.initial_states)
        
        Returns:
        --------
        2-tuple : first element is the procedure output (list of DataFrames), while second is a ProcedureFunctionResults object"""
        if parameters is not None:
            self.setParameters(parameters)
        if initial_states is not None:
            self.setInitialStates(initial_states)
        return self.exec(input)

    def exec(
        self,
        input : Optional[Union[List[DataFrame],DataFrame]] = None
        ) -> Tuple[Union[DataFrame,List[DataFrame]], ProcedureFunctionResults]:
        """
        Placeholder procedure execution. To be overwritten in subclasses

        Parameters:
        -----------
        input : list of DataFrames
            Procedure function input (boundary conditions). If None, loads using .loadInput()

        Returns:
        --------
        2-tuple : first element is the procedure function output (list of DataFrames), while second is a ProcedureFunctionResults object
        """
        input = self.loadInput(inplace=False)
        # data = self._plan.topology.pivotData(nodes=self.output_nodes,include_tag=False,use_output_series_id=False,use_node_id=True)
        return input, ProcedureFunctionResults()

    def makeSimplex(
        self,
        sigma : float = 0.25,
        limit : bool = True,
        ranges : Optional[list] = None,
        # minmax : Optional[list] = None
        ) -> List[List[float]]:
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
        points : List[List[float]] = []
        for i in range(len(self._parameters)+1):
            point : List[float] = []
            for j, p in enumerate(self._parameters):
                if ranges is not None and len(ranges) - 1 >= j:
                    if len(ranges[j]) < 2:
                        raise ValueError("ranges must be a list of 2-tuples")
                    range_min = ranges[j][0]
                    range_max = ranges[j][1]
                else:
                    range_min = None
                    range_max = None
                # if minmax is not None and len(minmax) - 1 >= j:
                #     if len(minmax[j]) < 2:
                #         raise ValueError("minmax must be a list of 2-tuples")
                #     abs_min = minmax[j][0]
                #     abs_max = minmax[j][1]
                # else:
                #     abs_min = None
                #     abs_max = None
                point.append(p.makeRandom(sigma=sigma, limit=limit, range_min=range_min, range_max=range_max)) # , abs_min=abs_min,abs_max=abs_max)
            points.append(list(point))
        return points
    
    def extractListsFromInput(self, input : List[DataFrame], allow_na : List[bool]=[False]) -> List[List[float]]:
        while len(allow_na) < len(input):
            allow_na.append(False)
        return [ getInputListFromDataFrame(df,allow_na[i], self.id) for i, df in enumerate(input) ]
    
    def pivotInputOutput(
            self, 
            input : List[DataFrame], 
            output : List[DataFrame] = [], 
            other : Optional[dict] = None) -> DataFrame:
        if not len(input):
            raise ValueError("input must be of length 1 or greater")
        result = input[0][["valor"]].rename(columns={"valor": self._boundaries[0].name})
        for i in range(1,len(self._boundaries)):
            if self._boundaries[i].optional and len(input) < i + 1:
                continue
            result = result.join(input[i][["valor"]].rename(columns={"valor": self._boundaries[i].name}))
        for i in range(0,len(self._outputs)):
            if self._outputs[i].optional and len(output) < i + 1:
                continue
            if type(output[i]) == DataFrame:
                result = result.join(output[i][["valor"]].rename(columns={"valor": self._outputs[i].name}))
            else:
                result[self._outputs[i].name] = output[i]
        if other is not None:
            # must be a a dict where key is the column name and value is the list of values
            for name, values in other.items():
                result[name] = values
        return result
    
    def tvpListToBoundaryDict(
            self, 
            b : Union[TVPList,DataFrame], 
            index : int=0, 
            is_output : bool=False
            ) -> ProcedureBoundaryDict:
        if is_output:
            if index + 1 > len(self._outputs):
                if not self._additional_outputs:
                    raise ValueError("Invalid index for output. Index exceeds procedure outputs length and additional outputs are not allowed")
                name = f"output_{index - 1}"
            else:
                name = self._outputs[index].name
        else:
            if index + 1 > len(self._boundaries):
                if not self._additional_boundaries:
                    raise ValueError("Invalid index for boundary. Index exceeds procedure boundaries length and additional boundaries are not allowed")
                name = f"input_{index - 1}"
            else:
                name = self._boundaries[index].name
        if isinstance(b, DataFrame):
            data = b
        else:
            data = tvpListToDataFrame(b)
        return {
            "name": name,
            "node_variable": (0,0),
            "data": data
        }
    
    def dfToBoundaryDicts(self, df : DataFrame) -> List[ProcedureBoundaryDict]:
        # each column into a ProcedureBoundaryDict using column names
        return [
            {
                "name": col,
                "node_variable": (0,0),
                "data": df[[col]]
            }
            for col in df.columns
        ] 

    
# from pydrodelta.procedures.hecras import HecRasProcedureFunction
# from pydrodelta.procedures.polynomial import PolynomialTransformationProcedureFunction
# from pydrodelta.procedures.muskingumchannel import MuskingumChannelProcedureFunction
# from pydrodelta.procedures.grp import GRPProcedureFunction
# from pydrodelta.procedures.linear_combination import LinearCombinationProcedureFunction
# from pydrodelta.procedures.expression import ExpressionProcedureFunction
# from pydrodelta.procedures.sacramento_simplified import SacramentoSimplifiedProcedureFunction
# from pydrodelta.procedures.sacramento_simplified_fixed_pars import SacramentoSimplifiedFixedParsProcedureFunction
# from pydrodelta.procedures.sac_enkf import SacEnkfProcedureFunction
# from pydrodelta.procedures.junction import JunctionProcedureFunction
# from pydrodelta.procedures.linear_channel import LinearChannelProcedureFunction
# from pydrodelta.procedures.uh_linear_channel import UHLinearChannelProcedureFunction
# from pydrodelta.procedures.gr4j_ import GR4JProcedureFunction as GR4J_ProcedureFunction
# from pydrodelta.procedures.gr4j import GR4JProcedureFunction
# from pydrodelta.procedures.linear_combination_2b import LinearCombination2BProcedureFunction
# from pydrodelta.procedures.linear_combination_3b import LinearCombination3BProcedureFunction
# from pydrodelta.procedures.linear_combination_4b import LinearCombination4BProcedureFunction
# from pydrodelta.procedures.hosh4p1l import HOSH4P1LProcedureFunction
# from pydrodelta.procedures.hosh4p1lnash import HOSH4P1LNashProcedureFunction
# from pydrodelta.procedures.hosh4p1luh import HOSH4P1LUHProcedureFunction
# from pydrodelta.procedures.difference import DifferenceProcedureFunction
# from pydrodelta.procedures.linear_net import LinearNetProcedureFunction
# from pydrodelta.procedures.linear_net_3 import LinearNet3ProcedureFunction
# from pydrodelta.procedures.exponential_fit import ExponentialFitProcedureFunction
# from pydrodelta.procedures.linear_fit import LinearFitProcedureFunction
# from pydrodelta.procedures.abstract import AbstractProcedureFunction
# from pydrodelta.procedures.lag_and_route import LagAndRouteProcedureFunction
# from pydrodelta.procedures.hidrosat import HIDROSATProcedureFunction
# from pydrodelta.procedures.analogy import AnalogyProcedureFunction
# from pydrodelta.procedures.persistence import PersistenceProcedureFunction
# from pydrodelta.procedures.lag_and_route_net import LagAndRouteNetProcedureFunction

# procedureFunctionDict = {
#     # "ProcedureFunction": ProcedureFunction,
#     "AbstractProcedureFunction": AbstractProcedureFunction,
#     "HecRas": HecRasProcedureFunction,
#     "HecRasProcedureFunction": HecRasProcedureFunction,
#     "PolynomialTransformationProcedureFunction": PolynomialTransformationProcedureFunction,
#     "Polynomial": PolynomialTransformationProcedureFunction,
#     "MuskingumChannel": MuskingumChannelProcedureFunction,
#     "MuskingumChannelProcedureFunction": MuskingumChannelProcedureFunction,
#     "GRP": GRPProcedureFunction,
#     "GRPProcedureFunction": GRPProcedureFunction,
#     "LinearCombination": LinearCombinationProcedureFunction,
#     "LinearCombination2B": LinearCombination2BProcedureFunction,
#     "LinearCombination3B": LinearCombination3BProcedureFunction,
#     "LinearCombination4B": LinearCombination4BProcedureFunction,
#     "Expression": ExpressionProcedureFunction,
#     "SacramentoSimplified": SacramentoSimplifiedProcedureFunction,
#     "SacramentoSimplifiedFixedPars": SacramentoSimplifiedFixedParsProcedureFunction,
#     "SacEnKF": SacEnkfProcedureFunction,
#     "Junction": JunctionProcedureFunction,
#     "LinearChannel": LinearChannelProcedureFunction,
#     "UHLinearChannel": UHLinearChannelProcedureFunction,
#     "GR4J": GR4JProcedureFunction,
#     "GR4J_": GR4J_ProcedureFunction,
#     "HOSH4P1L": HOSH4P1LProcedureFunction,
#     "HOSH4P1LNash": HOSH4P1LNashProcedureFunction,
#     "HOSH4P1LUH": HOSH4P1LUHProcedureFunction,
#     "Difference": DifferenceProcedureFunction,
#     "LinearNet": LinearNetProcedureFunction,
#     "LinearNet3": LinearNet3ProcedureFunction,
#     "ExponentialFit": ExponentialFitProcedureFunction,
#     "LinearFit": LinearFitProcedureFunction,
#     "LagAndRoute": LagAndRouteProcedureFunction,
#     "LagAndRouteNet": LagAndRouteNetProcedureFunction,
#     "HIDROSAT": HIDROSATProcedureFunction,
#     "Analogy": AnalogyProcedureFunction,
#     "Persistence": PersistenceProcedureFunction
# }
