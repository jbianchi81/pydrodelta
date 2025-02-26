from pandas import DataFrame
from pandas import Series
from datetime import timedelta, datetime
from sklearn.linear_model import LinearRegression
import scipy.stats as stats
from ..procedure_function import ProcedureFunction, ProcedureFunctionResults
from ..validation import getSchemaAndValidate
from ..function_boundary import FunctionBoundary
from typing import Union, List, Tuple
from ..descriptors.float_descriptor import FloatDescriptor
from ..descriptors.string_descriptor import StringDescriptor
from ..descriptors.list_descriptor import ListDescriptor
from ..descriptors.int_descriptor import IntDescriptor
from ..types.boundary_dict import BoundaryDict
from ..types.forecast_step_dict import ForecastStepDict
from ..types.linear_combination_parameters_dict import LinearCombinationParametersDict
from ..result_statistics import ResultStatistics
from ..util import groupByCalibrationPeriod
import json
import logging

class BoundaryCoefficients():
    """Linear combination coefficients for a boundary at a given forecast step"""

    name = StringDescriptor()
    """Name of the boundary. Must map to a name of a procedureFunction's boundary"""

    value = ListDescriptor()
    """List of coefficients (floats). First is for the last observation time step, second is for the previous step, and so on"""
    
    def __init__(
        self,
        name : str,
        values : List[float],
        procedure_function
        ):
        """
        Args:
            name (str): Name of the boundary. Must map to a name of a procedureFunction's boundary_
            values (List[float]): List of coefficients (floats). First is for the last observation time step, second is for the previous step, and so on
            procedure_function (ProcedureFunction): Reference to the ProcedureFunction that contains this

        Raises:
            Exception: If length of values is not equal to procedure function lookback steps
        """
        self._procedure_function = procedure_function
        self.name = name
        if len(values) < self._procedure_function.lookback_steps:
            raise Exception("Length of values list of boundary %i is shorter than procedure function lookback_steps (%i)" % (len(values), self._procedure_function.lookback_steps))
        if len(values) > self._procedure_function.lookback_steps:
            raise Exception("Length of values list of boundary %i is longer than procedure function lookback_steps (%i)" % (len(values), self._procedure_function.lookback_steps))
        self.values = values
    
    def toDict(self) -> dict:
        """Convert to dict"""
        return {
            "name": self.name,
            "values": self.values
        }

class ForecastStep():
    """Linear combination parameters for a given forecast step"""

    intercept = FloatDescriptor()
    """Intercept of the linear combination"""

    step = IntDescriptor()

    @property
    def boundaries(self) -> List[BoundaryCoefficients]:
        return self._boundaries
    @boundaries.setter
    def boundaries(
        self,
        boundaries : List[BoundaryDict]
        ) -> None:
        """
        Args:
            boundaries (List[dict]): List where each item is a dict with a name property that maps to the procedureFunction's boundaries and a values property that is a list of coefficients for that boundary

        Raises:
            Exception: If a boundary name is not found in the procedureFunction's boundaries 
        """
        self._boundaries = list()
        for boundary in boundaries:
            if str(boundary["name"]) not in [b.name for b in self._procedure_function.boundaries]:
                raise Exception("Boundary %s not found in procedure.boundaries: " % (str(boundary["name"]), str([b.name for b in self._procedure_function.boundaries])))
            self.boundaries.append(BoundaryCoefficients(**boundary, procedure_function = self._procedure_function))
    
    def __init__(
        self,
        intercept : float,
        boundaries : List[BoundaryDict],
        procedure_function,
        step : int,
        ):
        """
        Args:
            intercept (float): Intercept of the linear combination
            boundaries (List[dict]): List where each item is a dict with a name property that maps to the procedureFunction's boundaries and a values property that is a list of coefficients for that boundary
            procedure_function (_type_): Reference to the ProcedureFunction that contains this.
        """
        self._procedure_function = procedure_function
        self.intercept = intercept
        self.boundaries = boundaries
        self.step = step
    
    def toDict(self) -> dict:
        """Convert to dict"""
        return {
            "intercept": self.intercept,
            "boundaries": [ x.toDict() for x in self.boundaries ]
        }
    
    def __repr__(self) -> str:
        return json.dumps(self.toDict(),indent=4)



