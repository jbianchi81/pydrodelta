# from pydrodelta.node_variable import NodeVariable 
import logging

class ProcedureBoundary():
    """
    A variable at a node which is used as a procedure boundary condition
    """
    def __init__(
            self,
            node_id : int,
            var_id : int,
            name : str,
            plan = None,
            optional : bool = False,
            warmup_only : bool = False,
            compute_statistics : bool = True,
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
        self.optional = optional
        """If true, null values in this boundary will not raise an error"""
        self.node_id = int(node_id)
        """node identitifier. Must be present int plan.topology.nodes"""
        self.var_id = int(var_id)
        """variable identifier. Must be present in node.variables"""
        self.name = name
        """name of the boundary. Must be one of the procedureFunction's boundaries or outputs"""
        if plan is not None:
            self.setNodeVariable(plan)
            self._plan = plan
        else:
            self._variable = None
            self._node = None
            self._plan = None
        self.warmup_only = warmup_only
        """If true, mull values in the forecast horizon will not raise an error"""
        self.compute_statistics = compute_statistics
        """Compute result statistics for this boundary"""
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
        warmup_only : bool = False
        ) -> None:
        """
        Assert if the are missing values in the boundary
        
        Parameters:
        -----------
        warmup_only : bool (default False)
            Check only the period before the forecast date
        
        Raises:
        -------
        AssertionError when procedure boundary variable is None

        AssertionError when procedure boundary data is None

        AssertionError procedure boundary variable data has NaN values
        """
        if self._variable is None:
            raise AssertionError("procedure boundary variable is None")
        if self._variable.data is None:
            raise AssertionError("procedure boundary data is None")
        if warmup_only:
            na_count = self._variable.data[self._variable.data.index <= self._plan.forecast_date]["valor"].isna().sum()
        else:
            na_count = self._variable.data["valor"].isna().sum()
        if na_count > 0:
            first_na_datetime = self._variable.data[self._variable.data["valor"].isna()].iloc[0].name.isoformat()
            raise AssertionError("procedure boundary variable data has NaN values starting at position %s" % first_na_datetime)
        return
