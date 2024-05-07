from typing import TypedDict, List

class LinearCombinationDict(TypedDict):
    """
        coefficients: List[float]
        intercept: float
    """
    coefficients: List[float]
    intercept: float
