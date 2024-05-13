# Table of Contents

* [pydrodelta.calibration.linear\_regression\_calibration](#pydrodelta.calibration.linear_regression_calibration)
  * [LinearRegressionCalibration](#pydrodelta.calibration.linear_regression_calibration.LinearRegressionCalibration)
    * [linearRegression](#pydrodelta.calibration.linear_regression_calibration.LinearRegressionCalibration.linearRegression)
    * [\_\_init\_\_](#pydrodelta.calibration.linear_regression_calibration.LinearRegressionCalibration.__init__)
    * [run](#pydrodelta.calibration.linear_regression_calibration.LinearRegressionCalibration.run)

<a id="pydrodelta.calibration.linear_regression_calibration"></a>

# pydrodelta.calibration.linear\_regression\_calibration

<a id="pydrodelta.calibration.linear_regression_calibration.LinearRegressionCalibration"></a>

## LinearRegressionCalibration Objects

```python
class LinearRegressionCalibration(Calibration)
```

Calibration procedure using linear regression - least squares

<a id="pydrodelta.calibration.linear_regression_calibration.LinearRegressionCalibration.linearRegression"></a>

#### linearRegression

```python
def linearRegression(
    calibration_period: Tuple[datetime, datetime] = None
) -> Tuple[LinearCombinationParametersDict, DataFrame]
```

Perform linear regression

**Arguments**:

  calibration_period : Tuple[datetime,datetime] = None
  Begin and end dates of training set. Data outside this period is used for validation. If not set, validation is not performed
  

**Returns**:

  LinearCombinationParametersDict : resulting parameters
  DataFrame : resulting scores

<a id="pydrodelta.calibration.linear_regression_calibration.LinearRegressionCalibration.__init__"></a>

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
  
  Ignored. Target series is fixed to the first input
  
  objective_function : str = 'rmse'
  
  Ignored. Fixed to rmse
  
  save_result : str = None
  
  Save calibration result into this file
  
  calibration_period : Tuple[datetime,datetime] = None
  
  Begin and end dates of training set. Data outside this period is used for validation. If not set, validation is not performed

<a id="pydrodelta.calibration.linear_regression_calibration.LinearRegressionCalibration.run"></a>

#### run

```python
def run(
    inplace: bool = True,
    save_result: Optional[str] = None,
    calibration_period: Optional[Tuple[datetime, datetime]] = None
) -> Union[None, Tuple[LinearCombinationParametersDict, float]]
```

Execute calibration. Every parameter is optional. If missing or None, the corresponding instance property is used.

**Arguments**:

  -----------
  inplace : bool = True
  
  Save result inplace (self._calibration_result) and return None. Else return result
  
  save_results : str = None
  
  Save the calibration result into this file
  
  calibration_period : : Optional[Tuple[datetime,datetime]] = None
  
  Begin and end dates of training set. Data outside this period is used for validation. If not set, validation is not performed
  

**Returns**:

  --------
  None or calibration result : Tuple[List[ForecastStepDict],float]
  
  First element is the list of calibrated parameters. Second element is the obtained objective function value

