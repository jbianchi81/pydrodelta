from .procedure_function import ProcedureFunction
import logging
import json
from . import util
from .a5 import createEmptyObsDataFrame
from .result_statistics import ResultStatistics
from .procedure_function_results import ProcedureFunctionResults
from .pydrology import testPlot
from .calibration.downhill_simplex_calibration import DownhillSimplexCalibration
from .calibration.linear_regression_calibration import LinearRegressionCalibration
from typing import Optional, Union, List, Tuple
from datetime import timedelta
from pandas import DataFrame
from .descriptors.int_descriptor import IntDescriptor
from .descriptors.bool_descriptor import BoolDescriptor
from .descriptors.bool_or_none_descriptor import BoolOrNoneDescriptor
from .descriptors.dict_descriptor import DictDescriptor

class Procedure():
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

    overwrite : bool
        When exporting procedure results into the topology, overwrite observations in NodeVariable.data   

    overwrite_original : bool
        When exporting procedure results into the topology, overwrite observations in NodeVariable.original_data

    calibration : dict
        Configuration for calibration procedure (see Calibration)

    """

    _available_calibration_methods : dict = {
        "downhill-simplex": DownhillSimplexCalibration,
        "linear-regression": LinearRegressionCalibration
    }

    @property
    def calibration(self) -> Union[DownhillSimplexCalibration, LinearRegressionCalibration]:
        return self._calibration
    @calibration.setter
    def calibration(self,calibration : dict) -> None:
        if calibration is not None:
            if "method" not in calibration:
                raise KeyError("Required key 'method' missing from calibration argument")
            if calibration["method"] not in self._available_calibration_methods:
                raise ValueError("Calibration method '%s' not defined" % calibration["method"])
            kwargs = calibration.copy()
            del kwargs["method"]
            self._calibration = self._available_calibration_methods[calibration["method"]](procedure=self, **kwargs)
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

    def __init__(
        self,
        id : Union[int, str],
        function : dict,
        plan = None,
        initial_states : list = [],
        parameters : list = [],
        time_interval : Union[str,dict] = None,
        time_offset : Union[str,dict] = None,
        save_results : str = None,
        overwrite : bool = False,
        overwrite_original : bool = False,
        calibration : dict = None,
        adjust : bool = False,
        warmup_steps : int = None,
        tail_steps : int = None,
        error_band : bool = None
        ):
        self.id : Union[int,str] = id
        """Identifier of the procedure"""
        self._plan = plan
        """Plan containing this procedure"""
        self.initial_states : list = initial_states
        """List of procedure initial states"""
        if type(function) != dict:
            if type(function) != str:
                raise TypeError("Value of argument 'function' must be of type dict or str")
            function_file = function
            try:
                f = open(function_file)
            except IOError as e:
                raise IOError("Couldn´t open function file %s: %s" % (function_file, str(e)))
            try:
                function = json.load(f)
            except json.JSONDecodeError as e:
                raise json.JSONDecodeError("JSON decode error on parsing function file %s: %s" % (function_file, e.msg))
            f.close()
        if "type" not in function:
            raise ValueError("Property 'type' missing from argument 'function'")
        if function["type"] in procedureFunctionDict:
            self.function_type : type = procedureFunctionDict[function["type"]]
            """Class constructor of the procedure function"""
            self.function_type_name : str = function["type"]
            """Name of the class constructor of the procedure function"""
        else:
            raise ValueError("Procedure init: procedure function class constructor %s not found" % function["type"])
            # self.function_type = ProcedureFunction
            # self.function_type_name = "ProcedureFunction"
        self.function : ProcedureFunction = self.function_type(**function,procedure=self)
        """ProcedureFunction object (or a subclass) containing the .run() method, the .boundaries list and the .outputs list"""
        # self.procedure_type = params["procedure_type"]
        self.parameters : list = parameters
        """List of procedure parameters"""
        self.time_interval : timedelta = util.interval2timedelta(time_interval) if time_interval is not None else None
        """Time step duration of the procedure"""
        self.time_offset : timedelta = util.interval2timedelta(time_offset) if time_offset is not None else None
        """Time offset duration of the procedure"""
        self.input : List[DataFrame] = None # <- boundary conditions
        """Ordered list of input DataFrames of the procedure (the boundary conditions). Run .loadInput(inplace=True) to populate"""
        self.output : List[DataFrame] = None # <- outputs
        """Ordered list of output DataFrames of the procedure. Run .run(inplace=True) to populate"""
        self.output_obs : List[DataFrame] = None # <- observed values for error calculation
        """List of DataFrames of observed values for error calculation. Same order than .output. Run .loadOutputObs(inplace=True) to populate"""
        self.states : DataFrame = None
        """Pivot DataFrame of procedure states. Byproduct of .run(inplace=True) execution"""
        self.procedure_function_results : ProcedureFunctionResults = None
        """Results of the procedure function execution"""
        self.save_results : str = save_results
        """Save procedure results into this file (csv pivoted table)"""
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
            'function_type_name': self.function_type_name, 
            'function': self.function.toDict(),
            'parameters': self.parameters, 
            'time_interval': self.time_interval, 
            'time_offset': self.time_offset, 
            'input': [x.to_dict(orient="records") if isinstance(x, DataFrame) else x for x in self.input] if self.input is not None else None, 
            'output': [x.to_dict(orient="records") if isinstance(x, DataFrame) else x  for x in self.output] if self.output is not None else None, 
            'output_obs': [x.to_dict(orient="records")  if isinstance(x, DataFrame) else x for x in self.output_obs] if self.output_obs is not None else None, 
            'states': self.states.to_dict(orient="records") if isinstance(self.states,DataFrame) else self.states,
            'procedure_function_results': self.procedure_function_results.toDict() if self.procedure_function_results is not None else None, 
            'save_results': self.save_results, 
            'overwrite': self.overwrite, 
            'overwrite_original': self.overwrite_original, 
            'calibration': self.calibration.toDict() if self.calibration is not None else None
        }

    def loadInputDefault(self) -> None:
        """Loads input with default behaviour according to the procedure function"""
        if self.function.pivot_input:
            self.loadInput(
                inplace = True,
                pivot = True,
                use_boundary_name = True,
                tag_column = False
            )
        else:
            self.loadInput()

    def loadInput(
        self,
        inplace : bool = True,
        pivot : bool = False,
        use_boundary_name : bool = False,
        tag_column : bool = True
        ) -> Union[List[DataFrame],DataFrame]:
        """
        Loads the boundary variables defined in self.function.boundaries. Takes .data from each element of self.function.boundaries and returns a list. If pivot=True, joins all variables into a single DataFrame

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
        """
        if pivot:
            data = createEmptyObsDataFrame(extra_columns={"tag":str}) if tag_column else createEmptyObsDataFrame()
            columns = ["valor","tag"] if tag_column else ["valor"] 
            for boundary in self.function.boundaries:
                if boundary._variable.data is not None and len(boundary._variable.data):

                    if use_boundary_name:
                        data = data.join(
                            boundary._variable.data[columns][boundary._variable.data.valor.notnull()].rename(
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
                            boundary._variable.data[columns][boundary._variable.data.valor.notnull()],
                            how='outer',
                            rsuffix=rsuffix,
                            sort=True)
            for column in columns:
                del data[column]
            # data = data.replace({np.NaN:None})
        else:
            data = []
            for boundary in self.function.boundaries:
                logging.debug("loading boundary: %s: node %i, variable %i, optional: %s, warmup_only: %s" % (boundary.name, boundary.node_id,boundary.var_id, str(boundary.optional), str(boundary.warmup_only)))
                if not boundary.optional:
                    try:
                        warmup_only = boundary.warmup_only if boundary.warmup_only else False
                        boundary.assertNoNaN(warmup_only)
                    except AssertionError as e:
                        raise Exception("load input error at procedure %s, node %i, variable, %i: %s" % (self.id, boundary.node_id, boundary.var_id, str(e)))
                data.append(boundary._variable.data.copy())
        if inplace:
            self.input = data
        else:
            return data
    def loadOutputObs(
        self,
        inplace : bool = True,
        pivot : bool = False
        ):
        """
        Load observed values of output variables defined in self.function.outputs. Used in error calculation.

        Parameters:
        -----------

        inplace : bool
            If True, saves result into self.output_obs and returns None
        
        pivot: bool
            If true, joins all variables into a single DataFrame
        """
        if pivot:
            data = createEmptyObsDataFrame()
            for i, output in enumerate(self.function.outputs):
                if output._variable.data is not None and len(output._variable.data):
                    colname = "valor_%i" % (i + 1) 
                    data = data.join(output._variable.data[["valor"]].rename(columns={"valor": colname}).dropna(),how='outer',sort=True)
                else:
                    logging.warn("loadOutputObs: Procedure: %s, output: %i, with no data. Skipped." % (self.id,i))
            # logging.debug("loadOutputObs: columns: %s" % (data.columns))
            if "valor" in data.columns:
                data.drop(columns="valor",inplace=True)
        else:
            data = []
            for output in self.function.outputs:
                data.append(output._variable.data[["valor"]].dropna())
        if inplace:
            self.output_obs = data
        else:
            return data
    def computeStatistics(
        self, 
        obs : Optional[list] = None, 
        sim : Optional[list] = None,
        calibration_period : Optional[tuple]=None,
        result_index : int = 0
        ) -> Tuple[List[ResultStatistics]]:
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
        obs = obs if obs is not None else self.output_obs
        sim = sim if sim is not None else self.output
        result = list()
        result_val = list()
        # if len(obs) < len(sim):
        #     raise Exception("length of obs must be equal than length of sim")
        for i, o in enumerate(self.function.outputs):
            if len(sim) < i + 1:
                raise Exception("List of sim outputs is shorter than function.outputs (%i < %i" % (len(sim), len(self.function.outputs)))
            if len(obs) < i + 1:
                raise Exception("List of obs outputs is smaller than function.outputs (%i < %i" % (len(obs), len(self.function.outputs)))
            inner_join = sim[i][["valor"]].rename(columns={"valor":"sim"}).join(obs[i][["valor"]].rename(columns={"valor":"obs"}),how="inner").dropna()
            if calibration_period is not None:
                inner_join_cal, inner_join_val = util.groupByCalibrationPeriod(inner_join,calibration_period)
                if i == result_index and (inner_join_cal is None or not len(inner_join_cal)):
                    raise Exception("Invalid calibration period: no data found")
                result.append(ResultStatistics(
                    obs = inner_join_cal["obs"].values if inner_join_cal is not None else [], 
                    sim = inner_join_cal["sim"].values if inner_join_cal is not None else [], 
                    compute = o.compute_statistics, 
                    metadata = o.toDict(),
                    calibration_period = calibration_period,
                    group = "cal"
                ))
                if inner_join_val is not None and len(inner_join_val):
                    result_val.append(ResultStatistics(
                        obs = inner_join_val["obs"].values, 
                        sim = inner_join_val["sim"].values, 
                        compute = o.compute_statistics, 
                        metadata = o.toDict(),
                        calibration_period = calibration_period,
                        group = "val"
                    ))
                else:
                    logging.warn("No data found for validation")
            else:
                result.append(ResultStatistics(
                    obs = inner_join["obs"].values, 
                    sim = inner_join["sim"].values, 
                    compute = o.compute_statistics, 
                    metadata = o.toDict()
                ))
        if self.procedure_function_results is not None:
            self.procedure_function_results.setStatistics(result)
            if len(result_val):
                self.procedure_function_results.setStatisticsVal(result_val)
        return result, result_val
    
    def read_statistics(
        self, 
        short : bool = False,
        as_dataframe = False
        ) -> dict:
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
            if not len(self.procedure_function_results.statistics) or self.procedure_function_results.statistics[0] is None:
                raise Exception("Statistics not found for procedure function")
            stats = self.procedure_function_results.statistics[0].toShortDict()
            stats_val = self.procedure_function_results.statistics_val[0].toShortDict() if len(self.procedure_function_results.statistics_val) and self.procedure_function_results.statistics_val[0] is not None else None
            return DataFrame([[
                stats["n"],
                stats["rmse"],
                stats["r"],
                stats["nse"],
                stats_val["n"] if stats_val is not None else None,
                stats_val["rmse"] if stats_val is not None else None,
                stats_val["r"] if stats_val is not None else None,
                stats_val["nse"] if stats_val is not None else None
            ]], columns = ["n","rmse","r","nse","n_val","rmse_val","r_val","nse_val"])
        return {
            "procedure_id": self.id,
            "function_type": self.function_type_name,
            "results": [x.toShortDict() if x is not None and short else x.toDict() if x is not None else None for x in self.procedure_function_results.statistics] if self.procedure_function_results.statistics is not None else None,
            "results_val": [x.toShortDict() if x is not None and short else x.toDict() if x is not None else None for x in self.procedure_function_results.statistics_val] if self.procedure_function_results.statistics_val is not None else None
        }
    def read_results(self) -> dict:
        """Get results as a dict
        
        Returns
        -------
        results : dict of the form:
            {
                "procedure_id": int,
                "function_type": str,
                "results": dict    
            }
        """
        return {
            "procedure_id": self.id,
            "function_type": self.function_type_name,
            "results": self.procedure_function_results.toDict() if self.procedure_function_results is not None else None
        }
    def run(
        self,
        inplace : bool = True,
        save_results : Optional[str] = None,
        parameters : Union[list,tuple] = None, 
        initial_states : Union[list,tuple] = None, 
        load_input : bool = True, 
        load_output_obs : bool = True,
        adjust : bool = None,
        warmup_steps : int = None,
        tail_steps : int = None,
        error_band : bool = None
        ) -> Union[List[DataFrame], None]:
        """
        Run self.function.run()

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
            
        Returns
        -------
        None if inplace=True, else
        list of DataFrames
        """
        save_results = save_results if save_results is not None else self.save_results
        adjust = adjust if adjust is not None else self.adjust
        warmup_steps = warmup_steps if warmup_steps is not None else self.warmup_steps
        tail_steps = tail_steps if tail_steps is not None else self.tail_steps
        error_band = util.coalesce(error_band,self.error_band,True)
        # loads input inplace
        if load_input:
            # logging.debug("Loading input")
            if self.function.pivot_input:
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
        output, procedure_function_results = self.function.rerun(input = input, parameters = parameters, initial_states = initial_states)
        # sets procedure_function_results
        self.procedure_function_results = ProcedureFunctionResults(**procedure_function_results) if isinstance(procedure_function_results, dict) else procedure_function_results
        # sets states
        if self.procedure_function_results.states is not None:
            self.states = self.procedure_function_results.states
        # compute statistics
        if not self.function._no_sim:
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
            for i, o in enumerate(self.output):
                if len(self.output_obs) < i + 1:
                    raise Exception("Can't adjust: missing observed output at index %i of procedure %s" % (i, str(self.id)))
                (adjusted, adjusted_tag, lm_stats) = util.adjustSeries(
                    o,
                    self.output_obs[i],
                    warmup = self.warmup_steps,
                    tail = self.tail_steps)
                self.linear_model = lm_stats
                o["valor"] = adjusted
                if error_band:
                    o["inferior"] = adjusted - self.linear_model["quant_Err"][0.950]
                    o["superior"] = adjusted + self.linear_model["quant_Err"][0.950]
        # saves results to file
        if bool(save_results):
            self.procedure_function_results.save(output=save_results)
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
        ) -> None:
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
                if self.output is not None and len(self.output) <= index + 1:
                    return self.output[index]
            index = index + 1
        raise("Procedure.getOutputNodeData error: node with id: %s , var %i not found in output" % (str(node_id), var_id))
        # col_rename = {}
        # col_rename[node_id] = "valor"
        # data = self.output[[node_id]].rename(columns = col_rename)
        # if tag is not None:
        #     data["tag"] = tag
        # return data
    def outputToNodes(
        self,
        overwrite : bool = None,
        overwrite_original : bool = None
        ) -> None:
        """Saves procedure output into the topology. Each element of self.output is concatenated into the .data property of the corresponding NodeVariable in self.plan.topology.nodes according the mapping defined in self.function.outputs. 
        
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
        for o in self.function.outputs:
            if o._variable.series_sim is None:
                logging.warn("series_sim not defined for output %s" % o.name)
                continue
            if index + 1 > len(self.output):
                logging.error("Procedure output for node %s variable %i not found in self.output. Skipping" % (str(o.node_id),o.var_id))
                continue
            output_data = self.setIndexOfDataFrame(self.output[index],time_interval = o.node.time_interval)
            o._variable.concatenate(output_data,overwrite=overwrite,extend=False)
            if overwrite_original:
                o._variable.concatenateOriginal(self.output[index],overwrite=overwrite_original)
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
        time_interval : timedelta,
    ) -> DataFrame:
        """Set index of data frame from topology begin and end dates and time_interval"""
        data = util.serieRegular(
            data = data,
            time_interval  = time_interval if time_interval is not None else self._plan.time_interval,
            timestart = self._plan.topology.timestart,
            timeend = self._plan.topology.forecast_timeend if self._plan.topology.forecast_timeend is not None else self._plan.topology.timeend,
            time_offset = self._plan.topology.time_offset_start,
            interpolation_limit=0,
            interpolate=False)
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
        testPlot(self.output[index]["valor"],self.output_obs[index]["valor"])
    def calibrate(
        self,
        inplace : bool = True
        ) -> Union[tuple, None]:
        """Run Nelder-Mead Downhill Simplex calibration procedure. Calibration configuration is read from self.calibration (set at class instantiation)
        
        Parameters:
        ----------

        inplace : bool
            If true, set resulting parameters in self.function.parameters. Else, returns resulting parameters 
        
        Returns
        -------
        if inplace = True
            None
        else:
            Tuple where first element is the list of resulting parameters and the second is the resulting objective function

        """
        calibration_result = self.calibration.run(inplace=inplace)
        if inplace:
            # updates params
            self.function.setParameters(self.calibration.calibration_result[0])
            # runs procedure
            self.run(load_input=False, load_output_obs=False)
        else:
            return calibration_result
    
