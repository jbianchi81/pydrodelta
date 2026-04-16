from typing import List, Union, Optional
from .node_variable import NodeVariable
from .derived_node_serie import DerivedNodeSerie
from .node_serie import NodeSerie
from .node_serie_prono import NodeSerieProno
from .types.derived_origin_dict import DerivedOriginDict
from .types.interpolated_origin_dict import InterpolatedOriginDict
from .descriptors.dict_descriptor import DictDescriptor

class DerivedNodeVariable(NodeVariable):
    """This class represents a variable at a node where it is not observed, but values are derived from observations of the same variable at a nearby node or from observations of another variable at the same  (or nearby) node"""
    
    derived_from = DictDescriptor()
    """Derivation configuration"""
    
    interpolated_from = DictDescriptor()
    """Interpolation configuration"""
    
    @property
    def series(self) -> List[DerivedNodeSerie]:
        """Series of derived data of this variable at this node."""
        return self._series
    
    def _setDerivedSeries(self) -> None:
        if self.series_output is None:
            raise Exception("missing series_output for derived node %s variable %s" % (str(self._node.id) if self._node is not None else "unknown",str(self.id)))
        self._series = []
        for serie in self.series_output:
            self._series.append(
                DerivedNodeSerie(
                    series_id = serie.series_id, 
                    derived_from = self.derived_from,
                    topology = self._node._topology if self._node is not None else None,
                    base_path=self.base_path
                )
            )
    
    def _setInterpolatedSeries(self) -> None:
        if self.series_output is None:
            raise Exception("missing series_output for derived node %s variable %s" % (str(self._node.id) if self._node is not None else "unknown",str(self.id)))
        self._series = []
        for serie in self.series_output:
            self._series.append(
                DerivedNodeSerie(
                    series_id = serie.series_id, 
                    interpolated_from = self.interpolated_from,
                    topology = self._node._topology if self._node is not None else None,
                    base_path=self.base_path
                )
            )
    
    @property
    def series_prono(self) -> Optional[List[NodeSerieProno]]:
        """Series of forecasted data of this variable at this node. They may represent different data sources such as different model outputs"""
        return self._series_prono
    
    @series_prono.setter
    def series_prono(
        self,
        series : Optional[List[Union[dict,NodeSerieProno]]] = None
        ) -> None:
            if series is None:
                self._series_prono = None
            else:
                self._series_prono = [x if isinstance(x, NodeSerieProno) else NodeSerieProno(**x, base_path=self.base_path) for x in series]
    
    def __init__(
        self,
        derived_from : Optional[DerivedOriginDict] = None,
        interpolated_from : Optional[InterpolatedOriginDict] = None,
        series : Optional[List[Union[dict,NodeSerie]]] = None,
        series_prono : Optional[List[Union[dict,NodeSerieProno]]] = None,
        derived : bool = True,
        **kwargs):
        """
        derived_from : DerivedOriginDict = None

            Derivation configuration

        interpolated_from : InterpolatedOriginDict = None

            Interpolation configuration

        series : List[Union[dict,NodeSerie]] = None
            
            Additional timeseries
            
        series_prono : List[Union[dict,NodeSerieProno]] = None

            Forecast timeseries

        **kwargs

            Keyword arguments. See NodeVariable (:class:`~pydrodelta.NodeVariable`)
        """
        super().__init__(**kwargs)
        self.derived = True
        self.derived_from = derived_from
        self.interpolated_from = interpolated_from
        if derived_from is not None:
            self._setDerivedSeries()
        elif interpolated_from is not None:
            self._setInterpolatedSeries()
        else:
            self._series = []
        if series is not None:
            self._series.extend([x if isinstance(x, NodeSerie) else NodeSerie(**x, base_path=self.base_path) for x in series])
        self.series_prono = series_prono
    def derive(self) -> None:
        """Derive observations of .series[0] from associated node-variables"""
        self.series[0].derive()
        self.data = self.series[0].data
        self.original_data = self.data.copy(deep=True)
        if hasattr(self.series[0],"max_obs_date"):
            self.max_obs_date = self.series[0].max_obs_date
