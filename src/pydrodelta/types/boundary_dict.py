from typing import TypedDict, List

class BoundaryDict(TypedDict):
    name : str
    """Name of the input time series to which the coefficient applies. Must match the name of one of the input time series provided in the boundaries list of the procedure."""
    values : List[float]
    """List of coefficients to apply to the input time series at the given forecast step. The length of this list must match the number of lookback steps specified in the LinearCombinationParametersDict."""