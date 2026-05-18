from typing import TypedDict, Literal, Tuple, List
from .calibration_dict import CalibrationDict

class DownhillSimplexCalibrationDict(
    CalibrationDict,
    total=False
):
    method: Literal["downhill-simplex"]

    limit: bool

    sigma: float

    ranges: List[Tuple[float, float]]

    no_improve_thr: float

    max_stagnations: int

    max_iter: int

    save_simplex: str