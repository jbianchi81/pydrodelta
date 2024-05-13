# Table of Contents

* [pydrodelta.procedures.sacramento\_simplified](#pydrodelta.procedures.sacramento_simplified)
  * [ParFg](#pydrodelta.procedures.sacramento_simplified.ParFg)
    * [\_\_init\_\_](#pydrodelta.procedures.sacramento_simplified.ParFg.__init__)
  * [SmTransform](#pydrodelta.procedures.sacramento_simplified.SmTransform)
    * [\_\_init\_\_](#pydrodelta.procedures.sacramento_simplified.SmTransform.__init__)
    * [toDict](#pydrodelta.procedures.sacramento_simplified.SmTransform.toDict)
  * [SacramentoSimplifiedProcedureFunction](#pydrodelta.procedures.sacramento_simplified.SacramentoSimplifiedProcedureFunction)
    * [x1\_0](#pydrodelta.procedures.sacramento_simplified.SacramentoSimplifiedProcedureFunction.x1_0)
    * [x2\_0](#pydrodelta.procedures.sacramento_simplified.SacramentoSimplifiedProcedureFunction.x2_0)
    * [m1](#pydrodelta.procedures.sacramento_simplified.SacramentoSimplifiedProcedureFunction.m1)
    * [c2](#pydrodelta.procedures.sacramento_simplified.SacramentoSimplifiedProcedureFunction.c2)
    * [c3](#pydrodelta.procedures.sacramento_simplified.SacramentoSimplifiedProcedureFunction.c3)
    * [mu](#pydrodelta.procedures.sacramento_simplified.SacramentoSimplifiedProcedureFunction.mu)
    * [alfa](#pydrodelta.procedures.sacramento_simplified.SacramentoSimplifiedProcedureFunction.alfa)
    * [m2](#pydrodelta.procedures.sacramento_simplified.SacramentoSimplifiedProcedureFunction.m2)
    * [m3](#pydrodelta.procedures.sacramento_simplified.SacramentoSimplifiedProcedureFunction.m3)
    * [windowsize](#pydrodelta.procedures.sacramento_simplified.SacramentoSimplifiedProcedureFunction.windowsize)
    * [dt\_sec](#pydrodelta.procedures.sacramento_simplified.SacramentoSimplifiedProcedureFunction.dt_sec)
    * [rho](#pydrodelta.procedures.sacramento_simplified.SacramentoSimplifiedProcedureFunction.rho)
    * [ae](#pydrodelta.procedures.sacramento_simplified.SacramentoSimplifiedProcedureFunction.ae)
    * [wp](#pydrodelta.procedures.sacramento_simplified.SacramentoSimplifiedProcedureFunction.wp)
    * [sm\_transform](#pydrodelta.procedures.sacramento_simplified.SacramentoSimplifiedProcedureFunction.sm_transform)
    * [x](#pydrodelta.procedures.sacramento_simplified.SacramentoSimplifiedProcedureFunction.x)
    * [par\_fg](#pydrodelta.procedures.sacramento_simplified.SacramentoSimplifiedProcedureFunction.par_fg)
    * [max\_npasos](#pydrodelta.procedures.sacramento_simplified.SacramentoSimplifiedProcedureFunction.max_npasos)
    * [no\_check1](#pydrodelta.procedures.sacramento_simplified.SacramentoSimplifiedProcedureFunction.no_check1)
    * [no\_check2](#pydrodelta.procedures.sacramento_simplified.SacramentoSimplifiedProcedureFunction.no_check2)
    * [rk2](#pydrodelta.procedures.sacramento_simplified.SacramentoSimplifiedProcedureFunction.rk2)
    * [volume](#pydrodelta.procedures.sacramento_simplified.SacramentoSimplifiedProcedureFunction.volume)
    * [sm\_obs](#pydrodelta.procedures.sacramento_simplified.SacramentoSimplifiedProcedureFunction.sm_obs)
    * [sm\_sim](#pydrodelta.procedures.sacramento_simplified.SacramentoSimplifiedProcedureFunction.sm_sim)
    * [mock\_run](#pydrodelta.procedures.sacramento_simplified.SacramentoSimplifiedProcedureFunction.mock_run)
    * [\_\_init\_\_](#pydrodelta.procedures.sacramento_simplified.SacramentoSimplifiedProcedureFunction.__init__)
    * [run](#pydrodelta.procedures.sacramento_simplified.SacramentoSimplifiedProcedureFunction.run)

<a id="pydrodelta.procedures.sacramento_simplified"></a>

# pydrodelta.procedures.sacramento\_simplified

<a id="pydrodelta.procedures.sacramento_simplified.ParFg"></a>

## ParFg Objects

```python
class ParFg()
```

Flood guidance parameters

<a id="pydrodelta.procedures.sacramento_simplified.ParFg.__init__"></a>

#### \_\_init\_\_

```python
def __init__(parameters: dict, area: float = None)
```

parameters : dict

    Properties:
    - CN2  
    - hp1dia
    - hp2dias
    - Qbanca

area : float = None

<a id="pydrodelta.procedures.sacramento_simplified.SmTransform"></a>

## SmTransform Objects

```python
class SmTransform()
```

Soil moisture linear transformation parameters

<a id="pydrodelta.procedures.sacramento_simplified.SmTransform.__init__"></a>

#### \_\_init\_\_

```python
def __init__(parameters: list)
```

parameters : list or tuple: [slope, intercept]

<a id="pydrodelta.procedures.sacramento_simplified.SmTransform.toDict"></a>

#### toDict

```python
def toDict() -> dict
```

Convert to dict

<a id="pydrodelta.procedures.sacramento_simplified.SacramentoSimplifiedProcedureFunction"></a>

## SacramentoSimplifiedProcedureFunction Objects

```python
class SacramentoSimplifiedProcedureFunction(PQProcedureFunction)
```

Simplified (10-parameter) Sacramento for precipitation - discharge transformation.

Reference: https://www.researchgate.net/publication/348234919_Implementacion_de_un_procedimiento_de_pronostico_hidrologico_para_el_alerta_de_inundaciones_utilizando_datos_de_sensores_remotos

<a id="pydrodelta.procedures.sacramento_simplified.SacramentoSimplifiedProcedureFunction.x1_0"></a>

#### x1\_0

```python
@property
def x1_0() -> float
```

top soil layer storage capacity [L]

<a id="pydrodelta.procedures.sacramento_simplified.SacramentoSimplifiedProcedureFunction.x2_0"></a>

#### x2\_0

```python
@property
def x2_0() -> float
```

bottom soil layer storage capacity [L]

<a id="pydrodelta.procedures.sacramento_simplified.SacramentoSimplifiedProcedureFunction.m1"></a>

#### m1

```python
@property
def m1() -> float
```

runoff function exponent [-]

<a id="pydrodelta.procedures.sacramento_simplified.SacramentoSimplifiedProcedureFunction.c2"></a>

#### c2

```python
@property
def c2() -> float
```

percolation function coefficient [-]

<a id="pydrodelta.procedures.sacramento_simplified.SacramentoSimplifiedProcedureFunction.c3"></a>

#### c3

```python
@property
def c3() -> float
```

base flow recession rate [1/T]

<a id="pydrodelta.procedures.sacramento_simplified.SacramentoSimplifiedProcedureFunction.mu"></a>

#### mu

```python
@property
def mu() -> float
```

base flow/deep percolation partition parameter [-]

<a id="pydrodelta.procedures.sacramento_simplified.SacramentoSimplifiedProcedureFunction.alfa"></a>

#### alfa

```python
@property
def alfa() -> float
```

linear reservoir coefficient [1/T]

<a id="pydrodelta.procedures.sacramento_simplified.SacramentoSimplifiedProcedureFunction.m2"></a>

#### m2

```python
@property
def m2() -> float
```

percolation function exponent [-]

<a id="pydrodelta.procedures.sacramento_simplified.SacramentoSimplifiedProcedureFunction.m3"></a>

#### m3

```python
@property
def m3() -> float
```

evapotranspiration function exponent [-]

<a id="pydrodelta.procedures.sacramento_simplified.SacramentoSimplifiedProcedureFunction.windowsize"></a>

#### windowsize

```python
@property
def windowsize() -> int
```

Window size for soil moisture adjustment

<a id="pydrodelta.procedures.sacramento_simplified.SacramentoSimplifiedProcedureFunction.dt_sec"></a>

#### dt\_sec

```python
@property
def dt_sec() -> int
```

Time step in seconds

<a id="pydrodelta.procedures.sacramento_simplified.SacramentoSimplifiedProcedureFunction.rho"></a>

#### rho

```python
@property
def rho() -> float
```

Soil porosity

<a id="pydrodelta.procedures.sacramento_simplified.SacramentoSimplifiedProcedureFunction.ae"></a>

#### ae

```python
@property
def ae() -> float
```

Effective area of runnof generation [0-1]

<a id="pydrodelta.procedures.sacramento_simplified.SacramentoSimplifiedProcedureFunction.wp"></a>

#### wp

```python
@property
def wp() -> float
```

Wilting point

<a id="pydrodelta.procedures.sacramento_simplified.SacramentoSimplifiedProcedureFunction.sm_transform"></a>

#### sm\_transform

```python
@property
def sm_transform() -> SmTransform
```

soil moisture rescaling parameters (scale, bias)

<a id="pydrodelta.procedures.sacramento_simplified.SacramentoSimplifiedProcedureFunction.x"></a>

#### x

```python
@property
def x() -> list
```

Model states (x1,x2,x3,x4)

<a id="pydrodelta.procedures.sacramento_simplified.SacramentoSimplifiedProcedureFunction.par_fg"></a>

#### par\_fg

```python
@property
def par_fg() -> dict
```

Flood guidance parameters

<a id="pydrodelta.procedures.sacramento_simplified.SacramentoSimplifiedProcedureFunction.max_npasos"></a>

#### max\_npasos

```python
@property
def max_npasos() -> int
```

Maximum substeps for model computations

<a id="pydrodelta.procedures.sacramento_simplified.SacramentoSimplifiedProcedureFunction.no_check1"></a>

#### no\_check1

```python
@property
def no_check1() -> bool
```

Perform step subdivision based on precipitation intensity nsteps = pma/2  (for numerical stability)

<a id="pydrodelta.procedures.sacramento_simplified.SacramentoSimplifiedProcedureFunction.no_check2"></a>

#### no\_check2

```python
@property
def no_check2() -> bool
```

Perform step subdivision based on states derivatives (for numerical stability)

<a id="pydrodelta.procedures.sacramento_simplified.SacramentoSimplifiedProcedureFunction.rk2"></a>

#### rk2

```python
@property
def rk2() -> bool
```

Use Runge-Kutta-2 instead of Runge-Kutta-4

<a id="pydrodelta.procedures.sacramento_simplified.SacramentoSimplifiedProcedureFunction.volume"></a>

#### volume

Water balance

<a id="pydrodelta.procedures.sacramento_simplified.SacramentoSimplifiedProcedureFunction.sm_obs"></a>

#### sm\_obs

Soil moisture observations

<a id="pydrodelta.procedures.sacramento_simplified.SacramentoSimplifiedProcedureFunction.sm_sim"></a>

#### sm\_sim

Simulated soil moisture

<a id="pydrodelta.procedures.sacramento_simplified.SacramentoSimplifiedProcedureFunction.mock_run"></a>

#### mock\_run

```python
@property
def mock_run() -> bool
```

Perform mock run

<a id="pydrodelta.procedures.sacramento_simplified.SacramentoSimplifiedProcedureFunction.__init__"></a>

#### \_\_init\_\_

```python
def __init__(parameters: Union[dict, list, tuple], initial_states: list,
             **kwargs)
```

parameters : Union[dict,list,tuple]

    Properties:
    - x1_0 : float
        top soil layer storage capacity [L]
    - x2_0 : float
        bottom soil layer storage capacity [L]
    - m1 : float
        runoff function exponent [-]
    - c1 : float
        interflow function coefficient [1/T]        
    - c2 : float
        percolation function coefficient [-]        
    - c3 : float
        base flow recession rate [1/T]        
    - mu : float
        base flow/deep percolation partition parameter [-]        
    - alfa : float
        linear reservoir coefficient [1/T]        
    - m2 : float
        percolation function exponent [-]        
    - m3
        evapotranspiration function exponent [-]

extra_pars : Union[dict,list,tuple]

    - windowsize : int
        Window size for soil moisture adjustment        
    - dt_sec : int
        Time step in seconds        
    - rho : float
        Soil porosity        
    - ae : float
        Effective area of runnof generation [0-1]        
    - wp : float
        Wilting point        
    - sm_transform : tuple
        soil moisture rescaling parameters (scale, bias)
    - par_fg : dict
        Flood guidance parameters
    - max_npasos : int
        Maximum substeps for model computations        
    - no_check1 : bool
        Perform step subdivision based on precipitation intensity nsteps = pma/2  (for numerical stability)        
    - no_check2 : bool
        Perform step subdivision based on states derivatives (for numerical stability)        
    - rk2 : bool
        Use Runge-Kutta-2 instead of Runge-Kutta-4

initial_states : list

        Initial model states (x1,x2,x3,x4)

<a id="pydrodelta.procedures.sacramento_simplified.SacramentoSimplifiedProcedureFunction.run"></a>

#### run

```python
def run(
    input: Optional[DataFrame] = None
) -> Tuple[List[SeriesData], ProcedureFunctionResults]
```

Ejecuta la función. Si input es None, ejecuta self._procedure.loadInput para generar el input. input debe ser una lista de objetos SeriesData
Devuelve una lista de objetos SeriesData y opcionalmente un objeto ProcedureFunctionResults

