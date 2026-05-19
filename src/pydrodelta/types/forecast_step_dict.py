from typing import TypedDict, List
from .boundary_dict import BoundaryDict

class ForecastStepDict(TypedDict):
    step : int
    """Forecast step for which the coefficients apply. Step 1 corresponds to the first forecasted time step, step 2 to the second, and so on."""
    intercept : float
    """Intercept term for the linear combination at the given forecast step."""
    boundaries : List[BoundaryDict]
    """List of boundary dicts for the linear combination at the given forecast step. Each boundary dict corresponds to an input time series and contains the name of the input and the coefficient to apply to that input at the given forecast step."""