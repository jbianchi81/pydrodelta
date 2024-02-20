from .util import interval2timedelta
from typing import Union
from datetime import datetime, timedelta
from .descriptors.int_descriptor import IntDescriptor
from .descriptors.float_descriptor import FloatDescriptor
from .node_variable import NodeVariable

class InterpolatedOrigin:
    """Represents the origin node+variable of an interpolated node+variable"""

    node_id_1 = IntDescriptor()
    """First node identifier"""

    node_id_2 = IntDescriptor()
    """Second node identifier"""

    var_id_1 = IntDescriptor()
    """First variable identifier"""

    var_id_2 = IntDescriptor()
    """Second variable identifier"""

    @property
    def x_offset(self) -> Union[timedelta,int]:
        """Offset if the time axis"""
        return self._x_offset
    @x_offset.setter
    def x_offset(
        self,
        x_offset : Union[timedelta,dict,int]
        ) -> None:
        self._x_offset = interval2timedelta(x_offset) if isinstance(x_offset,(dict,timedelta)) else int(x_offset)

    y_offset = FloatDescriptor()
    """Offset of the values"""

    interpolation_coefficient = FloatDescriptor()
    """Interpolation weighting coefficient [0-1] (i.e., if 1, first node-variable gets all the weight)"""

    @property
    def origin_1(self) -> NodeVariable:
        """First node-variable origin for interpolation"""
        return self._origin_1

    @property
    def origin_2(self) -> NodeVariable:
        """Second node-variable origin for interpolation"""
        return self._origin_2

    def __init__(
        self,
        node_id_1 : int,
        node_id_2 : int,
        var_id_1 : int,
        var_id_2 : int,
        x_offset : Union[datetime,dict,float] = {"hours":0},
        y_offset : float = 0,
        interpolation_coefficient : float = None,
        topology = None
        ):
        """
        node_id_1 : int

            First node identifier

        node_id_2 : int

            Second node identifier

        var_id_1 : int

            First variable identifier

        var_id_2 : int

            Second variable identifier

        x_offset : Union[datetime,dict,float] = {"hours":0}

            Offset if the time axis

        y_offset : float = 0

            Offset of the values

        interpolation_coefficient : float = None

            Interpolation weighting coefficient [0-1] (i.e., if 1, first node-variable gets all the weight)

        topology = None

            Topology that contains the origin node-variables

        """
        self.node_id_1 = node_id_1
        self.node_id_2 = node_id_2
        self.var_id_1 = var_id_1
        self.var_id_2 = var_id_2
        self.x_offset = x_offset
        self.y_offset = y_offset
        self.interpolation_coefficient = interpolation_coefficient
        self._topology = topology
        self.setOrigin()
    
    def setOrigin(self) -> None:
        """Set origin node-variables according to the stored identifiers (.node_id_1, .node_id_2, .var_id_1, .var_id_2)"""
        if self._topology is not None:
            from_nodes = [x for x in self._topology.nodes if x.id == self.node_id_1]
            if not len(from_nodes):
                raise Exception("origin node not found for interpolated variable, id: %i" % self.node_id_1)
            if self.var_id_1 not in from_nodes[0].variables:
                raise Exception("origin variable not found for interpolated variable, node:id; %i, var_id: %i" % (self.node_id_1,self.var_id_1))
            self._origin_1 = from_nodes[0].variables[self.var_id_1]
            from_nodes = [x for x in self._topology.nodes if x.id == self.node_id_2]
            if not len(from_nodes):
                raise Exception("origin node not found for interpolated node, id: %i" % self.node_id_2)
            if self.var_id_2 not in from_nodes[0].variables:
                raise Exception("origin variable not found for interpolated variable, node:id; %i, var_id: %i" % (self.node_id_2,self.var_id_2))
            self._origin_2 = from_nodes[0].variables[self.var_id_2]
        else:
            self._origin_1 = None
            self._origin_2 = None
