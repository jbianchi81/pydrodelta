# Table of Contents

* [pydrodelta.procedure\_function](#pydrodelta.procedure_function)
  * [ProcedureFunction](#pydrodelta.procedure_function.ProcedureFunction)
    * [parameters](#pydrodelta.procedure_function.ProcedureFunction.parameters)
    * [parameter\_list](#pydrodelta.procedure_function.ProcedureFunction.parameter_list)
    * [initial\_states](#pydrodelta.procedure_function.ProcedureFunction.initial_states)
    * [boundaries](#pydrodelta.procedure_function.ProcedureFunction.boundaries)
    * [boundaries](#pydrodelta.procedure_function.ProcedureFunction.boundaries)
    * [outputs](#pydrodelta.procedure_function.ProcedureFunction.outputs)
    * [outputs](#pydrodelta.procedure_function.ProcedureFunction.outputs)
    * [input](#pydrodelta.procedure_function.ProcedureFunction.input)
    * [extra\_pars](#pydrodelta.procedure_function.ProcedureFunction.extra_pars)
    * [limits](#pydrodelta.procedure_function.ProcedureFunction.limits)
    * [pivot\_input](#pydrodelta.procedure_function.ProcedureFunction.pivot_input)
    * [\_\_init\_\_](#pydrodelta.procedure_function.ProcedureFunction.__init__)
    * [toDict](#pydrodelta.procedure_function.ProcedureFunction.toDict)
    * [rerun](#pydrodelta.procedure_function.ProcedureFunction.rerun)
    * [run](#pydrodelta.procedure_function.ProcedureFunction.run)
    * [makeSimplex](#pydrodelta.procedure_function.ProcedureFunction.makeSimplex)
    * [setParameters](#pydrodelta.procedure_function.ProcedureFunction.setParameters)
    * [setInitialStates](#pydrodelta.procedure_function.ProcedureFunction.setInitialStates)

<a id="pydrodelta.procedure_function"></a>

# pydrodelta.procedure\_function

<a id="pydrodelta.procedure_function.ProcedureFunction"></a>

## ProcedureFunction Objects

```python
class ProcedureFunction()
```

Abstract class to represent the transformation function of the procedure. It is instantiation, 'params' should be a dictionary which may contain an array of numerical or string 'parameters', an array of numerical or string 'initial_states', whereas 'procedure' must be the Procedure element which contains the function. The .run() method should accept an optional array of seriesData as 'input' and return an array of seriesData and a procedureFunctionResults object. When extending this class, any additional parameters may be added to 'params'.

<a id="pydrodelta.procedure_function.ProcedureFunction.parameters"></a>

#### parameters

function parameter values. Ordered list or dict

<a id="pydrodelta.procedure_function.ProcedureFunction.parameter_list"></a>

#### parameter\_list

```python
@property
def parameter_list() -> list
```

Get parameters list

<a id="pydrodelta.procedure_function.ProcedureFunction.initial_states"></a>

#### initial\_states

list or dict of function initial state values

<a id="pydrodelta.procedure_function.ProcedureFunction.boundaries"></a>

#### boundaries

```python
@property
def boundaries() -> EnhancedTypedList[ProcedureBoundary]
```

List of boundary conditions. Each item is a dict with a name <string> and a node_variable tuple(node_id : int,variable_id : int). The node_variables must map to plan.topology.nodes[node_id].variables[variable_id]

<a id="pydrodelta.procedure_function.ProcedureFunction.boundaries"></a>

#### boundaries

```python
@boundaries.setter
def boundaries(boundaries: List[ProcedureBoundaryDict]) -> None
```

Setter of boundaries

**Arguments**:

  ----------
  boundaries : list
  List of boundary conditions. Each item is a dict with a name <string> and a node_variable <NodeVariableIdTuple>. The node_variables must map to plan.topology.nodes[node_id].variables[variable_id]

<a id="pydrodelta.procedure_function.ProcedureFunction.outputs"></a>

#### outputs

```python
@property
def outputs() -> EnhancedTypedList[ProcedureBoundary]
```

list of procedure outputs. Each item is a dict with a name <string> and a node_variable tuple (node_id,variable_id). The node_variables must map to plan.topology.nodes[node_id].variables[variable_id]

<a id="pydrodelta.procedure_function.ProcedureFunction.outputs"></a>

#### outputs

```python
@outputs.setter
def outputs(outputs: List[ProcedureBoundaryDict]) -> None
```

Setter for outputs

**Arguments**:

  -----------
  outputs : list of dict
  list of procedure outputs. Each item is a dict with a name <string> and a node_variable tuple (node_id, variable_id). The node_variables must map to plan.topology.nodes[node_id].variables[variable_id]

<a id="pydrodelta.procedure_function.ProcedureFunction.input"></a>

#### input

Input of the procedure function

<a id="pydrodelta.procedure_function.ProcedureFunction.extra_pars"></a>

#### extra\_pars

Additional (non-calibratable) parameters

<a id="pydrodelta.procedure_function.ProcedureFunction.limits"></a>

#### limits

```python
@property
def limits() -> List[Tuple[float, float]]
```

Parameter limits

<a id="pydrodelta.procedure_function.ProcedureFunction.pivot_input"></a>

#### pivot\_input

```python
@property
def pivot_input() -> bool
```

Read-only property. Specifies if the run method of the procedure function requires a pivoted input

<a id="pydrodelta.procedure_function.ProcedureFunction.__init__"></a>

#### \_\_init\_\_

```python
def __init__(procedure=None,
             parameters: Union[list, dict] = [],
             initial_states: Union[list, dict] = [],
             boundaries: list = [],
             outputs: list = [],
             extra_pars: dict = dict(),
             **kwargs)
```

Initiate a procedure function

**Arguments**:

  -----------
  procedure : Procedure
  
  Procedure containing this function
  
  parameters : list or dict of floats
  
  function parameter values. Ordered list or dict
  
  initial_states : list or dict of floats
  
  list of function initial state values. Ordered list or dict
  
  boundaries : list of dict
  
  List of boundary conditions. Each item is a dict with a name <string> and a node_variable <NodeVariableIdTuple>
  
  outputs : list of dict
  
  list of procedure outputs. Each item is a dict with a name <string> and a node_variable tuple <NodeVariableIdTuple>
  
- `extra_pars` - dict
  
  Additional (non-calibratable) parameters

<a id="pydrodelta.procedure_function.ProcedureFunction.toDict"></a>

#### toDict

```python
def toDict() -> dict
```

Convert this procedureFunction to a dict

**Returns**:

  --------
  dict

<a id="pydrodelta.procedure_function.ProcedureFunction.rerun"></a>

#### rerun

```python
def rerun(input: list = None,
          parameters: Union[list, tuple] = None,
          initial_states: Union[list, tuple] = None) -> Tuple[list, dict]
```

Execute the procedure function with the given parameters and initial_states

**Arguments**:

  -----------
  input : list if DataFrames
  Procedure function input (boundary conditions). If None, loads using .loadInput()
  
  parameters : list or tuple
  Set procedure function parameters (self.parameters).
  
  initial_states : list or tuple
  Set initial states (self.initial_states)
  

**Returns**:

  --------
  2-tuple : first element is the procedure function output (list of DataFrames), while second is a ProcedureFunctionResults object

<a id="pydrodelta.procedure_function.ProcedureFunction.run"></a>

#### run

```python
def run(input: list = None) -> Tuple[list, dict]
```

Placeholder procedure function execution. To be overwritten in subclasses

**Arguments**:

  -----------
  input : list of DataFrames
  Procedure function input (boundary conditions). If None, loads using .loadInput()
  

**Returns**:

  --------
  2-tuple : first element is the procedure function output (list of DataFrames), while second is a ProcedureFunctionResults object

<a id="pydrodelta.procedure_function.ProcedureFunction.makeSimplex"></a>

#### makeSimplex

```python
def makeSimplex(sigma: float = 0.25,
                limit: bool = True,
                ranges: Optional[list] = None) -> list
```

Generate Simplex from procedure function parameters.

Generates a list of len(self._parameters)+1 parameter sets randomly using a normal distribution centered in the corresponding parameter range and with variance=sigma

**Arguments**:

  -----------
  sigma : float (default 0.25)
  Variance of the normal distribution relative to the range(1 = max_range - min_range)
  
  limit : bool (default True)
  Truncate values outside of the min-max range
  
  ranges : list or None
  Override parameter ranges with these values. Length must be equal to self._parameters and each element of the list must be a 2-tuple (range_min, range_max)
  

**Returns**:

  --------
  list : list of  length = len(self._parameters) + 1 where each element is a list of floats of length = len(self._parameters)

<a id="pydrodelta.procedure_function.ProcedureFunction.setParameters"></a>

#### setParameters

```python
def setParameters(parameters: Union[list, tuple] = []) -> None
```

Generic self.parameters setter. If self._parameters is not empty, uses name of each item to set self.parameters as a dict. Else will set a list

**Arguments**:

  -----------
  parameters : list or tuple
  Procedure function parameters to set

<a id="pydrodelta.procedure_function.ProcedureFunction.setInitialStates"></a>

#### setInitialStates

```python
def setInitialStates(states: Union[list, tuple] = []) -> None
```

Generic self.initial_states setter. If self._states is not empty, uses name of each item to set self.initial_states as a dict. Else will set a list

**Arguments**:

  states : list or tuple
  Procedure function initial states to set

