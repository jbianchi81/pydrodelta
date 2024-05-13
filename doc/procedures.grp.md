# Table of Contents

* [pydrodelta.procedures.grp](#pydrodelta.procedures.grp)
  * [GRPProcedureFunction](#pydrodelta.procedures.grp.GRPProcedureFunction)
    * [X0](#pydrodelta.procedures.grp.GRPProcedureFunction.X0)
    * [X1](#pydrodelta.procedures.grp.GRPProcedureFunction.X1)
    * [X2](#pydrodelta.procedures.grp.GRPProcedureFunction.X2)
    * [X3](#pydrodelta.procedures.grp.GRPProcedureFunction.X3)
    * [windowsize](#pydrodelta.procedures.grp.GRPProcedureFunction.windowsize)
    * [rho](#pydrodelta.procedures.grp.GRPProcedureFunction.rho)
    * [wp](#pydrodelta.procedures.grp.GRPProcedureFunction.wp)
    * [ae](#pydrodelta.procedures.grp.GRPProcedureFunction.ae)
    * [Sk\_init](#pydrodelta.procedures.grp.GRPProcedureFunction.Sk_init)
    * [Rk\_init](#pydrodelta.procedures.grp.GRPProcedureFunction.Rk_init)
    * [dt](#pydrodelta.procedures.grp.GRPProcedureFunction.dt)
    * [alpha](#pydrodelta.procedures.grp.GRPProcedureFunction.alpha)
    * [UH1](#pydrodelta.procedures.grp.GRPProcedureFunction.UH1)
    * [SH1](#pydrodelta.procedures.grp.GRPProcedureFunction.SH1)
    * [update](#pydrodelta.procedures.grp.GRPProcedureFunction.update)
    * [\_\_init\_\_](#pydrodelta.procedures.grp.GRPProcedureFunction.__init__)
    * [createUnitHydrograph](#pydrodelta.procedures.grp.GRPProcedureFunction.createUnitHydrograph)
    * [run](#pydrodelta.procedures.grp.GRPProcedureFunction.run)
    * [advance\_step](#pydrodelta.procedures.grp.GRPProcedureFunction.advance_step)
    * [computeUnitHydrograph](#pydrodelta.procedures.grp.GRPProcedureFunction.computeUnitHydrograph)
    * [setParameters](#pydrodelta.procedures.grp.GRPProcedureFunction.setParameters)
    * [setInitialStates](#pydrodelta.procedures.grp.GRPProcedureFunction.setInitialStates)

<a id="pydrodelta.procedures.grp"></a>

# pydrodelta.procedures.grp

<a id="pydrodelta.procedures.grp.GRPProcedureFunction"></a>

## GRPProcedureFunction Objects

```python
class GRPProcedureFunction(PQProcedureFunction)
```

L'équipe du Cemagref a développé un logiciel de prévision hydrologique (GRP) pour le Service central d'hydrométéorologie et d'appui à la prévision des inondations (SCHAPI), conçu pour prédire les crues des cours d'eau. Les chercheurs expliquent que les observations et prévisions des précipitations du réseau Météo-France pour les bassins correspondants sont exploitées par le logiciel. L'indice d'humidité des sols est également un facteur pris en compte par le logiciel.

<a id="pydrodelta.procedures.grp.GRPProcedureFunction.X0"></a>

#### X0

```python
@property
def X0() -> float
```

capacite du reservoir de production (mm)

<a id="pydrodelta.procedures.grp.GRPProcedureFunction.X1"></a>

#### X1

```python
@property
def X1() -> float
```

capacite du reservoir de routage (mm)

<a id="pydrodelta.procedures.grp.GRPProcedureFunction.X2"></a>

#### X2

```python
@property
def X2() -> float
```

facteur de l'ajustement multiplicatif de la pluie efficace (sans dimension)

<a id="pydrodelta.procedures.grp.GRPProcedureFunction.X3"></a>

#### X3

```python
@property
def X3() -> float
```

temps de base de l'hydrogramme unitaire (d)

<a id="pydrodelta.procedures.grp.GRPProcedureFunction.windowsize"></a>

#### windowsize

```python
@property
def windowsize() -> int
```

time window size

<a id="pydrodelta.procedures.grp.GRPProcedureFunction.rho"></a>

#### rho

```python
@property
def rho() -> float
```

rho soil porosity [0-1]

<a id="pydrodelta.procedures.grp.GRPProcedureFunction.wp"></a>

#### wp

```python
@property
def wp() -> float
```

wp soil wilting point [0-1]

<a id="pydrodelta.procedures.grp.GRPProcedureFunction.ae"></a>

#### ae

```python
@property
def ae() -> float
```

ae effective area [0-1]

<a id="pydrodelta.procedures.grp.GRPProcedureFunction.Sk_init"></a>

#### Sk\_init

```python
@property
def Sk_init() -> float
```

Initial soil storage

<a id="pydrodelta.procedures.grp.GRPProcedureFunction.Rk_init"></a>

#### Rk\_init

```python
@property
def Rk_init() -> float
```

Initial routing storage

<a id="pydrodelta.procedures.grp.GRPProcedureFunction.dt"></a>

#### dt

```python
@property
def dt() -> float
```

computation step of the unit hydrograph

<a id="pydrodelta.procedures.grp.GRPProcedureFunction.alpha"></a>

#### alpha

```python
@property
def alpha() -> float
```

exponent of the unit hydrograph

<a id="pydrodelta.procedures.grp.GRPProcedureFunction.UH1"></a>

#### UH1

Pulses unit hydrograph

<a id="pydrodelta.procedures.grp.GRPProcedureFunction.SH1"></a>

#### SH1

Accumulated unit hidrigraph

<a id="pydrodelta.procedures.grp.GRPProcedureFunction.update"></a>

#### update

Update states with observed discharge

<a id="pydrodelta.procedures.grp.GRPProcedureFunction.__init__"></a>

#### \_\_init\_\_

```python
def __init__(parameters: Union[list, tuple, dict],
             initial_states: Union[list, tuple, dict] = [],
             update=False,
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

        update : bool = False

            Update model states when discharge observations are available
|
        \**kwargs : keyword arguments (see ProcedureFunction)

<a id="pydrodelta.procedures.grp.GRPProcedureFunction.createUnitHydrograph"></a>

#### createUnitHydrograph

```python
@staticmethod
def createUnitHydrograph(X3: float, alpha: float) -> Tuple[list, list]
```

Creates unit hydrograph

**Arguments**:

  -----------
  X3 : float
  Unit hydrograph base time
  
  alpha : float
  Unit hydrograph exponent
  

**Returns**:

  --------
  Tuple[list,list] : where first element is the pulses Unit hydrograph and the second is the accumulated unit hydrograph

<a id="pydrodelta.procedures.grp.GRPProcedureFunction.run"></a>

#### run

```python
def run(
    input: List[DataFrame] = None
) -> Tuple[List[DataFrame], ProcedureFunctionResults]
```

Ejecuta la función. Si input es None, ejecuta self._procedure.loadInput para generar el input. input debe ser una lista de objetos SeriesData
Devuelve una lista de objetos SeriesData y opcionalmente un objeto ProcedureFunctionResults

**Arguments**:

  -----------
  input : list of DataFrames
  Boundary conditions. If None, runs .loadInput
  

**Returns**:

  Tuple[List[DataFrame],ProcedureFunctionResults] : first element is the procedure function output (list of DataFrames), while second is a ProcedureFunctionResults object
  --------

<a id="pydrodelta.procedures.grp.GRPProcedureFunction.advance_step"></a>

#### advance\_step

```python
def advance_step(Sk: float,
                 Rk: float,
                 pma: float,
                 etp: float,
                 k: int,
                 q_obs=None
                 ) -> Tuple[float, float, float, float, float, float]
```

Advances model time step

**Arguments**:

  -----------
  Sk : float
  
  Soil Storage
  
  Rk : float
  
  Routing storage
  
  pma : float
  
  Mean areal precipitation
  
  etp : float
  
  Potential evapotranspiration
  
  k : int
  
  Time step index
  
  q_obs : float or None
  
  observed discharge
  

**Returns**:

  --------
  Tuple[float,float,float,float,float,float] : (Sk_, Rk_, Qk, Qr, self.X2*(Perc+Pn-Ps), R1 - R1**2/(R1+self.X1)

<a id="pydrodelta.procedures.grp.GRPProcedureFunction.computeUnitHydrograph"></a>

#### computeUnitHydrograph

```python
def computeUnitHydrograph(k: int) -> list
```

Compute unit hydrograph discharge for time step k

**Arguments**:

  -----------
  k : int
  
  Time step index
  

**Returns**:

  --------
  discharge : float

<a id="pydrodelta.procedures.grp.GRPProcedureFunction.setParameters"></a>

#### setParameters

```python
def setParameters(parameters: Union[list, tuple] = []) -> None
```

Setter for self.parameters.

**Arguments**:

  -----------
  parameters : list or tuple
  
  GRP parameters to set (X0,X1,X2,X3)

<a id="pydrodelta.procedures.grp.GRPProcedureFunction.setInitialStates"></a>

#### setInitialStates

```python
def setInitialStates(states: Union[list, tuple] = [])
```

Setter for self.initial_states.

**Arguments**:

  states : list or tuple
  
  GRP initial states to set (Sk,Rk)

