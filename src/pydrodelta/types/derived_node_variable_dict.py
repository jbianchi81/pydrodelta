from .node_variable_dict import NodeVariableDict
from typing import List, Union
from .series_dict import SeriesDict
from .series_prono_dict import SeriesPronoDict
from ..node_serie import NodeSerie
from ..node_serie_prono import NodeSerieProno
from .derived_origin_dict import DerivedOriginDict
from .interpolated_origin_dict import InterpolatedOriginDict

class DerivedNodeVariableDict(NodeVariableDict):
    """
        series : List[Union[SeriesDict,NodeSerie]]
        series_prono : List[Union[SeriesPronoDict,NodeSerieProno]]
        derived_from : DerivedOriginDict
        interpolated_from : InterpolatedOriginDict
        derived : bool
    """
    series : List[Union[SeriesDict,NodeSerie]]
    series_prono : List[Union[SeriesPronoDict,NodeSerieProno]]
    derived_from : DerivedOriginDict
    interpolated_from : InterpolatedOriginDict
    derived : bool
        