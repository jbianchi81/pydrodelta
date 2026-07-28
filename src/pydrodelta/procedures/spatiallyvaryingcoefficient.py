from ..procedure_function_results import ProcedureFunctionResults
from ..procedure import Procedure
from ..function_boundary import FunctionBoundary
from ..util import adjustSeries
import math
from ..descriptors.int_descriptor import IntDescriptor
from ..descriptors.dict_descriptor import DictDescriptor
from ..descriptors.bool_descriptor import BoolDescriptor
from ..descriptors.string_descriptor import StringDescriptor
from typing import Tuple, Optional, List, Union, TypedDict, Any
from pandas import DataFrame, Series, concat
from datetime import datetime
import logging
from typing_extensions import Unpack, cast
from ..types.procedure_init_kwargs import ProcedureInitKwargs

class SpatialVaryingCoefficientParsDict(TypedDict, total=False):
    warmup_steps: int
    """Skip this number of initial steps for fit procedure. If not provided, no steps will be skipped."""
    drop_warmup: bool
    """Eliminate warmup steps from output"""
    tail_steps: int
    """Use only this number of final steps for fit procedure"""
    use_forecast_range: bool
    """Fit using only pairs where sim is within forecasted range of values"""
    nonspatial: Optional[List[str]]
    """Treat these inputs as nonspatial"""
    coordinates: Optional[List[Tuple[float, float]]]
    """Point coordinates. If missing, tries to read from station metadata"""