from pydrodelta.procedures.hecras import HecRasProcedureFunction
from pydrodelta.procedures.polynomial import PolynomialTransformationProcedureFunction
from pydrodelta.procedures.muskingumchannel import MuskingumChannelProcedureFunction
from pydrodelta.procedures.grp import GRPProcedureFunction
from pydrodelta.procedures.linear_combination import LinearCombinationProcedureFunction
from pydrodelta.procedures.expression import ExpressionProcedureFunction
from pydrodelta.procedures.sacramento_simplified import SacramentoSimplifiedProcedureFunction
from pydrodelta.procedures.sac_enkf import SacEnkfProcedureFunction
from pydrodelta.procedures.junction import JunctionProcedureFunction
from pydrodelta.procedures.linear_channel import LinearChannelProcedureFunction
from pydrodelta.procedures.uh_linear_channel import UHLinearChannelProcedureFunction
from pydrodelta.procedures.gr4j_ import GR4JProcedureFunction as GR4J_ProcedureFunction
from pydrodelta.procedures.gr4j import GR4JProcedureFunction
from pydrodelta.procedures.linear_combination_2b import LinearCombination2BProcedureFunction
from pydrodelta.procedures.linear_combination_3b import LinearCombination3BProcedureFunction
from pydrodelta.procedures.linear_combination_4b import LinearCombination4BProcedureFunction
from pydrodelta.procedures.hosh4p1l import HOSH4P1LProcedureFunction
from pydrodelta.procedures.hosh4p1lnash import HOSH4P1LNashProcedureFunction
from pydrodelta.procedures.hosh4p1luh import HOSH4P1LUHProcedureFunction
from pydrodelta.procedures.difference import DifferenceProcedureFunction
from pydrodelta.procedures.linear_net_3 import LinearNet3ProcedureFunction
from pydrodelta.procedures.exponential_fit import ExponentialFitProcedureFunction
from pydrodelta.procedures.linear_fit import LinearFitProcedureFunction

