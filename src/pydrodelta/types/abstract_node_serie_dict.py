from typing import TypedDict, Required, NotRequired, List, Union, Literal
from a5client.util_types import Intervaleable, TVP, TVPserializable

class AbstractNodeSerieDict(TypedDict, total=False):
    # required
    series_id: Required[int]

    # optional
    id: NotRequired[int]
    tipo: NotRequired[Literal["puntual","areal","raster"]]

    lim_outliers: NotRequired[List[float]]  # minItems=2 not enforced here
    lim_jump: NotRequired[float]

    x_offset: NotRequired[Intervaleable]
    y_offset: NotRequired[float]
    scale: NotRequired[float]

    comment: NotRequired[str]

    moving_average: NotRequired[Intervaleable]

    csv_file: NotRequired[str]
    json_file: NotRequired[str]

    observations: NotRequired[
        List[Union[TVP, TVPserializable]]
    ]

    save_post: NotRequired[str]

    name: NotRequired[str]

    required: NotRequired[bool]

    output_file: NotRequired[str]
    output_format: NotRequired[str]
    output_schema: NotRequired[str]

    agg_func: NotRequired[
        Literal[
            "sum",
            "first",
            "last",
            "mean",
            "median",
            "min",
            "max",
            "std",
            "var",
            "prod",
            "mad",
        ]
    ]