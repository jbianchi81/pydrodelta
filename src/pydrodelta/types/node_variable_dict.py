from typing import TypedDict, NotRequired, Required, Union, List, Literal, Sequence
from a5client.util_types import Intervaleable
from .abstract_node_serie_dict import AbstractNodeSerieDict
from .node_serie_prono_dict import NodeSeriePronoDict
from .node_serie_sim_dict import NodeSerieSimDict
from ..node_serie import NodeSerie
from ..node_serie_prono import NodeSerieProno

class DerivedFromDict(TypedDict, total=False):
    node_id: Required[int]
    var_id: Required[int]
    x_offset: NotRequired[Intervaleable]
    y_offset: NotRequired[float]


class InterpolatedFromDict(TypedDict, total=False):
    node_id_1: Required[int]
    node_id_2: Required[int]
    var_id_1: Required[int]
    var_id_2: Required[int]
    interpolation_coefficient: Required[float]

    x_offset: NotRequired[Intervaleable]
    y_offset: NotRequired[float]


class AdjustFromDict(TypedDict, total=False):
    truth: NotRequired[int]
    sim: NotRequired[int]
    method: NotRequired[Literal["lfit"]]


class LinearCombinationDict(TypedDict, total=False):
    intercept: NotRequired[float]
    coefficients: NotRequired[List[float]]

class NodeVariableDict(TypedDict, total=False):
    # required
    id: Required[int]

    # optional
    name: NotRequired[str]

    series: NotRequired[Union[Sequence[AbstractNodeSerieDict],Sequence[NodeSerie]]]
    series_prono: NotRequired[Union[Sequence[NodeSeriePronoDict],Sequence[NodeSerieProno]]]
    series_output: NotRequired[Sequence[AbstractNodeSerieDict]]
    series_sim: NotRequired[Sequence[NodeSerieSimDict]]

    output_series_id: NotRequired[Union[float, None]]

    derived: NotRequired[bool]
    derived_from: NotRequired[DerivedFromDict]

    interpolated_from: NotRequired[InterpolatedFromDict]

    fill_value: NotRequired[float]

    adjust_from: NotRequired[AdjustFromDict]

    linear_combination: NotRequired[LinearCombinationDict]

    time_interval: NotRequired[Intervaleable]
    interpolation_limit: NotRequired[Intervaleable]

    extrapolate: NotRequired[bool]

    use_filled_truth: NotRequired[bool]