class SpatiallyVaryingCoefficientProcedure(Procedure):
    """Fits a linear model at each node where observed data is available, then interpolates coefficients for nodes with no observed data. Produces simulated outputs for all nodes"""

    _boundaries = [
        FunctionBoundary({"name": "input_1", "optional":False})
    ]
    """input: Variables containing simulated data that will be fitted against observations. Include variables with and without observed data. Optionally, add non spatial variables at the end"""

    _additional_boundaries = True

    _outputs = [
        FunctionBoundary({"name": "output"})
    ]
    """output: dependent variable (response). Include all input boundaries in the same order"""

    warmup_steps : Optional[int]
    """Skip this number of initial steps for fit procedure"""

    drop_warmup : bool
    """Eliminate warmup steps from output"""

    tail_steps : Optional[int]
    """Use only this number of final steps for fit procedure"""

    linear_models : LinFitModel[]
    """Results of the fit procedure(s)"""

    use_forecast_range : bool
    """Fit using only pairs where sim is within forecasted range of values"""

    nonspatial : List[str]
    """Treat these inputs as non-spatial"""

    coordinates : List[Tuple[float, float]]
    """Point coordinates"""

    @property
    def sim_range(self) -> Optional[Tuple[float,float]]:
        """Inmutable. Values range used for fit"""
        return self._sim_range

    type = StringDescriptor()

    def __init__(
        self,
        extra_pars : Optional[SpatialVaryingCoefficientParsDict] = None,
        **kwargs : Unpack[ProcedureInitKwargs]):
        """
        
        **kwargs : keyword arguments (see ProcedureFunction)
        """
        super().__init__(extra_pars = extra_pars, **kwargs)
        if "warmup_steps" in self.extra_pars:
            self.warmup_steps = self.extra_pars["warmup_steps"]
            self.drop_warmup = self.extra_pars["drop_warmup"] if "drop_warmup" in self.extra_pars else False
        else:
            self.warmup_steps = None
            self.drop_warmup = False
        if "tail_steps" in self.extra_pars:
            self.tail_steps = self.extra_pars["tail_steps"]
        else:
            self.tail_steps = None
        self.linear_model = None

        if "use_forecast_range" in self.extra_pars:
            self.use_forecast_range = self.extra_pars["use_forecast_range"]
        else:
            self.use_forecast_range = False

        self._sim_range = None

        self.type = "linear"

        self.linear_models = []

        self.nonspatial = self.extra_pars["nonspatial"] if "nonspatial" in self.extra_pars else []

        self.setCoordinates(extra_pars["coordinates"] if extra_pars is not None and "coordinates" in extra_pars else None)

    def setCoordinates(self, coordinates : Optional[List[Tuple[float, float]]]):
        self.coordinates = []
        for i, b in enumerate(self.boundaries):
            if b.name in self.nonspatial:
                continue
            if coordinates is not None and 0 <= i < len(coordinates) and coordinates[i] is not None:
                self.coordinates.append(parse_float_pair(coordinates[i]))
                continue
            if b.node is None:
                raise RuntimeError("node not set at boundary %s" % b.name)
            if b.node.station is None:
                raise RuntimeError("station not set at boundary %s, node %d" % (b.name, b.node.id))
            if b.node.station.geom is None:
                raise RuntimeError("geom not set at boundary %s, node %d, station.id %d" % (b.name, b.node.id, b.node.station.id))
            self.coordinates.append((b.node.station.geom.x, b.node.station.geom.y))

    def exec(
        self,
        input : Optional[Union[DataFrame,List[DataFrame]]] = None,
        output_obs : Optional[Union[DataFrame,List[DataFrame]]] = None
        ) -> tuple:
        """
        Ejecuta la función. Si input es None, ejecuta self.loadInput para generar el input. input debe ser una lista de objetos SeriesData
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
            # read sim
            input = self.loadInput(inplace=False,pivot=True, read_sim=True)
        if isinstance(input, list):
            input = self.pivot_input(input)
        if output_obs is None:
            # read obs
            output_obs = self.output_obs if self.output_obs is not None else self.loadInput(inplace=False, pivot=True)
        if isinstance(output_obs, list):
            output_obs = self.pivot_input(output_obs)

        result = self.fit(input, output_obs)

        return (
            result.output,
            # ProcedureFunctionResults(
            #     border_conditions = input,
            #     data = input[0][["valor"]].rename(columns={"valor":"input"}).join(output_obs[0][["valor"]].rename(columns={"valor": "output_obs"})).join(output_data[["valor"]].rename(columns={"valor":"output"})),
            #     extra_pars = cast(dict, self.extra_pars),
            #     adjust_results = self.linear_model
            # )
        )

    def fit(
        self,
        sim : DataFrame,
        obs : DataFrame
    ) -> FitResult:
        return fitSpatiallyVaryingCoefficient(sim, obs, self.coordinates, self.nonspatial)
        
def fitSpatiallyVaryingCoefficient(
        sim : DataFrame, 
        obs : DataFrame, 
        coordinates : List[Tuple[float, float]], 
        nonspatial : List[str]=[],
        warmup_steps : Optional[int]=None,
        tail_steps : Optional[int]=None,
        sim_range : Optional[Tuple[float, float]]=None,
        drop_warmup : bool=False) -> FitResult:
    data = sim.join(obs, rsuffix="_obs")
    # no_obs : List[str] = []
    coefficients = DataFrame({
        "name": Series(dtype="str"),
        "x": Series(dtype="float"),
        "y": Series(dtype="float"),
        "has_obs": Series(dtype="bool"),
        "intercept": Series(dtype="float"),
        "coefficients": Series(dtype="object"),
        "quant_Err": Series(dtype="float"),
        "r2": Series(dtype="float")
    })

    for index, c in enumerate(sim.columns):

        # if nonspatial, skip
        if c in nonspatial:
            continue

        if len(coordinates) <= index:
            raise ValueError("Missing coordinates for index %d, column %s" % (index, c))

        obs_column = "%s_obs" % c
        if obs_column not in data:
            raise RuntimeError("Column %s not found in obs" % c)

        # if no obs, skip
        if not len(data[obs_column].dropna()):
            coefficients.loc[len(coefficients)] = {
                "name": c,
                "has_obs": False,
                "x": coordinates[index][0],
                "y": coordinates[index][1]
            }
            continue

        # fit
        covariables = nonspatial
        covariables.append(c)
        (adjusted,none,fitted_model) = adjustSeries(
            data[covariables],
            data[[obs_column]],
            warmup=warmup_steps,
            tail=tail_steps,
            sim_range=sim_range,
            covariables=covariables,
            drop_warmup=drop_warmup
        )

        coefficients.loc[len(coefficients)] = {
            "name": c,
            "has_obs": True,
            "x": coordinates[index][0],
            "y": coordinates[index][1],
            "intercept": fitted_model["intercept"],
            "coefficients": fitted_model["coefficients"],
            "quant_Err": fitted_model["quant_Err"],
            "r2": fitted_model["r2"]
        }

        data = data.join(adjusted, rsuffix="_%s" % c)

    if not coefficients["has_obs"].any():
        raise ValueError("No obs data found for fit procedure")

    # TODO 
    # interpolate
    # return adjusted
    
def parse_float_pair(value: Any) -> tuple[float, float]:
    if not isinstance(value, (list, tuple)):
        raise TypeError("Expected a list or tuple")

    if len(value) < 2:
        raise ValueError("Expected at least two elements")

    return (float(value[0]), float(value[1]))
