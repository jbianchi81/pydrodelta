# Table of Contents

* [pydrodelta.procedures.linear\_net\_3](#pydrodelta.procedures.linear_net_3)
  * [LinearNet3ProcedureFunction](#pydrodelta.procedures.linear_net_3.LinearNet3ProcedureFunction)
    * [coefficients](#pydrodelta.procedures.linear_net_3.LinearNet3ProcedureFunction.coefficients)
    * [Proc](#pydrodelta.procedures.linear_net_3.LinearNet3ProcedureFunction.Proc)
    * [dt](#pydrodelta.procedures.linear_net_3.LinearNet3ProcedureFunction.dt)
    * [\_\_init\_\_](#pydrodelta.procedures.linear_net_3.LinearNet3ProcedureFunction.__init__)
    * [run](#pydrodelta.procedures.linear_net_3.LinearNet3ProcedureFunction.run)

<a id="pydrodelta.procedures.linear_net_3"></a>

# pydrodelta.procedures.linear\_net\_3

<a id="pydrodelta.procedures.linear_net_3.LinearNet3ProcedureFunction"></a>

## LinearNet3ProcedureFunction Objects

```python
class LinearNet3ProcedureFunction(ProcedureFunction)
```

LinearNet procedure function with 3 input nodes. See ..pydrology.LinearNet

<a id="pydrodelta.procedures.linear_net_3.LinearNet3ProcedureFunction.coefficients"></a>

#### coefficients

```python
@property
def coefficients()
```

Linear net coefficients (list of 2-tuples)

<a id="pydrodelta.procedures.linear_net_3.LinearNet3ProcedureFunction.Proc"></a>

#### Proc

```python
@property
def Proc()
```

Fixed: Nash

<a id="pydrodelta.procedures.linear_net_3.LinearNet3ProcedureFunction.dt"></a>

#### dt

computation time step

<a id="pydrodelta.procedures.linear_net_3.LinearNet3ProcedureFunction.__init__"></a>

#### \_\_init\_\_

```python
def __init__(parameters: dict, **kwargs)
```

/**kwargs : keyword arguments

Keyword arguments:
------------------
extra_pars : dict
    properties:
    dt : float 
        calculation timestep

<a id="pydrodelta.procedures.linear_net_3.LinearNet3ProcedureFunction.run"></a>

#### run

```python
def run(input: list = None) -> tuple
```

Ejecuta la función. Si input es None, ejecuta self._procedure.loadInput para generar el input. input debe ser una lista de objetos SeriesData
Devuelve una lista de objetos SeriesData y opcionalmente un objeto ProcedureFunctionResults

**Arguments**:

  -----------
  input : list of DataFrames
  Procedure function input (boundary conditions). If None, loads using .loadInput()
  

**Returns**:

  --------
  2-tuple : first element is the procedure function output (list of DataFrames), while second is a ProcedureFunctionResults object