class LinearCombinationProcedureFunction(ProcedureFunction):
    """Multivariable linear combination procedure function - one linear combination for each forecast horizon. Being x [, y, ...] the boundary series, for each forecast time step t it returns intercept[t] + [ x[-l] * coefficients[t]boundaries['x'][l] for l in 1..lookback_steps ] and so on for additional boundaries and lookback steps."""
    
    _boundaries = [
        FunctionBoundary({"name": "input_1", "warmup_only": True}),
        # FunctionBoundary({"name": "input_2", "optional": True})
    ]
    
    _additional_boundaries = True
    
    _outputs = [
        FunctionBoundary({"name": "output"})
    ]
    
    _additional_outputs = False
    
    @property
    def forecast_steps(self) -> int:
        return self.parameters["forecast_steps"]
    
    @property
    def lookback_steps(self) -> int:
        return self.parameters["lookback_steps"]
        
    @property
    def coefficients(self) -> List[ForecastStep]:
        """Coefficients of the linear combination"""
        if "coefficients" not in self.parameters:
            logging.warning("Coefficients not set")
            return None
        return [
            ForecastStep(**step, procedure_function = self)
            for step in self.parameters["coefficients"]
        ]

    _no_sim = True

    @property
    def k(self) -> int:
        """Number of independent variables"""
        return self.lookback_steps * len(self.coefficients[0].boundaries)
    
    @property 
    def Z(self) -> float:
        """Confidence level multiplier (e.g., Z = 1.96 for 95% confidence)"""
        return self.extra_pars["Z"] if "Z" in self.extra_pars else 1.96
    
    @property
    def confidence_level(self) -> float:
        return 2 * stats.norm.cdf(self.Z) - 1

    @property
    def error_band(self) -> Union[List[float],None]:
        """Error band half-widths for each step in the forecast horizon"""
        if self._procedure.calibration is not None and self._procedure.calibration.result is not None and "scores" in self._procedure.calibration.result and self._procedure.calibration.result["scores"] is not None:
            error_band = []
            for i, step in enumerate(self._procedure.calibration.result["scores"]):
                rse = step["rse_val"] if step["rse_val"] is not None else step["rse"]
                if rse is None:
                    raise ValueError("rse not found for step %i of procedure %s" % (i, self._procedure.id))
                error_band.append(self.Z * rse)
            return error_band
        else:
            return None

    def __init__(
        self,
        parameters : LinearCombinationParametersDict,
        extra_pars : dict = {},
        **kwargs
        ):
        """
        Args:
            parameters : LinearCombinationParametersDict:
                Properties:
                - forecast_steps : int
                - lookback_steps : int
                - coefficients : List[ForecastStepDict]
            
            extra_pars : {Z: float = 1.96}
                Z: Confidence level multiplier (e.g., Z = 1.96 for 95% confidence)

        Raises:
            Exception: _description_
            Exception: _description_
        """
        super().__init__(parameters = parameters, extra_pars = extra_pars, **kwargs)
        getSchemaAndValidate(dict(kwargs, parameters = parameters),"LinearCombinationProcedureFunction")
        # self._coefficients = list()
        if len(self.parameters["coefficients"]) < self.forecast_steps:
            raise Exception("length of coefficients is shorter than forecast_steps")
        if len(self.parameters["coefficients"]) > self.forecast_steps:
            raise Exception("length of coefficients exceeds forecast_steps")
        # set warmup_steps
        if self._procedure.calibration is not None and self._procedure.calibration.calibrate == True:
            pass
        else:
            for boundary in self.boundaries:
                boundary.warmup_steps = self.lookback_steps
        # for forecast_step in self.parameters["coefficients"]:
        #     self._coefficients.append(ForecastStep(**forecast_step, procedure_function = self))
    
    def run(
        self,
        input : List[DataFrame] = None
        ) -> Tuple[List[DataFrame],ProcedureFunctionResults]:
        """Run the function procedure
        
        Arguments:
            input : list of DataFrames
                Boundary conditions. If None, runs .loadInput

        Returns:
            Tuple[List[DataFrame],ProcedureFunctionResults] : first element is the procedure function output (list of DataFrames), while second is a ProcedureFunctionResults object
        
        Raises:
            Exception : If data is missing in a boundary at a required timestep"""
        if input is None:
            input = self._procedure.loadInput(inplace=False,pivot=False)
        output = []
        error_band = self.error_band
        for t_index, forecast_step in enumerate(self.coefficients):
            forecast_date = self._procedure._plan.forecast_date + (t_index + 1) * self._procedure._plan.time_interval
            result = 1 * forecast_step.intercept
            for b_index, boundary in enumerate(forecast_step.boundaries):
                for c_index, coefficient in enumerate(boundary.values):
                    lookback_date = self._procedure._plan.forecast_date - c_index * self._procedure._plan.time_interval
                    if lookback_date not in input[b_index].index:
                        raise Exception("Procedure %s: missing index at %s for %s" % (str(self._procedure.id),str(lookback_date), boundary.name))
                    if input[b_index].at[lookback_date,"valor"] is None:
                        raise Exception("Procedure %s: missing value at %s for %s" % (str(self._procedure.id),str(lookback_date), boundary.name))
                    result = result + coefficient * float(input[b_index].at[lookback_date,"valor"])
            output.append({
                "timestart": forecast_date,
                "valor": result 
            })
            # ADD ERROR BAND
            if error_band is not None and len(error_band) >= t_index + 1:
                output[len(output)-1]["superior"] = result + error_band[t_index]
                output[len(output)-1]["inferior"] = result - error_band[t_index]
        output = DataFrame(output)
        output = output.set_index("timestart")
        if error_band is not None:
            results_data = output[["valor","inferior","superior"]]
        else:
            results_data = output[["valor"]] # .join(output_obs.rename(columns={"valor_1": "obs"}),how="outer")
        for i, input_ in enumerate(input):
            colname = "input_%i" % (i + 1)
            results_data = results_data.join(input_[["valor"]].rename(columns={"valor": colname}),how="outer")
        return [output], ProcedureFunctionResults(
            data = results_data,
            parameters = {
                "forecast_steps": self.forecast_steps,
                "lookback_steps": self.lookback_steps,
                "coefficients": [x.toDict() for x in self.coefficients]
            }
        )
    
    def linearRegression(
        self,
        input : List[DataFrame] = None,
        calibration_period : Tuple[datetime, datetime] = None
        ) -> List[dict]:
        """
        Fit linear regression coefficients
        
        Args:
            input : List[DataFrame] = None
                input data. If None, loads from boundaries
            calibration_period : Tuple[datetime, datetime] = None
                Begin and end dates of training set. Data outside this period is used for validation. If not set, no validation is performed
        """
        is_optional = [x.optional for x in self.boundaries]
        for b in self.boundaries:
            b.optional = True
        input = input if input is not None else self._procedure.loadInput(inplace=False,pivot=False)
        for i, b in enumerate(self.boundaries):
            b.optional = is_optional[i]
        results = DataFrame({
            "horiz": Series(dtype="int"),
            "n": Series(dtype="int"),
            "rmse": Series(dtype="float"),
            "r": Series(dtype="float"),
            "nse": Series(dtype="float"),
            "rse": Series(dtype="float"),
            "n_val": Series(dtype="int"),
            "rmse_val": Series(dtype="float"),
            "r_val": Series(dtype="float"),
            "nse_val": Series(dtype="float"),
            "rse_val": Series(dtype="float"),
        })
        stats_all = []
        fitted_parameters : LinearCombinationParametersDict = {
            "forecast_steps": self.forecast_steps,
            "lookback_steps": self.lookback_steps,
            "coefficients": [] # List[ForecastStepDict]
        }
        for horiz in range(self.forecast_steps):
            data, data_val = self.getTrainingData(horiz, input, dropna=True, calibration_period = calibration_period)
            training_set = data.loc[:, data.columns!='target'].to_numpy()
            target = data.loc[:, data.columns=='target'].to_numpy()
            reg = LinearRegression().fit(training_set, target)
            predict = reg.predict(training_set)
            stats = ResultStatistics(
                [x[0] for x in target],
                [x[0] for x in predict],
                compute=True, 
                group = "cal", 
                calibration_period = calibration_period, 
                k = self.k)
            stats_all.append(stats)
            if data_val is not None:
                predict_val = reg.predict(data_val.loc[:, data_val.columns!='target'].to_numpy())
                target_val = data_val.loc[:, data_val.columns=='target'].to_numpy()
                stats_val = ResultStatistics(
                    [x[0] for x in target_val],
                    [x[0] for x in predict_val],
                    compute=True, 
                    group = "val", 
                    calibration_period = calibration_period,
                    k = self.k)
                stats_all.append(stats_val)
            else:
                stats_val = None
            results.loc[len(results.index)] = [
                horiz,
                stats.n,
                stats.rmse,
                stats.r,
                stats.nse,
                stats.rse,
                stats_val.n if stats_val is not None else None,
                stats_val.rmse if stats_val is not None else None,
                stats_val.r if stats_val is not None else None,
                stats_val.nse if stats_val is not None else None,
                stats_val.rse if stats_val is not None else None,
            ]

            forecast_step : ForecastStepDict = {
                "step": horiz,
                "intercept": float(reg.intercept_[0]),
                "boundaries": []
            }
            coef_i = 0
            for i, feature in enumerate(input):
                boundary : BoundaryDict = {
                    "name": self.boundaries[i].name,
                    "values": []
                }
                for lag in range(1,self.lookback_steps+1):
                    boundary["values"].append(float(reg.coef_[0][coef_i]))
                    coef_i = coef_i + 1
                forecast_step["boundaries"].append(boundary)
            fitted_parameters["coefficients"].append(forecast_step)
        return fitted_parameters, results, stats_all

    def getTrainingData(
        self,
        horiz : Union[int,timedelta] = 0,
        input : List[DataFrame] = None,
        dropna : bool = False,
        calibration_period : Tuple[datetime,datetime] = None 
        ) -> Tuple[DataFrame, DataFrame]:
        """
        Get training set for linear regression. input[0] is the target. One feature of the training set is generated for each input + lag (1 to self.lookback_steps) combination 
        
        Args:
            horiz : Union[int,timedelta] = 0
                Displace training set by int steps or timedelta
            input : List[DataFrame] = None
                First element is the target, the rest is the training set 
            dropna : bool = False
                If True, remove rows with NaN
            calibration_period : Tuple[datetime,datetime] = None 
        
        Returns:
            2-Tuple of DataFrames.
                First element: Training set of len(input) * self.lookback_steps columns
                Second element: Validation set of len(input) * self.lookback_steps columns. None if calibration_period is not set or no validation data is found 
        """
        input = input if input is not None else self._procedure.loadInput(inplace=False,pivot=False)
        data = input[0][["valor"]].rename(columns={"valor": "target"})
        for i, feature in enumerate(input):
            for lag in range(1,self.lookback_steps+1):
                feature_name = "input_%i_lag_%i" % (i, lag)
                feature_ = feature[["valor"]].shift(horiz) if type(horiz) == int else feature[["valor"]].shift(freq=horiz)
                feature_ = feature_.shift(lag)
                data = data.join(feature_.rename(columns={"valor": feature_name}))
        if dropna:
            data.dropna(inplace=True)
        if calibration_period is not None:
            data_cal, data_val = groupByCalibrationPeriod(data, calibration_period)
            if data_cal is None:
                raise Exception("No data found in calibration period")
            return data_cal, data_val
        return data, None # .to_numpy()
    
    def setParameters(
        self,
        parameters : LinearCombinationParametersDict = None,
        forecast_steps : int = None,
        lookback_steps : int = None,
        coefficients : List[ForecastStepDict] = None        
    ) -> None:
        if parameters is not None:
            self.parameters = parameters
        else:
            if forecast_steps is None:
                raise KeyError("Missing forecast_steps")
            if lookback_steps is None:
                raise KeyError("Missing lookback_steps")
            if coefficients is None:
                raise KeyError("Missing coefficients")
            self.parameters = {
                "forecast_steps": forecast_steps,
                "lookback_steps": lookback_steps,
                "coefficients": coefficients
            }            
        



