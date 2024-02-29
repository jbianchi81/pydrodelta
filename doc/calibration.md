# Table of Contents

* [pydrodelta.calibration](#pydrodelta.calibration)
  * [Calibration](#pydrodelta.calibration.Calibration)
    * [calibrate](#pydrodelta.calibration.Calibration.calibrate)
    * [result\_index](#pydrodelta.calibration.Calibration.result_index)
    * [objective\_function](#pydrodelta.calibration.Calibration.objective_function)
    * [limit](#pydrodelta.calibration.Calibration.limit)
    * [sigma](#pydrodelta.calibration.Calibration.sigma)
    * [ranges](#pydrodelta.calibration.Calibration.ranges)
    * [no\_improve\_thr](#pydrodelta.calibration.Calibration.no_improve_thr)
    * [max\_stagnations](#pydrodelta.calibration.Calibration.max_stagnations)
    * [max\_iter](#pydrodelta.calibration.Calibration.max_iter)
    * [calibration\_result](#pydrodelta.calibration.Calibration.calibration_result)
    * [save\_result](#pydrodelta.calibration.Calibration.save_result)
    * [calibration\_period](#pydrodelta.calibration.Calibration.calibration_period)
    * [downhill\_simplex](#pydrodelta.calibration.Calibration.downhill_simplex)
    * [\_\_init\_\_](#pydrodelta.calibration.Calibration.__init__)
    * [runReturnScore](#pydrodelta.calibration.Calibration.runReturnScore)
    * [makeSimplex](#pydrodelta.calibration.Calibration.makeSimplex)
    * [downhillSimplex](#pydrodelta.calibration.Calibration.downhillSimplex)
    * [run](#pydrodelta.calibration.Calibration.run)

<a id="pydrodelta.calibration"></a>

# pydrodelta.calibration

<a id="pydrodelta.calibration.Calibration"></a>

## Calibration Objects

```python
class Calibration()
```

Calibration procedure using Nelder Mead Downhill Simplex

<a id="pydrodelta.calibration.Calibration.calibrate"></a>

#### calibrate

Perform the calibration

<a id="pydrodelta.calibration.Calibration.result_index"></a>

#### result\_index

Index of the result element to use to compute the objective function

<a id="pydrodelta.calibration.Calibration.objective_function"></a>

#### objective\_function

Objective function for the calibration procedure. One of 'rmse', 'mse', 'bias', 'stdev_dif', 'r', 'nse', 'cov', 'oneminusr'

<a id="pydrodelta.calibration.Calibration.limit"></a>

#### limit

Limit values of the parameters to the provided min-max ranges

<a id="pydrodelta.calibration.Calibration.sigma"></a>

#### sigma

Factor of the variance of the initial distribution of the parameter values

<a id="pydrodelta.calibration.Calibration.ranges"></a>

#### ranges

```python
@property
def ranges() -> List[Tuple[float, float]]
```

Override default parameter ranges with these values. A list of length equal to the number of parameters of the procedure function (._procedure.function._parameters) where each element is a 2-tuple of floats (range_min, range_max)

<a id="pydrodelta.calibration.Calibration.no_improve_thr"></a>

#### no\_improve\_thr

break after max_stagnations iterations with an improvement lower than no_improv_thr

<a id="pydrodelta.calibration.Calibration.max_stagnations"></a>

#### max\_stagnations

break after max_stagnations iterations with an improvement lower than no_improve_thr

<a id="pydrodelta.calibration.Calibration.max_iter"></a>

#### max\_iter

maximum iterations

<a id="pydrodelta.calibration.Calibration.calibration_result"></a>

#### calibration\_result

```python
@property
def calibration_result() -> Tuple[List[float], float]
```

Calibration result. First element is the list of obtained parameters. The second element is the obtained objective function value

<a id="pydrodelta.calibration.Calibration.save_result"></a>

#### save\_result

Save calibration result into this file

<a id="pydrodelta.calibration.Calibration.calibration_period"></a>

#### calibration\_period

```python
@property
def calibration_period() -> Tuple[datetime, datetime]
```

Calibration period (begin date, end date)

<a id="pydrodelta.calibration.Calibration.downhill_simplex"></a>

#### downhill\_simplex

```python
@property
def downhill_simplex() -> DownhillSimplex
```

Instance of DownhillSimplex

<a id="pydrodelta.calibration.Calibration.__init__"></a>

#### \_\_init\_\_

```python
def __init__(procedure,
             calibrate: bool = True,
             result_index: int = 0,
             objective_function: str = 'rmse',
             limit: bool = True,
             sigma: float = 0.25,
             ranges: List[Tuple[float, float]] = None,
             no_improve_thr: float = 0.0000001,
             max_stagnations: int = 10,
             max_iter: int = 5000,
             save_result: str = None,
             calibration_period: list = None)
```

**Arguments**:

  -----------
  procedure : Procedure
  The procedure to be calibrated
  
  calibrate : bool = True
  
  Perform the calibration
  
  result_index : int = 0
  
  Index of the output element to use to compute the objective function
  
  objective_function : str = 'rmse'
  
  Objective function for the calibration procedure. One of 'rmse', 'mse', 'bias', 'stdev_dif', 'r', 'nse', 'cov', 'oneminusr'
  
  limit : bool = True
  
  Limit values of the parameters to the provided min-max ranges
  
  sigma : float = 0.25
  
  Ratio of the standard deviation of the initial distribution of the parameter values with the min-max range. sigma = stddev / (0.5 * (max_range - min_range)) I.e., if sigma=1, the standard deviation of the parameter values will be equal to half the min-max range
  
  ranges : List[Tuple[float,float]] = None
  
  Override default parameter ranges with these values. A list of length equal to the number of parameters of the procedure function (._procedure.function._parameters) where each element is a 2-tuple of floats (range_min, range_max)
  
  no_improve_thr : float = 0.000001
  
  break after max_stagnations iterations with an improvement lower than no_improv_thr
  
  max_stagnations : int = 10
  
  break after max_stagnations iterations with an improvement lower than no_improve_thr
  
  max_iter : int = 5000
  
  maximum iterations
  
  save_result : str = None
  
  Save calibration result into this file
  
  calibration_period : list = None
  
  Calibration period (begin date, end date)

<a id="pydrodelta.calibration.Calibration.runReturnScore"></a>

#### runReturnScore

```python
def runReturnScore(parameters: array,
                   objective_function: Optional[str] = None,
                   result_index: Optional[int] = None) -> float
```

Runs procedure and returns objective function value
procedure.input and procedure.output_obs must be already loaded

**Arguments**:

  -----------
  parameters : array
  
  Procedure function parameters
  
  objective_function : Optional[str] = None
  
  Name of the objective function. One of 'rmse', 'mse', 'bias', 'stdev_dif', 'r', 'nse', 'cov', 'oneminusr'
  
  result_index : Optional[int] = None
  
  Index of the output to use to compute the objective function
  

**Returns**:

  --------
  the objective function value : float

<a id="pydrodelta.calibration.Calibration.makeSimplex"></a>

#### makeSimplex

```python
def makeSimplex(
    inplace: bool = True,
    objective_function: Optional[str] = None,
    result_index: Optional[int] = None,
    sigma: Optional[float] = None,
    limit: Optional[bool] = None,
    ranges: Optional[List[Tuple[float, float]]] = None
) -> Union[None, List[Tuple[List[float], float]]]
```

Generate simplex

**Arguments**:

  -----------
  inplace : bool = True
  
  Save result inplace (self.simplex) and return None. Else return result
  
  objective_function : Optional[str] = None
  
  Name of the objective function. One of 'rmse', 'mse', 'bias', 'stdev_dif', 'r', 'nse', 'cov', 'oneminusr'
  
  result_index : Optional[int] = None
  
  Index of the output to use to compute the objective function
  
  sigma : float = None
  
  Ratio of the standard deviation of the initial distribution of the parameter values with the min-max range. sigma = stddev / (0.5 * (max_range - min_range)) I.e., if sigma=1, the standard deviation of the parameter values will be equal to half the min-max range
  
  limit : bool = True
  
  Limit values of the parameters to the provided min-max ranges
  
  ranges : List[Tuple[float,float]] = None
  
  Override default parameter ranges with these values. A list of length equal to the number of parameters of the procedure function (._procedure.function._parameters) where each element is a 2-tuple of floats (range_min, range_max)
  

**Returns**:

  --------
  None or simplex : Union[None,List[Tuple[List[float],float]]]
  
  First element of each item is the parameter list. Second element is the obtained objective function value

<a id="pydrodelta.calibration.Calibration.downhillSimplex"></a>

#### downhillSimplex

```python
def downhillSimplex(
        inplace: bool = True,
        sigma: Optional[int] = None,
        limit: Optional[bool] = None,
        ranges: Optional[List[Tuple[float, float]]] = None,
        no_improve_thr: Optional[float] = None,
        max_stagnations: Optional[int] = None,
        max_iter: Optional[int] = None) -> Union[None, DownhillSimplex]
```

Instantiate DownhillSimplex object. Every parameter is optional. If missing or None, the corresponding instance property is used.

**Arguments**:

  -----------
  inplace : bool = True
  
  Save result inplace (self.downhill_simplex) and return None. Else return result
  
  sigma : float = None
  
  Ratio of the standard deviation of the initial distribution of the parameter values with the min-max range. sigma = stddev / (0.5 * (max_range - min_range)) I.e., if sigma=1, the standard deviation of the parameter values will be equal to half the min-max range
  
  limit : bool = True
  
  Limit values of the parameters to the provided min-max ranges
  
  ranges : List[Tuple[float,float]] = None
  
  Override default parameter ranges with these values. A list of length equal to the number of parameters of the procedure function (._procedure.function._parameters) where each element is a 2-tuple of floats (range_min, range_max)
  
  no_improve_thr : float = None
  
  break after max_stagnations iterations with an improvement lower than no_improv_thr
  
  max_stagnations : int = None
  
  break after max_stagnations iterations with an improvement lower than no_improve_thr
  
  max_iter : int = None
  
  maximum iterations
  

**Returns**:

  --------
  None or DownhillSimplex : Union[None,DownhillSimplex]

<a id="pydrodelta.calibration.Calibration.run"></a>

#### run

```python
def run(
    inplace: bool = True,
    sigma: Optional[int] = None,
    limit: Optional[bool] = None,
    ranges: Optional[List[Tuple[float, float]]] = None,
    no_improve_thr: Optional[float] = None,
    max_stagnations: Optional[int] = None,
    max_iter: Optional[int] = None,
    save_result: Optional[str] = None
) -> Union[None, Tuple[List[float], float]]
```

Execute calibration. Every parameter is optional. If missing or None, the corresponding instance property is used.

**Arguments**:

  -----------
  inplace : bool = True
  
  Save result inplace (self.downhill_simplex) and return None. Else return result
  
  sigma : float = None
  
  Ratio of the standard deviation of the initial distribution of the parameter values with the min-max range. sigma = stddev / (0.5 * (max_range - min_range)) I.e., if sigma=1, the standard deviation of the parameter values will be equal to half the min-max range
  
  limit : bool = True
  
  Limit values of the parameters to the provided min-max ranges
  
  ranges : List[Tuple[float,float]] = None
  
  Override default parameter ranges with these values. A list of length equal to the number of parameters of the procedure function (._procedure.function._parameters) where each element is a 2-tuple of floats (range_min, range_max)
  
  no_improve_thr : float = None
  
  break after max_stagnations iterations with an improvement lower than no_improv_thr
  
  max_stagnations : int = None
  
  break after max_stagnations iterations with an improvement lower than no_improve_thr
  
  max_iter : int = None
  
  maximum iterations
  
  save_results : str = None
  
  Save the calibration result into this file
  

**Returns**:

  --------
  None or calibration result : Tuple[List[float],float]
  
  First element is the list of calibrated parameters. Second element is the obtained objective function value

