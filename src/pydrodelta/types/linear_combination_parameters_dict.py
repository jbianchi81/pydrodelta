from typing import TypedDict, List
from .forecast_step_dict import ForecastStepDict

class LinearCombinationParametersDict(TypedDict):
    forecast_steps : int
    lookback_steps : int
    coefficients : List[ForecastStepDict]
