# Table of Contents

* [pydrodelta.procedures.muskingumchannel](#pydrodelta.procedures.muskingumchannel)
  * [MuskingumChannelProcedureFunction](#pydrodelta.procedures.muskingumchannel.MuskingumChannelProcedureFunction)
    * [K](#pydrodelta.procedures.muskingumchannel.MuskingumChannelProcedureFunction.K)
    * [X](#pydrodelta.procedures.muskingumchannel.MuskingumChannelProcedureFunction.X)
    * [Proc](#pydrodelta.procedures.muskingumchannel.MuskingumChannelProcedureFunction.Proc)
    * [dt](#pydrodelta.procedures.muskingumchannel.MuskingumChannelProcedureFunction.dt)
    * [engine](#pydrodelta.procedures.muskingumchannel.MuskingumChannelProcedureFunction.engine)
    * [\_\_init\_\_](#pydrodelta.procedures.muskingumchannel.MuskingumChannelProcedureFunction.__init__)
    * [run](#pydrodelta.procedures.muskingumchannel.MuskingumChannelProcedureFunction.run)
    * [setEngine](#pydrodelta.procedures.muskingumchannel.MuskingumChannelProcedureFunction.setEngine)
    * [setParameters](#pydrodelta.procedures.muskingumchannel.MuskingumChannelProcedureFunction.setParameters)
    * [setInitialStates](#pydrodelta.procedures.muskingumchannel.MuskingumChannelProcedureFunction.setInitialStates)

<a id="pydrodelta.procedures.muskingumchannel"></a>

# pydrodelta.procedures.muskingumchannel

<a id="pydrodelta.procedures.muskingumchannel.MuskingumChannelProcedureFunction"></a>

## MuskingumChannelProcedureFunction Objects

```python
class MuskingumChannelProcedureFunction(ProcedureFunction)
```

Método de tránsito hidrológico de la Oficina del río Muskingum. Parámetros: Tiempo de Tránsito (K) y Factor de forma (X). Condiciones de borde: Hidrograma en nodo superior de tramo.

<a id="pydrodelta.procedures.muskingumchannel.MuskingumChannelProcedureFunction.K"></a>

#### K

```python
@property
def K() -> float
```

Model parameter: transit time

<a id="pydrodelta.procedures.muskingumchannel.MuskingumChannelProcedureFunction.X"></a>

#### X

```python
@property
def X() -> float
```

Model parameter: shape factor

<a id="pydrodelta.procedures.muskingumchannel.MuskingumChannelProcedureFunction.Proc"></a>

#### Proc

```python
@property
def Proc() -> str
```

Routing procedure

<a id="pydrodelta.procedures.muskingumchannel.MuskingumChannelProcedureFunction.dt"></a>

#### dt

```python
@property
def dt() -> str
```

Calculation step

<a id="pydrodelta.procedures.muskingumchannel.MuskingumChannelProcedureFunction.engine"></a>

#### engine

```python
@property
def engine() -> MuskingumChannel
```

Reference to the MuskingumChannel procedure engine

<a id="pydrodelta.procedures.muskingumchannel.MuskingumChannelProcedureFunction.__init__"></a>

#### \_\_init\_\_

```python
def __init__(parameters: dict,
             initial_states: Union[list, dict] = [0],
             **kwargs)
```

**Arguments**:

  parameters : dict
  
  Properties:
  
  - K : float - transit time
  
  - X : float - shape factor
  
  initial_states : list - Initial discharge at the output. Defaults to [0]
  
  Keyword arguments:
  See ..procedure_function.ProcedureFunction

<a id="pydrodelta.procedures.muskingumchannel.MuskingumChannelProcedureFunction.run"></a>

#### run

```python
def run(input: list = None) -> tuple
```

Runs the procedure

input[0]: hidrograma en borde superior del tramo (DataFrame con index:timestamp y valor:float)

**Arguments**:

  -----------
  input : list of DataFrames
  Procedure function input (boundary conditions). If None, loads using .loadInput()
  

**Returns**:

  --------
  2-tuple : first element is the procedure function output (list of DataFrames), while second is a ProcedureFunctionResults object

<a id="pydrodelta.procedures.muskingumchannel.MuskingumChannelProcedureFunction.setEngine"></a>

#### setEngine

```python
def setEngine(input: DataFrame) -> None
```

Initialize MuskingumChannel procedure engine using provided input. Takes column "valor" from  input as upstream boundary condition

**Arguments**:

  input : DataFrame - The Procedure boundary

<a id="pydrodelta.procedures.muskingumchannel.MuskingumChannelProcedureFunction.setParameters"></a>

#### setParameters

```python
def setParameters(parameters: Union[list, tuple] = ...) -> None
```

Setter for self.parameters.

**Arguments**:

  -----------
  parameters : list or tuple
  
  Muskingum procedure function parameters to set (K : float, X : float)

<a id="pydrodelta.procedures.muskingumchannel.MuskingumChannelProcedureFunction.setInitialStates"></a>

#### setInitialStates

```python
def setInitialStates(states: list = []) -> None
```

Setter for self.initial_states.

**Arguments**:

  -----------
  states : list or tuple
  Muskingum procedure function parameters to set (initial_output_q : float)

