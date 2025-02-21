# from pydrodelta.node_variable import NodeVariable 
import logging
from .descriptors.bool_descriptor import BoolDescriptor
from .descriptors.int_descriptor import IntDescriptor
from .descriptors.string_descriptor import StringDescriptor
from .node import Node
from .node_variable import NodeVariable
from typing import Tuple

class ProcedureBoundary():
    """
    A variable at a node which is used as a procedure boundary condition
    """

    optional = BoolDescriptor()
    """If true, null values in this boundary will not raise an error"""

    _node_variable : Tuple[int,int]

    @property
    def node_id(self) -> int: # = IntDescriptor()
        """node identitifier. Must be present in plan.topology.nodes"""
        return self._node_variable[0]

    @property
    def var_id(self) -> int: #  = IntDescriptor()
        """variable identifier. Must be present in node.variables"""
        return self._node_variable[1]

    _name : str

    @property
    def name(self) -> str: # = StringDescriptor()
        """name of the boundary. Must be one of the procedureFunction's boundaries or outputs"""
        return self._name

    @property
    def node(self) -> Node:
        """Reference to the Node instance of the topology that this boundary is assigned to"""
        return self._node

    @property
    def variable(self) -> NodeVariable:
        """Reference to the NodeVariable instance of the topology that this boundary is assigned to"""
        return self._variable

    warmup_only = BoolDescriptor()
    """If true, null values in the forecast horizon will not raise an error"""
        
    compute_statistics = BoolDescriptor()
    """Compute result statistics for this boundary"""
    def __init__(
            self,
            node_id : int = None,
            var_id : int = None,
            name : str = None,
            plan = None,
            optional : bool = False,
            warmup_only : bool = False,
            compute_statistics : bool = True,
            node_variable : Tuple[int,int] = None
        ):
        """Initiate class ProcedureBoundary
        
        Parameters:
        -----------
        node_id : int
            node identitifier. Must be present int plan.topology.nodes
        
        var_id : int
            variable identifier. Must be present in node.variables
        
        name : str
            name of the boundary. Must be one of the procedureFunction's boundaries or outputs
        
        plan : Plan
            The plan that contains the topology and the procedure that contains this boundary
        
        optional : bool (default False)
           If true, nulls in this boundary will not raise an error

        warmup_only : bool (default False)
            If true, mull values in the forecast horizon will not raise an error
        
        compute_statistics : bool (default True)
            Compute result statistics for this boundary
        """
        if node_id is None and node_variable is None:
            raise TypeError("Either node_id or node_variable must be set")
        if var_id is None and node_variable is None:
            raise TypeError("Either var_id or node_variable must be set")
        if name is None:
            raise TypeError("name must be str, not None")
        self.optional = optional
        node_id = node_id if node_id is not None else node_variable[0]
        var_id = var_id if var_id is not None else node_variable[1]
        self._node_variable = (node_id, var_id)
        self._name = name
        self._plan = plan
        if self._plan is not None:
            self.setNodeVariable(self._plan)
        else:
            self._variable = None
            self._node = None
        self.warmup_only = warmup_only
        self.compute_statistics = compute_statistics
    
    def toDict(self) -> dict:
        """Convert object into dict"""
        return {
            "optional": self.optional,
            "node_id": self.node_id,
            "var_id": self.var_id,
            "name": self.name,
            "warmup_only": self.warmup_only,
            "compute_statistics": self.compute_statistics
        }
    def setNodeVariable(self,plan) -> None:
        """
        Search for node id=self.node_id, variable id=self.var_id in plan.topology and set self._node and self._variable
        
        Parameters:
        -----------
        plan : Plan
            The plan containing the topology where to search the node and variable
        
        Raises:
        -------
        Exception when node with id: self.node_id containing a variable with id: self.var_id is not found in plan.topology"""
        for t_node in plan.topology.nodes:
            if t_node.id == self.node_id:
                self._node = t_node
                if self.var_id in t_node.variables:
                    self._variable = t_node.variables[self.var_id]
                    return
        raise Exception("ProcedureBoundary.setNodeVariable error: node with id: %s , var %i not found in topology" % (str(self.node_id), self.var_id))
    def assertNoNaN(
        self,
        warmup_only : bool = False,
        read_sim : bool = False,
        sim_index : int = 0
        ) -> None:
        """
        Assert if the are missing values in the boundary
        
        Parameters:
        -----------
        warmup_only : bool (default False)
            Check only the period before the forecast date

        read_sim : bool = False
            Check series_sim[sim_index].data
        
        sim_index : int = 0
            Read this item of series_sim
        
        Raises:
        -------
        AssertionError when procedure boundary variable is None

        AssertionError when procedure boundary data is None

        AssertionError procedure boundary variable data has NaN values
        """
        if self._variable is None:
            raise AssertionError("procedure boundary variable is None")
        if read_sim:
            if len(self._variable.series_sim) < sim_index + 1:
                raise AssertionError("procedure boundary series_sim not found at required index %i" % sim_index)
            if self._variable.series_sim[sim_index].data is None:
                raise AssertionError("procedure boundary sim data is None at required index %i" % sim_index)
            data = self._variable.series_sim[sim_index].data
        else:
            if self._variable.data is None:
                raise AssertionError("procedure boundary data is None")
            data = self._variable.data
        if warmup_only:
            na_count = data[data.index <= self._plan.forecast_date]["valor"].isna().sum()
        else:
            na_count = data["valor"].isna().sum()
        if na_count > 0:
            first_na_datetime = data[data["valor"].isna()].iloc[0].name.isoformat()
            raise AssertionError("procedure boundary variable %s has NaN values starting at position %s" % ( ("sim data at index %i" % sim_index) if read_sim else "data", first_na_datetime))
        return
