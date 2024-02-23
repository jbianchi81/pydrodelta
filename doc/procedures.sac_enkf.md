# Table of Contents

* [pydrodelta.procedures.sac\_enkf](#pydrodelta.procedures.sac_enkf)
  * [SacEnkfProcedureFunction](#pydrodelta.procedures.sac_enkf.SacEnkfProcedureFunction)
    * [p\_stddev](#pydrodelta.procedures.sac_enkf.SacEnkfProcedureFunction.p_stddev)
    * [pet\_stddev](#pydrodelta.procedures.sac_enkf.SacEnkfProcedureFunction.pet_stddev)
    * [x\_stddev](#pydrodelta.procedures.sac_enkf.SacEnkfProcedureFunction.x_stddev)
    * [var\_innov](#pydrodelta.procedures.sac_enkf.SacEnkfProcedureFunction.var_innov)
    * [trim\_sm](#pydrodelta.procedures.sac_enkf.SacEnkfProcedureFunction.trim_sm)
    * [Rqobs](#pydrodelta.procedures.sac_enkf.SacEnkfProcedureFunction.Rqobs)
    * [asim](#pydrodelta.procedures.sac_enkf.SacEnkfProcedureFunction.asim)
    * [update](#pydrodelta.procedures.sac_enkf.SacEnkfProcedureFunction.update)
    * [xpert](#pydrodelta.procedures.sac_enkf.SacEnkfProcedureFunction.xpert)
    * [replicates](#pydrodelta.procedures.sac_enkf.SacEnkfProcedureFunction.replicates)
    * [ens](#pydrodelta.procedures.sac_enkf.SacEnkfProcedureFunction.ens)
    * [ens1](#pydrodelta.procedures.sac_enkf.SacEnkfProcedureFunction.ens1)
    * [ens2](#pydrodelta.procedures.sac_enkf.SacEnkfProcedureFunction.ens2)
    * [H](#pydrodelta.procedures.sac_enkf.SacEnkfProcedureFunction.H)
    * [\_\_init\_\_](#pydrodelta.procedures.sac_enkf.SacEnkfProcedureFunction.__init__)
    * [xnoise](#pydrodelta.procedures.sac_enkf.SacEnkfProcedureFunction.xnoise)
    * [cero](#pydrodelta.procedures.sac_enkf.SacEnkfProcedureFunction.cero)
    * [media](#pydrodelta.procedures.sac_enkf.SacEnkfProcedureFunction.media)
    * [media1](#pydrodelta.procedures.sac_enkf.SacEnkfProcedureFunction.media1)
    * [covarianza](#pydrodelta.procedures.sac_enkf.SacEnkfProcedureFunction.covarianza)
    * [q](#pydrodelta.procedures.sac_enkf.SacEnkfProcedureFunction.q)
    * [linfit](#pydrodelta.procedures.sac_enkf.SacEnkfProcedureFunction.linfit)
    * [advance\_step\_and\_pert](#pydrodelta.procedures.sac_enkf.SacEnkfProcedureFunction.advance_step_and_pert)
    * [pertX](#pydrodelta.procedures.sac_enkf.SacEnkfProcedureFunction.pertX)
    * [setH](#pydrodelta.procedures.sac_enkf.SacEnkfProcedureFunction.setH)
    * [setInitialEnsemble](#pydrodelta.procedures.sac_enkf.SacEnkfProcedureFunction.setInitialEnsemble)
    * [getC](#pydrodelta.procedures.sac_enkf.SacEnkfProcedureFunction.getC)
    * [getR](#pydrodelta.procedures.sac_enkf.SacEnkfProcedureFunction.getR)
    * [getKG](#pydrodelta.procedures.sac_enkf.SacEnkfProcedureFunction.getKG)
    * [asimila](#pydrodelta.procedures.sac_enkf.SacEnkfProcedureFunction.asimila)
    * [resultsDF](#pydrodelta.procedures.sac_enkf.SacEnkfProcedureFunction.resultsDF)
    * [newResultsRow](#pydrodelta.procedures.sac_enkf.SacEnkfProcedureFunction.newResultsRow)

<a id="pydrodelta.procedures.sac_enkf"></a>

# pydrodelta.procedures.sac\_enkf

<a id="pydrodelta.procedures.sac_enkf.SacEnkfProcedureFunction"></a>

## SacEnkfProcedureFunction Objects

```python
class SacEnkfProcedureFunction(sac.SacramentoSimplifiedProcedureFunction)
```

Simplified (10-parameter) Sacramento for precipitation - discharge transformation - ensemble with data assimilation.

Reference: https://www.researchgate.net/publication/348234919_Implementacion_de_un_procedimiento_de_pronostico_hidrologico_para_el_alerta_de_inundaciones_utilizando_datos_de_sensores_remotos

<a id="pydrodelta.procedures.sac_enkf.SacEnkfProcedureFunction.p_stddev"></a>

#### p\_stddev

```python
@property
def p_stddev() -> float
```

Standard deviation of the error of input precipitation

<a id="pydrodelta.procedures.sac_enkf.SacEnkfProcedureFunction.pet_stddev"></a>

#### pet\_stddev

```python
@property
def pet_stddev() -> float
```

Standard deviation of the error of input potential evapotranspiration

<a id="pydrodelta.procedures.sac_enkf.SacEnkfProcedureFunction.x_stddev"></a>

#### x\_stddev

```python
@property
def x_stddev() -> float
```

Standard deviation of the model states

<a id="pydrodelta.procedures.sac_enkf.SacEnkfProcedureFunction.var_innov"></a>

#### var\_innov

```python
@property
def var_innov() -> tuple[Union[str, float], Union[str, float]]
```

variance of the innovations (observation error): soil moisture (first element) and discharge (second element). If second element is 'rule', get variance of discharge from the rule defined in self.Rqobs

<a id="pydrodelta.procedures.sac_enkf.SacEnkfProcedureFunction.trim_sm"></a>

#### trim\_sm

```python
@property
def trim_sm() -> tuple[bool, bool]
```

2-tuple of bool. Option to trim soil moisture observations at the low (wilting point, self.wf) and high (soil porosity, self.rho) values, respectively

<a id="pydrodelta.procedures.sac_enkf.SacEnkfProcedureFunction.Rqobs"></a>

#### Rqobs

```python
@property
def Rqobs() -> list[tuple[float, float, float]]
```

Rule to determine observed discharge error variance as a function of the observed value. Ordered list of (threshold, bias, variance)

<a id="pydrodelta.procedures.sac_enkf.SacEnkfProcedureFunction.asim"></a>

#### asim

```python
@property
def asim() -> tuple[str, str]
```

2-tuple of str or None. Option to assimilate soil moisture and discharge, respectively

<a id="pydrodelta.procedures.sac_enkf.SacEnkfProcedureFunction.update"></a>

#### update

```python
@property
def update() -> tuple[str, str, str, str]
```

4-tuple of str or None. Option to correct model states via data assimilation (x1, x2, x3, x4)

<a id="pydrodelta.procedures.sac_enkf.SacEnkfProcedureFunction.xpert"></a>

#### xpert

```python
@property
def xpert() -> bool
```

Option to add noise to model states at the beginning of each step

<a id="pydrodelta.procedures.sac_enkf.SacEnkfProcedureFunction.replicates"></a>

#### replicates

```python
@property
def replicates() -> int
```

Number of ensemble members

<a id="pydrodelta.procedures.sac_enkf.SacEnkfProcedureFunction.ens"></a>

#### ens

Ensemble of model states (length = len(self.replicates) list of 4-tuples)

<a id="pydrodelta.procedures.sac_enkf.SacEnkfProcedureFunction.ens1"></a>

#### ens1

Ensemble of model states without data assimilation in the last step (length = len(self.replicates) list of 4-tuples)

<a id="pydrodelta.procedures.sac_enkf.SacEnkfProcedureFunction.ens2"></a>

#### ens2

Ensemble of model states without data assimilation in the last 2 steps (length = len(self.replicates) list of 4-tuples)

<a id="pydrodelta.procedures.sac_enkf.SacEnkfProcedureFunction.H"></a>

#### H

The states transformation matrix

<a id="pydrodelta.procedures.sac_enkf.SacEnkfProcedureFunction.__init__"></a>

#### \_\_init\_\_

```python
def __init__(extra_pars: dict = dict(), **kwargs)
```

extra_pars : dict = dict()

    Properties:
    - p_stddev : float - Standard deviation of the error of input precipitation
    - pet_stddev : float - Standard deviation of the error of input potential evapotranspiration
    - x_stddev : float - Standard deviation of the model states
    - var_innov : tuple - variance of the innovations (observation error): soil moisture (first element) and discharge (second element). If second element is 'rule', get variance of discharge from the rule defined in self.Rqobs
    - trim_sm : tuple - 2-tuple of bool. Option to trim soil moisture observations at the low (wilting point, self.wf) and high (soil porosity, self.rho) values, respectively
    - rule : list[tuple[float,float,float]] - Rule to determine observed discharge error variance as a function of the observed value. Ordered list of (threshold, bias, variance)
    - asim : 2-tuple of str or None - Option to assimilate soil moisture and discharge, respectively
    - update : 4-tuple or str or None - Option to correct model states via data assimilation (x1, x2, x3, x4)
    - xpert : bool - Option to add noise to model states at the beginning of each step
    - replicates : int - Number of ensemble members

<a id="pydrodelta.procedures.sac_enkf.SacEnkfProcedureFunction.xnoise"></a>

#### xnoise

```python
def xnoise(value: float, statename: str) -> float
```

Get product of value with a random normal of mean 0, scale = self.x_stddev

The result is constrained to the valid range of range the model state variable

**Arguments**:

  -----------
  value : float
  Input value of the model state
  
  statename : str
  Name of the model state variable (one of x1, x2, x3, x4)

<a id="pydrodelta.procedures.sac_enkf.SacEnkfProcedureFunction.cero"></a>

#### cero

```python
def cero(value: float, max: float) -> float
```

Return max(0, min(value, max))

**Arguments**:

  -----------
  value : float
  
  max : float
  

**Returns**:

  --------
  float

<a id="pydrodelta.procedures.sac_enkf.SacEnkfProcedureFunction.media"></a>

#### media

```python
def media(index: int) -> Tuple[float, float, float]
```

Get the ensemble mean of the model state variable of the selected index for each ensemble (self.ens, self.ens1, self.ens2)

**Arguments**:

  -----------
  index : 0 <= int <= 3
  

**Returns**:

  --------
  mean of ensemble 0 (self.ens) : float
  mean of ensemble 1 (self.ens1) : float
  mean of ensemble 2 (self.ens2) : float

<a id="pydrodelta.procedures.sac_enkf.SacEnkfProcedureFunction.media1"></a>

#### media1

```python
def media1(index: int) -> float
```

Get the ensemble mean of the model state variable of the selected index

**Arguments**:

  -----------
  index : 0 <= int <= 3
  

**Returns**:

  --------
  float

<a id="pydrodelta.procedures.sac_enkf.SacEnkfProcedureFunction.covarianza"></a>

#### covarianza

```python
def covarianza(index_1: int, index_2: int) -> float
```

Get ensemble covariance between model state variables of index_1 and index_2

**Arguments**:

  -----------
  index_1 : 0 <= int <= 3
  
- `index_2` - 0 <= int <= 3
  

**Returns**:

  --------
  float

<a id="pydrodelta.procedures.sac_enkf.SacEnkfProcedureFunction.q"></a>

#### q

```python
def q(value: float) -> Tuple[float, float]
```

Get variance and bias for the given value of discharge, according the mapping at self.Rqobs

**Arguments**:

  -----------
  value :float
  

**Returns**:

  --------
  variance : float
  
  bias : float

<a id="pydrodelta.procedures.sac_enkf.SacEnkfProcedureFunction.linfit"></a>

#### linfit

```python
def linfit(wsize: int, value: float) -> float
```

Adjust soil moisture value with a linear regression of the error of simulated vs observed values in a time step window of wsize

**Arguments**:

  -----------
  wsize : int
  
  value : float
  

**Returns**:

  --------
  float

<a id="pydrodelta.procedures.sac_enkf.SacEnkfProcedureFunction.advance_step_and_pert"></a>

#### advance\_step\_and\_pert

```python
def advance_step_and_pert(x: list, pma: float, etp: float) -> Tuple[list, int]
```

Advance model step and (where self.xpert is set) add noise

**Arguments**:

  -----------
  x : list
  model states at the beginning of the step [x1,x2,x3,x4]
  
  pma : float
  Mean areal precipitation during the step
  
  etp : float
  Potential evapotranspiration during the step
  

**Returns**:

  --------
  x : list
  the model states at the end of the step [x1,x2,x3,x4]
  
  npasos : int
  The number of substeps used for computation

<a id="pydrodelta.procedures.sac_enkf.SacEnkfProcedureFunction.pertX"></a>

#### pertX

```python
def pertX(x: list) -> list
```

Add noise to each of x [x1,x2,x3,x4]

**Arguments**:

  -----------
  x : list
  Model states  [x1,x2,x3,x4]
  

**Returns**:

  --------
  list :  [x1,x2,x3,x4]

<a id="pydrodelta.procedures.sac_enkf.SacEnkfProcedureFunction.setH"></a>

#### setH

```python
def setH() -> None
```

Set transformation matrix .H

<a id="pydrodelta.procedures.sac_enkf.SacEnkfProcedureFunction.setInitialEnsemble"></a>

#### setInitialEnsemble

```python
def setInitialEnsemble(init_states: list) -> None
```

Initialize ensembles (self.ens, self.ens1, self.ens2) from initial states and randomization parameter self.x_stddev.

**Arguments**:

  -----------
  init_states : list
  Initial states [x1,x2,x3,x4]

<a id="pydrodelta.procedures.sac_enkf.SacEnkfProcedureFunction.getC"></a>

#### getC

```python
def getC() -> list
```

Generate covariance matrix C

**Returns**:

  --------
  covariance matrix C : list

<a id="pydrodelta.procedures.sac_enkf.SacEnkfProcedureFunction.getR"></a>

#### getR

```python
def getR(innov: dict, qvar: float, smc_var: float) -> Tuple[list, list]
```

Generate observation error matrix R and adapt transformation matrix H into H_j according to available observations for assimilation

**Arguments**:

  -----------
  innov : dict
  Which observed variables to assimilate. Valid keys: 'smc', 'q'. Values must be boolean
  
  qvar : float
  variance of discharge
  
  smc_var : float
  variance of soil moisture
  

**Returns**:

  --------
  R : list
  The error matrix
  
  H_j : list
  The adapted transformation matrix

<a id="pydrodelta.procedures.sac_enkf.SacEnkfProcedureFunction.getKG"></a>

#### getKG

```python
def getKG(H_j: list, C: list, R: list) -> np.ndarray
```

Calculate Kalman gain matrix

**Arguments**:

  -----------
  H_j : list
  Adapted transformation matrix
  
  C : list
  states covariance matrix
  
  R : list
  Observation error covariance matrix
  

**Returns**:

  --------
  Kalman gain matrix (KG) : numpy.ndarray

<a id="pydrodelta.procedures.sac_enkf.SacEnkfProcedureFunction.asimila"></a>

#### asimila

```python
def asimila(obs: list, R: list, KG_j: list) -> list
```

Assimilate available observations

**Arguments**:

  -----------
  obs : list
  Available observations for data assimilation
  
  R : list
  Observation error covariance matrix
  
  KG_j : list
  Kalman gain matrix
  

**Returns**:

  --------
  err : list
  ensemble model error matrix (difference of simulated states with observed states)

<a id="pydrodelta.procedures.sac_enkf.SacEnkfProcedureFunction.resultsDF"></a>

#### resultsDF

```python
def resultsDF() -> DataFrame
```

Convert simulation results into a DataFrame

<a id="pydrodelta.procedures.sac_enkf.SacEnkfProcedureFunction.newResultsRow"></a>

#### newResultsRow

```python
def newResultsRow(timestart: datetime = None,
                  x1: float = None,
                  x2: float = None,
                  x3: float = None,
                  x4: float = None,
                  q4: float = None,
                  smc: float = None) -> DataFrame
```

Generate single-row DataFrame from simulation states and outputs

