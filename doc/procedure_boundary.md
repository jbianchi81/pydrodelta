# Table of Contents

* [pydrodelta.procedure\_boundary](#pydrodelta.procedure_boundary)
  * [ProcedureBoundary](#pydrodelta.procedure_boundary.ProcedureBoundary)
    * [optional](#pydrodelta.procedure_boundary.ProcedureBoundary.optional)
    * [node\_id](#pydrodelta.procedure_boundary.ProcedureBoundary.node_id)
    * [var\_id](#pydrodelta.procedure_boundary.ProcedureBoundary.var_id)
    * [name](#pydrodelta.procedure_boundary.ProcedureBoundary.name)
    * [node](#pydrodelta.procedure_boundary.ProcedureBoundary.node)
    * [variable](#pydrodelta.procedure_boundary.ProcedureBoundary.variable)
    * [warmup\_only](#pydrodelta.procedure_boundary.ProcedureBoundary.warmup_only)
    * [compute\_statistics](#pydrodelta.procedure_boundary.ProcedureBoundary.compute_statistics)
    * [\_\_init\_\_](#pydrodelta.procedure_boundary.ProcedureBoundary.__init__)
    * [toDict](#pydrodelta.procedure_boundary.ProcedureBoundary.toDict)
    * [setNodeVariable](#pydrodelta.procedure_boundary.ProcedureBoundary.setNodeVariable)
    * [assertNoNaN](#pydrodelta.procedure_boundary.ProcedureBoundary.assertNoNaN)

<a id="pydrodelta.procedure_boundary"></a>

# pydrodelta.procedure\_boundary

<a id="pydrodelta.procedure_boundary.ProcedureBoundary"></a>

## ProcedureBoundary Objects

```python
class ProcedureBoundary()
```

A variable at a node which is used as a procedure boundary condition

<a id="pydrodelta.procedure_boundary.ProcedureBoundary.optional"></a>

#### optional

If true, null values in this boundary will not raise an error

<a id="pydrodelta.procedure_boundary.ProcedureBoundary.node_id"></a>

#### node\_id

```python
@property
def node_id() -> int
```

node identitifier. Must be present in plan.topology.nodes

<a id="pydrodelta.procedure_boundary.ProcedureBoundary.var_id"></a>

#### var\_id

```python
@property
def var_id() -> int
```

variable identifier. Must be present in node.variables

<a id="pydrodelta.procedure_boundary.ProcedureBoundary.name"></a>

#### name

```python
@property
def name() -> str
```

name of the boundary. Must be one of the procedureFunction's boundaries or outputs

<a id="pydrodelta.procedure_boundary.ProcedureBoundary.node"></a>

#### node

```python
@property
def node() -> Node
```

Reference to the Node instance of the topology that this boundary is assigned to

<a id="pydrodelta.procedure_boundary.ProcedureBoundary.variable"></a>

#### variable

```python
@property
def variable() -> NodeVariable
```

Reference to the NodeVariable instance of the topology that this boundary is assigned to

<a id="pydrodelta.procedure_boundary.ProcedureBoundary.warmup_only"></a>

#### warmup\_only

If true, null values in the forecast horizon will not raise an error

<a id="pydrodelta.procedure_boundary.ProcedureBoundary.compute_statistics"></a>

#### compute\_statistics

Compute result statistics for this boundary

<a id="pydrodelta.procedure_boundary.ProcedureBoundary.__init__"></a>

#### \_\_init\_\_

```python
def __init__(node_id: int = None,
             var_id: int = None,
             name: str = None,
             plan=None,
             optional: bool = False,
             warmup_only: bool = False,
             compute_statistics: bool = True,
             node_variable: Tuple[int, int] = None)
```

Initiate class ProcedureBoundary

**Arguments**:

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

<a id="pydrodelta.procedure_boundary.ProcedureBoundary.toDict"></a>

#### toDict

```python
def toDict() -> dict
```

Convert object into dict

<a id="pydrodelta.procedure_boundary.ProcedureBoundary.setNodeVariable"></a>

#### setNodeVariable

```python
def setNodeVariable(plan) -> None
```

Search for node id=self.node_id, variable id=self.var_id in plan.topology and set self._node and self._variable

**Arguments**:

  -----------
  plan : Plan
  The plan containing the topology where to search the node and variable
  

**Raises**:

  -------
  Exception when node with id: self.node_id containing a variable with id: self.var_id is not found in plan.topology

<a id="pydrodelta.procedure_boundary.ProcedureBoundary.assertNoNaN"></a>

#### assertNoNaN

```python
def assertNoNaN(warmup_only: bool = False) -> None
```

Assert if the are missing values in the boundary

**Arguments**:

  -----------
  warmup_only : bool (default False)
  Check only the period before the forecast date
  

**Raises**:

  -------
  AssertionError when procedure boundary variable is None
  
  AssertionError when procedure boundary data is None
  
  AssertionError procedure boundary variable data has NaN values

