from .util import interval2timedelta
from .descriptors.int_descriptor import IntDescriptor
from .descriptors.float_descriptor import FloatDescriptor
from typing import Union
from datetime import timedelta
from .node_variable import NodeVariable

class DerivedOrigin:
    """Represents the origin node+variable of a derived node+variable"""
    
    node_id = IntDescriptor()
    """Node identifier of the origin"""
    
    var_id = IntDescriptor()
    """Variable identifier of the origin"""
    
    @property
    def x_offset(self) -> Union[timedelta,int]:
        """Offset of the time index"""
        return self._x_offset
    @x_offset.setter
    def x_offset(
        self,
        x_offset : Union[dict,int]
        )-> None:
        self._x_offset = interval2timedelta(x_offset) if isinstance(x_offset,dict) else int(x_offset) if x_offset is not None else None

    y_offset = FloatDescriptor()
    """Offset of the values"""
    
    @property
    def origin(self) -> NodeVariable:
        """Origin NodeVariable"""
        return self._origin
    def origin(
        self,
        ignored
        ) -> None:
        if self._topology is not None:
            from_nodes = [x for x in self._topology.nodes if x.id == self.node_id]
            if not len(from_nodes):
                raise Exception("origin node not found for derived variable, id: %i" % self.node_id)
            if self.var_id not in from_nodes[0].variables:
                raise Exception("origin variable not found for derived variable, node:id; %i, var_id: %i" % (self.node_id,self.var_id))
            self._origin = from_nodes[0].variables[self.var_id]
        else:
            self._origin = None

    def __init__(
        self,
        node_id : int,
        var_id : int,
        x_offset : Union[dict,int] = None,
        y_offset : float = None,
        topology = None
        ):
        """
        Parameters:
        -----------
        node_id : int
            
            Node identifier of the origin

        var_id : int

            Variable identifier of the origin

        x_offset : Union[dict,int] = None

            Offset of the time index

        y_offset : float = None

            Offset of the values

        topology = None
        """
        self.node_id = node_id
        self.var_id = var_id
        self.x_offset = x_offset
        self.y_offset = y_offset
        self._topology = topology
        self.origin = 0
