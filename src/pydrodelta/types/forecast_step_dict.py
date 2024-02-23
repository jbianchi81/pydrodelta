from typing import TypedDict
from .boundary_dict import BoundaryDict

class ForecastStepDict(TypedDict):
    intercept : float
    boundaries : list[BoundaryDict]