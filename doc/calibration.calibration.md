# Table of Contents

* [pydrodelta.calibration.calibration](#pydrodelta.calibration.calibration)
  * [Calibration](#pydrodelta.calibration.calibration.Calibration)
    * [calibrate](#pydrodelta.calibration.calibration.Calibration.calibrate)
    * [result\_index](#pydrodelta.calibration.calibration.Calibration.result_index)
    * [objective\_function](#pydrodelta.calibration.calibration.Calibration.objective_function)
    * [calibration\_result](#pydrodelta.calibration.calibration.Calibration.calibration_result)
    * [save\_result](#pydrodelta.calibration.calibration.Calibration.save_result)
    * [calibration\_period](#pydrodelta.calibration.calibration.Calibration.calibration_period)
    * [scores](#pydrodelta.calibration.calibration.Calibration.scores)
    * [\_\_init\_\_](#pydrodelta.calibration.calibration.Calibration.__init__)
    * [runReturnScore](#pydrodelta.calibration.calibration.Calibration.runReturnScore)
    * [run](#pydrodelta.calibration.calibration.Calibration.run)

<a id="pydrodelta.calibration.calibration"></a>

# pydrodelta.calibration.calibration

<a id="pydrodelta.calibration.calibration.Calibration"></a>

## Calibration Objects

```python
class Calibration()
```

Calibration base/abstract class

<a id="pydrodelta.calibration.calibration.Calibration.calibrate"></a>

#### calibrate

Perform the calibration

<a id="pydrodelta.calibration.calibration.Calibration.result_index"></a>

#### result\_index

Index of the result element to use to compute the objective function

<a id="pydrodelta.calibration.calibration.Calibration.objective_function"></a>

#### objective\_function

Objective function for the calibration procedure. One of 'rmse', 'mse', 'bias', 'stdev_dif', 'r', 'nse', 'cov', 'oneminusr'

<a id="pydrodelta.calibration.calibration.Calibration.calibration_result"></a>

#### calibration\_result

```python
@property
def calibration_result() -> Tuple[List[float], float]
```

Calibration result. First element is the list of obtained parameters. The second element is the obtained objective function value

<a id="pydrodelta.calibration.calibration.Calibration.save_result"></a>

#### save\_result

Save calibration result into this file

<a id="pydrodelta.calibration.calibration.Calibration.calibration_period"></a>

#### calibration\_period

```python
@property
def calibration_period() -> Tuple[datetime, datetime]
```

Calibration period (begin date, end date)

<a id="pydrodelta.calibration.calibration.Calibration.scores"></a>

#### scores

Calibration/Validation scores

<a id="pydrodelta.calibration.calibration.Calibration.__init__"></a>

#### \_\_init\_\_

```python
def __init__(procedure,
             calibrate: bool = True,
             result_index: int = 0,
             objective_function: str = 'rmse',
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
  
  save_result : str = None
  
  Save calibration result into this file
  
  calibration_period : list = None
  
  Calibration period (begin date, end date)

<a id="pydrodelta.calibration.calibration.Calibration.runReturnScore"></a>

#### runReturnScore

```python
def runReturnScore(parameters: array,
                   objective_function: Optional[str] = None,
                   result_index: Optional[int] = None,
                   save_results: str = None) -> float
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

<a id="pydrodelta.calibration.calibration.Calibration.run"></a>

#### run

```python
def run(inplace: bool = True,
        save_result: Optional[str] = None,
        **kwargs) -> Union[None, Tuple[List[float], float]]
```

Execute calibration. Every parameter is optional. If missing or None, the corresponding instance property is used.

**Arguments**:

  -----------
  inplace : bool = True
  
  Save result inplace (self.downhill_simplex) and return None. Else return result
  
  save_result : str = None
  
  Save the calibration result into this file
  

**Returns**:

  --------
  None or calibration result : Tuple[List[float],float]
  
  First element is the list of calibrated parameters. Second element is the obtained objective function value

