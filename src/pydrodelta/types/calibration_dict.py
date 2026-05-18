from typing import TypedDict, Literal, Tuple, Union
from a5client.util_types import Dateable

ObjectiveFunction = Literal[
    "rmse",
    "mse",
    "bias",
    "stdev_dif",
    "r",
    "nse",
    "cov",
    "oneminusr",
    "kge"
]

class CalibrationDict(TypedDict, total=False):
    calibrate: bool
    result_index: int
    objective_function: ObjectiveFunction
    save_result: str
    calibration_period: Tuple[Dateable, Dateable]