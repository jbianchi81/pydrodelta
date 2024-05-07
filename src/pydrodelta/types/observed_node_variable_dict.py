from .node_variable_dict import NodeVariableDict
from typing import List, Union
from .series_dict import SeriesDict
from .series_prono_dict import SeriesPronoDict
from ..node_serie import NodeSerie
from ..node_serie_prono import NodeSerieProno

class ObservedNodeVariableDict(NodeVariableDict):
    """
        series : List[Union[SeriesDict,NodeSerie]]
        series_prono : List[Union[SeriesPronoDict,NodeSerieProno]]
    """
    series : List[Union[SeriesDict,NodeSerie]]
    series_prono : List[Union[SeriesPronoDict,NodeSerieProno]]
        