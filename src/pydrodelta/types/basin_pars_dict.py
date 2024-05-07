from typing import TypedDict

class BasinParsDict(TypedDict):
    """
    area : float
        basin area in square meters
    rho  : float
        soil porosity (0-1)
    ae: float
        effective area (0-1)
    wp : float
        wilting point of soil (0-1)
    area_id : int
        Basin identifier at a5 input API
    """
    area : float
    rho : float
    ae : float
    wp : float
    area_id : int