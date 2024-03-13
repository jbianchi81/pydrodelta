from typing import TypedDict, List
from .boundary_dict import BoundaryDict

class ForecastStepDict(TypedDict):
    step : int
    intercept : float
    boundaries : List[BoundaryDict]