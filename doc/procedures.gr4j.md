# Table of Contents

* [pydrodelta.procedures.gr4j](#pydrodelta.procedures.gr4j)
  * [GR4JProcedureFunction](#pydrodelta.procedures.gr4j.GR4JProcedureFunction)
    * [X0](#pydrodelta.procedures.gr4j.GR4JProcedureFunction.X0)
    * [X1](#pydrodelta.procedures.gr4j.GR4JProcedureFunction.X1)
    * [X2](#pydrodelta.procedures.gr4j.GR4JProcedureFunction.X2)
    * [X3](#pydrodelta.procedures.gr4j.GR4JProcedureFunction.X3)
    * [Sk\_init](#pydrodelta.procedures.gr4j.GR4JProcedureFunction.Sk_init)
    * [Rk\_init](#pydrodelta.procedures.gr4j.GR4JProcedureFunction.Rk_init)
    * [dt](#pydrodelta.procedures.gr4j.GR4JProcedureFunction.dt)
    * [engine](#pydrodelta.procedures.gr4j.GR4JProcedureFunction.engine)
    * [\_\_init\_\_](#pydrodelta.procedures.gr4j.GR4JProcedureFunction.__init__)
    * [run](#pydrodelta.procedures.gr4j.GR4JProcedureFunction.run)
    * [setEngine](#pydrodelta.procedures.gr4j.GR4JProcedureFunction.setEngine)
    * [setParameters](#pydrodelta.procedures.gr4j.GR4JProcedureFunction.setParameters)
    * [setInitialStates](#pydrodelta.procedures.gr4j.GR4JProcedureFunction.setInitialStates)

<a id="pydrodelta.procedures.gr4j"></a>

# pydrodelta.procedures.gr4j

<a id="pydrodelta.procedures.gr4j.GR4JProcedureFunction"></a>

## GR4JProcedureFunction Objects

```python
class GR4JProcedureFunction(PQProcedureFunction)
```

Modelo Operacional de Transformación de Precipitación en Escorrentía de Ingeniería Rural de 4 parámetros (CEMAGREF). A diferencia de la versión original, la convolución se realiza mediante producto de matrices. Parámetros: Máximo almacenamiento en reservorio de producción, tiempo al pico (hidrograma unitario),máximo almacenamiento en reservorio de propagación, coeficiente de intercambio.

<a id="pydrodelta.procedures.gr4j.GR4JProcedureFunction.X0"></a>

#### X0

```python
@property
def X0() -> float
```

capacite du reservoir de production (mm)

<a id="pydrodelta.procedures.gr4j.GR4JProcedureFunction.X1"></a>

#### X1

```python
@property
def X1() -> float
```

capacite du reservoir de routage (mm)

<a id="pydrodelta.procedures.gr4j.GR4JProcedureFunction.X2"></a>

#### X2

```python
@property
def X2() -> float
```

facteur de l'ajustement multiplicatif de la pluie efficace (sans dimension)

<a id="pydrodelta.procedures.gr4j.GR4JProcedureFunction.X3"></a>

#### X3

```python
@property
def X3() -> float
```

temps de base de l'hydrogramme unitaire (d)

<a id="pydrodelta.procedures.gr4j.GR4JProcedureFunction.Sk_init"></a>

#### Sk\_init

```python
@property
def Sk_init() -> float
```

Initial soil storage

<a id="pydrodelta.procedures.gr4j.GR4JProcedureFunction.Rk_init"></a>

#### Rk\_init

```python
@property
def Rk_init() -> float
```

Initial routing storage

<a id="pydrodelta.procedures.gr4j.GR4JProcedureFunction.dt"></a>

#### dt

```python
@property
def dt() -> float
```

Time step duration [days]

<a id="pydrodelta.procedures.gr4j.GR4JProcedureFunction.engine"></a>

#### engine

```python
@property
def engine() -> GR4J
```

Reference to instance of GR4J procedure engine

<a id="pydrodelta.procedures.gr4j.GR4JProcedureFunction.__init__"></a>

#### \_\_init\_\_

```python
def __init__(parameters: Union[list, tuple, dict],
             initial_states: Union[list, tuple, dict] = None,
             extra_pars: dict = None,
             **kwargs)
```

parameters : list or tuple or dict

            If list or tuple: (X0 : float, X1 : float, X2 : float, X3 : float)

            If dict: {"X0": float, "X1": float, "X2": float, "X3": float}

            Where:
            - X0:	capacite du reservoir de production (mm)
            - X1:	capacite du reservoir de routage (mm)
            - X2:	facteur de l'ajustement multiplicatif de la pluie efficace (sans dimension)
            - X3:	temps de base de l'hydrogramme unitaire (d)

        initial_states: list, tuple or dict

            If list or tuple: (Sk_init : float, Rk_init : float)

            If dict: {"Sk_init": float, "Rk_init": float}

            where:
            - Sk_init: Initial soil storage [mm]
            - Rk_init: Initial routing storage [mm]

        extra_pars : dict = None

            Additional, non-calibratable parameters

            Properties:
            - dt : float

                Time step duration (days, default 1)
|
        \**kwargs : keyword arguments (see ProcedureFunction)

<a id="pydrodelta.procedures.gr4j.GR4JProcedureFunction.run"></a>

#### run

```python
def run(input: List[DataFrame] = None) -> Tuple[list, dict]
```

Runs the procedure function.

**Arguments**:

  -----------
  
  input : List[DataFrame] = None
  
  If input is None, it loads the boundaries. Else, input must be a list of DataFrames
  

**Returns**:

  --------
  
  Tuple[List[DataFrame], ProcedureFunctionResults]
  
  Devuelve una lista de DataFrames (uno por output del procedimiento) y opcionalmente un objeto ProcedureFunctionResults

<a id="pydrodelta.procedures.gr4j.GR4JProcedureFunction.setEngine"></a>

#### setEngine

```python
def setEngine(input: List[Tuple[float, float]]) -> None
```

Instantiate GR4J procedure engine using input as Boundaries

**Arguments**:

  input : List[Tuple[float,float]] - Boundary conditions: list of (pmad : float, etpd : float)

<a id="pydrodelta.procedures.gr4j.GR4JProcedureFunction.setParameters"></a>

#### setParameters

```python
def setParameters(parameters: Union[list, tuple] = []) -> None
```

Set parameters from ordered list

**Arguments**:

  -----------
  parameters : Union[list, tuple] = []
  
  (X0 : float, X1 : float, X2 : float, X3 : float)
  
  Where:
  - X0:	capacite du reservoir de production (mm)
  - X1:	capacite du reservoir de routage (mm)
  - X2:	facteur de l'ajustement multiplicatif de la pluie efficace (sans dimension)
  - X3:	temps de base de l'hydrogramme unitaire (d)

<a id="pydrodelta.procedures.gr4j.GR4JProcedureFunction.setInitialStates"></a>

#### setInitialStates

```python
def setInitialStates(states: Union[list, tuple] = [])
```

Set initial states from ordered list

**Arguments**:

  -----------
  states : Union[list, tuple] = []
  
  (Sk_init : float, Rk_init : float)
  
  where:
  - Sk_init: Initial soil storage [mm]
  - Rk_init: Initial routing storage [mm]

