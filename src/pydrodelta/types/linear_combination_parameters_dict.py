from typing import TypedDict, List
from .forecast_step_dict import ForecastStepDict

class LinearCombinationParametersDict(TypedDict):
    forecast_steps : int
    """Number of steps to forecast. Determines the length of the output time series."""
    lookback_steps : int
    """Number of steps to look back for the linear combination. Determines the number of coefficients."""
    coefficients : List[ForecastStepDict]
    """List of coefficients for the linear combination. Each item in the list is a ForecastStepDict that contains the coefficients to apply at a given forecast step. The length of this list must match the number of forecast steps specified in the forecast_steps field."""