procedureFunctionDict = {
    "ProcedureFunction": ProcedureFunction,
    "HecRas": HecRasProcedureFunction,
    "HecRasProcedureFunction": HecRasProcedureFunction,
    "PolynomialTransformationProcedureFunction": PolynomialTransformationProcedureFunction,
    "Polynomial": PolynomialTransformationProcedureFunction,
    "MuskingumChannel": MuskingumChannelProcedureFunction,
    "MuskingumChannelProcedureFunction": MuskingumChannelProcedureFunction,
    "GRP": GRPProcedureFunction,
    "GRPProcedureFunction": GRPProcedureFunction,
    "LinearCombination": LinearCombinationProcedureFunction,
    "LinearCombination2B": LinearCombination2BProcedureFunction,
    "LinearCombination3B": LinearCombination3BProcedureFunction,
    "LinearCombination4B": LinearCombination4BProcedureFunction,
    "Expression": ExpressionProcedureFunction,
    "SacramentoSimplified": SacramentoSimplifiedProcedureFunction,
    "SacEnKF": SacEnkfProcedureFunction,
    "Junction": JunctionProcedureFunction,
    "LinearChannel": LinearChannelProcedureFunction,
    "UHLinearChannel": UHLinearChannelProcedureFunction,
    "GR4J": GR4JProcedureFunction,
    "GR4J_": GR4J_ProcedureFunction,
    "HOSH4P1L": HOSH4P1LProcedureFunction,
    "HOSH4P1LNash": HOSH4P1LNashProcedureFunction,
    "HOSH4P1LUH": HOSH4P1LUHProcedureFunction,
    "Difference": DifferenceProcedureFunction,
    "LinearNet3": LinearNet3ProcedureFunction,
    "ExponentialFit": ExponentialFitProcedureFunction,
    "LinearFit": LinearFitProcedureFunction
}
