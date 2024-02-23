from typing import TypedDict
from .forecast_step_dict import ForecastStepDict

class LinearCombinationParametersDict(TypedDict):
    forecast_steps : int
    lookback_steps : int
    coefficients : list[ForecastStepDict]
