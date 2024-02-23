# Table of Contents

* [pydrodelta.procedures.hosh4p1l](#pydrodelta.procedures.hosh4p1l)
  * [HOSH4P1LProcedureFunction](#pydrodelta.procedures.hosh4p1l.HOSH4P1LProcedureFunction)
    * [maxSurfaceStorage](#pydrodelta.procedures.hosh4p1l.HOSH4P1LProcedureFunction.maxSurfaceStorage)
    * [maxSoilStorage](#pydrodelta.procedures.hosh4p1l.HOSH4P1LProcedureFunction.maxSoilStorage)
    * [Proc](#pydrodelta.procedures.hosh4p1l.HOSH4P1LProcedureFunction.Proc)
    * [T](#pydrodelta.procedures.hosh4p1l.HOSH4P1LProcedureFunction.T)
    * [distribution](#pydrodelta.procedures.hosh4p1l.HOSH4P1LProcedureFunction.distribution)
    * [dt](#pydrodelta.procedures.hosh4p1l.HOSH4P1LProcedureFunction.dt)
    * [shift](#pydrodelta.procedures.hosh4p1l.HOSH4P1LProcedureFunction.shift)
    * [approx](#pydrodelta.procedures.hosh4p1l.HOSH4P1LProcedureFunction.approx)
    * [k](#pydrodelta.procedures.hosh4p1l.HOSH4P1LProcedureFunction.k)
    * [n](#pydrodelta.procedures.hosh4p1l.HOSH4P1LProcedureFunction.n)
    * [SurfaceStorage](#pydrodelta.procedures.hosh4p1l.HOSH4P1LProcedureFunction.SurfaceStorage)
    * [SoilStorage](#pydrodelta.procedures.hosh4p1l.HOSH4P1LProcedureFunction.SoilStorage)
    * [engine](#pydrodelta.procedures.hosh4p1l.HOSH4P1LProcedureFunction.engine)
    * [setEngine](#pydrodelta.procedures.hosh4p1l.HOSH4P1LProcedureFunction.setEngine)
    * [\_\_init\_\_](#pydrodelta.procedures.hosh4p1l.HOSH4P1LProcedureFunction.__init__)
    * [run](#pydrodelta.procedures.hosh4p1l.HOSH4P1LProcedureFunction.run)
    * [setInitialStates](#pydrodelta.procedures.hosh4p1l.HOSH4P1LProcedureFunction.setInitialStates)

<a id="pydrodelta.procedures.hosh4p1l"></a>

# pydrodelta.procedures.hosh4p1l

<a id="pydrodelta.procedures.hosh4p1l.HOSH4P1LProcedureFunction"></a>

## HOSH4P1LProcedureFunction Objects

```python
class HOSH4P1LProcedureFunction(PQProcedureFunction)
```

Modelo Operacional de Transformación de Precipitación en Escorrentía de 4 parámetros (estimables). Hidrología Operativa Síntesis de Hidrograma. Método NRCS, perfil de suelo con 2 reservorios de retención (sin efecto de base).

<a id="pydrodelta.procedures.hosh4p1l.HOSH4P1LProcedureFunction.maxSurfaceStorage"></a>

#### maxSurfaceStorage

```python
@property
def maxSurfaceStorage() -> float
```

Maximum surface storage (model parameter)

<a id="pydrodelta.procedures.hosh4p1l.HOSH4P1LProcedureFunction.maxSoilStorage"></a>

#### maxSoilStorage

```python
@property
def maxSoilStorage() -> float
```

Maximum soil storage (model parameter)

<a id="pydrodelta.procedures.hosh4p1l.HOSH4P1LProcedureFunction.Proc"></a>

#### Proc

```python
@property
def Proc() -> str
```

Routing procedure (model parameter)

<a id="pydrodelta.procedures.hosh4p1l.HOSH4P1LProcedureFunction.T"></a>

#### T

```python
@property
def T() -> float
```

Triangular hydrogram time to peak (model parameter)

<a id="pydrodelta.procedures.hosh4p1l.HOSH4P1LProcedureFunction.distribution"></a>

#### distribution

```python
@property
def distribution() -> str
```

Triangular hydrogram distribution (model parameter)

<a id="pydrodelta.procedures.hosh4p1l.HOSH4P1LProcedureFunction.dt"></a>

#### dt

```python
@property
def dt() -> float
```

Computation step (procedure configuration)

<a id="pydrodelta.procedures.hosh4p1l.HOSH4P1LProcedureFunction.shift"></a>

#### shift

```python
@property
def shift() -> bool
```

shift (procedure configuration)

<a id="pydrodelta.procedures.hosh4p1l.HOSH4P1LProcedureFunction.approx"></a>

#### approx

```python
@property
def approx() -> bool
```

approx (procedure configuration)

<a id="pydrodelta.procedures.hosh4p1l.HOSH4P1LProcedureFunction.k"></a>

#### k

```python
@property
def k() -> float
```

Nash linear channel coefficient k (model parameter)

<a id="pydrodelta.procedures.hosh4p1l.HOSH4P1LProcedureFunction.n"></a>

#### n

```python
@property
def n() -> float
```

Nash linear channel number of reservoirs n (model parameter)

<a id="pydrodelta.procedures.hosh4p1l.HOSH4P1LProcedureFunction.SurfaceStorage"></a>

#### SurfaceStorage

```python
@property
def SurfaceStorage() -> float
```

Initial surface storage [mm] (model initial state)

<a id="pydrodelta.procedures.hosh4p1l.HOSH4P1LProcedureFunction.SoilStorage"></a>

#### SoilStorage

```python
@property
def SoilStorage() -> float
```

Initial soil storage [mm] (model initial state)

<a id="pydrodelta.procedures.hosh4p1l.HOSH4P1LProcedureFunction.engine"></a>

#### engine

```python
@property
def engine() -> HOSH4P1L
```

Reference to the hydrologic procedure engine (see ..pydrology.HOSH4P1L)

<a id="pydrodelta.procedures.hosh4p1l.HOSH4P1LProcedureFunction.setEngine"></a>

#### setEngine

```python
def setEngine(input: list) -> None
```

Set HOSH4P1L procedure engine

**Arguments**:

  input : list - boundary conditions: list of (pmad, etpd)

<a id="pydrodelta.procedures.hosh4p1l.HOSH4P1LProcedureFunction.__init__"></a>

#### \_\_init\_\_

```python
def __init__(parameters: Union[list, tuple,
                               dict], extra_pars: Union[list, tuple, dict],
             initial_states: Union[list, tuple, dict], **kwargs)
```

parameters  : Union[list,tuple,dict]

    Ordered list or dict

    Properties:
    - maxSurfaceStorage
    - maxSoilStorage
    - Proc (optional, default "UH")
    - T (optional, default None)
    - distribution (optional, default "Symmetric")
    - k (optional, default None)
    - n (optional, default None)

<a id="pydrodelta.procedures.hosh4p1l.HOSH4P1LProcedureFunction.run"></a>

#### run

```python
def run(
    input: list[DataFrame] = None
) -> tuple[List[DataFrame], ProcedureFunctionResults]
```

Run the function procedure

**Arguments**:

  -----------
  input : list of DataFrames
  Boundary conditions. If None, runs .loadInput
  

**Returns**:

  tuple[List[DataFrame],ProcedureFunctionResults] : first element is the procedure function output (list of DataFrames), while second is a ProcedureFunctionResults object

<a id="pydrodelta.procedures.hosh4p1l.HOSH4P1LProcedureFunction.setInitialStates"></a>

#### setInitialStates

```python
def setInitialStates(states: Union[list, tuple] = []) -> None
```

Initial states setter

**Arguments**:

  -----------
- `states` - Union[list,tuple]
  
  (SurfaceStorage : float, SoilStorage : float)

