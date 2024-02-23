from pandas import DataFrame
from ..procedure_function import ProcedureFunction, ProcedureFunctionResults
from ..validation import getSchemaAndValidate
from ..function_boundary import FunctionBoundary
from typing import Union, List
from ..descriptors.float_descriptor import FloatDescriptor
from ..descriptors.string_descriptor import StringDescriptor
from ..descriptors.list_descriptor import ListDescriptor
from ..types.boundary_dict import BoundaryDict
from ..types.forecast_step_dict import ForecastStepDict
from ..types.linear_combination_parameters_dict import LinearCombinationParametersDict

class BoundaryCoefficients():
    """Linear combination coefficients for a boundary at a given forecast step"""

    name = StringDescriptor()
    """Name of the boundary. Must map to a name of a procedureFunction's boundary"""

    value = ListDescriptor()
    """List of coefficients (floats). First is for the last observation time step, second is for the previous step, and so on"""
    
    def __init__(
        self,
        name : str,
        values : list[float],
        procedure_function
        ):
        """
        Args:
            name (str): Name of the boundary. Must map to a name of a procedureFunction's boundary_
            values (list[float]): List of coefficients (floats). First is for the last observation time step, second is for the previous step, and so on
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
        procedure_function
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
    
    def toDict(self) -> dict:
        """Convert to dict"""
        return {
            "intercept": self.intercept,
            "boundaries": [ x.toDict() for x in self.boundaries ]
        }



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
        return self._coefficients

    def __init__(
        self,
        parameters : LinearCombinationParametersDict,
        **kwargs
        ):
        """
        Args:
            parameters : LinearCombinationParametersDict:
                Properties:
                - forecast_steps : int
                - lookback_steps : int
                - coefficients : List[ForecastStepDict]

        Raises:
            Exception: _description_
            Exception: _description_
        """
        super().__init__(parameters = parameters, **kwargs)
        getSchemaAndValidate(dict(kwargs, parameters = parameters),"LinearCombinationProcedureFunction")
        self._coefficients = list()
        if len(self.parameters["coefficients"]) < self.forecast_steps:
            raise Exception("length of coefficients is shorter than forecast_steps")
        if len(self.parameters["coefficients"]) > self.forecast_steps:
            raise Exception("length of coefficients exceeds forecast_steps")
        for forecast_step in self.parameters["coefficients"]:
            self._coefficients.append(ForecastStep(**forecast_step, procedure_function = self))
    
    def run(
        self,
        input : list[DataFrame] = None
        ) -> tuple[List[DataFrame],ProcedureFunctionResults]:
        """Run the function procedure
        
        Arguments:
            input : list of DataFrames
                Boundary conditions. If None, runs .loadInput

        Returns:
            tuple[List[DataFrame],ProcedureFunctionResults] : first element is the procedure function output (list of DataFrames), while second is a ProcedureFunctionResults object
        
        Raises:
            Exception : If data is missing in a boundary at a required timestep"""
        if input is None:
            input = self._procedure.loadInput(inplace=False,pivot=False)
        output = []
        for t_index, forecast_step in enumerate(self.coefficients):
            forecast_date = self._procedure._plan.forecast_date + t_index * self._procedure._plan.time_interval
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
        output = DataFrame(output)
        output = output.set_index("timestart")
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