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
from pyproj import Geod
import numpy as np
import re

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
    power: Optional[float]
    """The power parameter for IDW. Default=2"""

class FitResult:
    data : DataFrame
    coefficients: DataFrame
    def __init__(
            self,
            data : DataFrame,
            coefficients : DataFrame):
        self.data = data
        self.coefficients = coefficients        

class SpatiallyVaryingCoefficientProcedure(Procedure):
    """Fits a linear model at each node where observed data is available, then interpolates coefficients for nodes with no observed data. Produces simulated outputs for all nodes"""

    _boundaries = [
        FunctionBoundary({"name": "input_1", "optional":False})
    ]
    """input: Variables containing simulated data that will be fitted against observations. Include variables with and without observed data. Optionally, add non spatial variables at the end"""

    _additional_boundaries = True

    _outputs = [
        FunctionBoundary({"name": "output_1"})
    ]
    """output: dependent variable (response). Include all input boundaries in the same order"""

    _additional_outputs = True

    warmup_steps : Optional[int]
    """Skip this number of initial steps for fit procedure"""

    drop_warmup : bool
    """Eliminate warmup steps from output"""

    tail_steps : Optional[int]
    """Use only this number of final steps for fit procedure"""

    coefficients : Optional[DataFrame]
    """Resulting coefficients of the fit + interpolate procedure"""

    use_forecast_range : bool
    """Fit using only pairs where sim is within forecasted range of values"""

    nonspatial : List[str]
    """Treat these inputs as non-spatial"""

    coordinates : List[Tuple[float, float]]
    """Point coordinates"""

    adj_data : Optional[DataFrame]
    """dataframe containing input, observed and adjusted data"""

    @property
    def sim_range(self) -> Optional[Tuple[float,float]]:
        """Inmutable. Values range used for fit"""
        return self._sim_range

    @property
    def power(self) -> float:
        """power parameter for IDW. Default=2"""
        return self.extra_pars["power"] if "power" in self.extra_pars else 2

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

        self.nonspatial = self.extra_pars["nonspatial"] if "nonspatial" in self.extra_pars else []

        self.setCoordinates(extra_pars["coordinates"] if extra_pars is not None and "coordinates" in extra_pars else None)

        self._pivot_input = True
        self.read_sim = True
        self._pivot_output_obs = True
        self._read_original_data = True
        self._use_boundary_name = True


    def setCoordinates(self, coordinates : Optional[List[Tuple[float, float]]]):
        self.coordinates = []
        for i, b in enumerate(self.boundaries):
            if coordinates is not None and 0 <= i < len(coordinates) and coordinates[i] is not None:
                self.coordinates.append(parse_float_pair(coordinates[i]))
                continue
            if b.node is None:
                if b.name in self.nonspatial:
                    self.coordinates.append((np.nan, np.nan))
                    continue                            
                raise RuntimeError("node not set at boundary %s" % b.name)
            if b.node.station is None:
                if b.name in self.nonspatial:
                    self.coordinates.append((np.nan, np.nan))
                    continue                            
                raise RuntimeError("station not set at boundary %s, node %d" % (b.name, b.node.id))
            if b.node.station.geom is None:
                if b.name in self.nonspatial:
                    self.coordinates.append((np.nan, np.nan))
                    continue                            
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
            input = self.loadInput(inplace=False,pivot=True, tag_column=False, read_sim=True, use_boundary_name=True)
        if isinstance(input, list):
            input = self.pivot_input_data(input)
        if output_obs is None:
            # read obs
            output_obs = self.output_obs if self.output_obs is not None else self.loadOutputObs(inplace=False, pivot=True, original_data=True, use_boundary_name=True)
        if isinstance(output_obs, list):
            output_obs = self.pivot_input_data(output_obs)

        fit_result = self.fit(input, output_obs)

        self.coefficients = fit_result.coefficients
        self.adj_data = fit_result.data

        pattern = re.compile('^adj_input')
        adj_columns = [c for c in fit_result.data.columns if pattern.match(c)]
        rename_colmap = {}
        for c in adj_columns:
            rename_colmap[c] = c.replace("adj_input","output")
        result_data = fit_result.data[adj_columns].rename(columns=rename_colmap)

        return (
            result_data,
            ProcedureFunctionResults(
                border_conditions = input,
                data = fit_result.data,
                extra_pars = cast(dict, self.extra_pars),
                adjust_results = fit_result.coefficients.to_dict(orient="records")
            )
        )

    def fit(
        self,
        sim : DataFrame,
        obs : DataFrame
    ) -> FitResult:
        pattern = re.compile('^output_')
        obs_columns = [c for c in obs.columns if pattern.match(c)]
        rename_colmap = {}
        for c in obs_columns:
            rename_colmap[c] = c.replace("output","input")
        return fitSpatiallyVaryingCoefficient(sim, obs.rename(columns=rename_colmap), self.coordinates, self.nonspatial, self.power)
        
