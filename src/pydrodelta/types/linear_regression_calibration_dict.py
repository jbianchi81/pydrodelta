from typing import TypedDict, Literal, Tuple, List
from .calibration_dict import CalibrationDict

class LinearRegressionCalibrationDict(
    CalibrationDict,
    total=False
):
    method: Literal["linear-regression"]
