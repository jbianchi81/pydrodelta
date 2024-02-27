from typing import TypedDict, List
from .boundary_dict import BoundaryDict

class ForecastStepDict(TypedDict):
    intercept : float
    boundaries : List[BoundaryDict]