def fitSpatiallyVaryingCoefficient(
        sim : DataFrame, 
        obs : DataFrame, 
        coordinates : List[Tuple[float, float]], 
        nonspatial : List[str]=[],
        power : float=2,
        warmup_steps : Optional[int]=None,
        tail_steps : Optional[int]=None,
        sim_range : Optional[Tuple[float, float]]=None,
        drop_warmup : bool=False) -> FitResult:
    """sim and obs must have the same column names

    Args:
        sim (DataFrame): _description_
        obs (DataFrame): _description_
        coordinates (List[Tuple[float, float]]): _description_
        nonspatial (List[str], optional): _description_. Defaults to [].
        power (float, optional): _description_. Defaults to 2.
        warmup_steps (Optional[int], optional): _description_. Defaults to None.
        tail_steps (Optional[int], optional): _description_. Defaults to None.
        sim_range (Optional[Tuple[float, float]], optional): _description_. Defaults to None.
        drop_warmup (bool, optional): _description_. Defaults to False.

    Raises:
        ValueError: _description_
        RuntimeError: _description_
        ValueError: _description_

    Returns:
        FitResult: _description_
    """
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

    # fit points with obs
    for index, c in enumerate(sim.columns):

        # if nonspatial, skip
        if c in nonspatial:
            data["adj_%s" % c] = np.nan
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
        covariables = [c, *nonspatial]
        (adjusted,none,fitted_model) = adjustSeries(
            data[covariables],
            data[[obs_column]].rename(columns={obs_column: obs_column.replace("_obs","")}),
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

        data["adj_%s" % c] = adjusted

    fitted_points = coefficients[coefficients["has_obs"] == True]
    if not len(fitted_points): # coefficients["has_obs"].any():
        raise ValueError("No obs data found for fit procedure")


    # interpolate coefficients
    geod = Geod(ellps="WGS84")
    for index, point in coefficients[coefficients["has_obs"] == False].iterrows():

        fp = fitted_points.copy()
        # distance
        _, _, fp["distance"] = geod.inv(
            np.full(len(fp), point.x),
            np.full(len(fp), point.y),
            fp["x"].to_numpy(),
            fp["y"].to_numpy(),
        )
        # IDW weights
        fp["weight"] = fp.apply(lambda row : 1 if row.distance == 0 else (1 / row.distance) ** power, axis=1)
        # intercept
        fp["w_intercept"] = fp.apply(lambda row : row.intercept * row.weight, axis=1)
        point["intercept"] = fp["w_intercept"].sum() / fp["weight"].sum()
        # coefficients
        fp["w_coefficients"] = fp.apply(lambda row : np.array(row.coefficients) * row.weight, axis=1)
        point["coefficients"] = fp["w_coefficients"].sum() / fp["weight"].sum()

        # interpolate values
        covariables = [point["name"], *nonspatial]
        data["adj_%s" % point["name"]] = data.apply(lambda row: point["intercept"] + np.array(point["coefficients"] * np.array(row[covariables])).sum() , axis=1)
    
    return FitResult(
        data,
        coefficients
    )
    
def parse_float_pair(value: Any) -> tuple[float, float]:
    if not isinstance(value, (list, tuple)):
        raise TypeError("Expected a list or tuple")

    if len(value) < 2:
        raise ValueError("Expected at least two elements")

    return (float(value[0]), float(value[1]))
