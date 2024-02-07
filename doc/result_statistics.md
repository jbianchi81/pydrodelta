# Table of Contents

* [pydrodelta.result\_statistics](#pydrodelta.result_statistics)
  * [ResultStatistics](#pydrodelta.result_statistics.ResultStatistics)
    * [\_\_init\_\_](#pydrodelta.result_statistics.ResultStatistics.__init__)
    * [compute](#pydrodelta.result_statistics.ResultStatistics.compute)
    * [toDict](#pydrodelta.result_statistics.ResultStatistics.toDict)

<a id="pydrodelta.result_statistics"></a>

# pydrodelta.result\_statistics

<a id="pydrodelta.result_statistics.ResultStatistics"></a>

## ResultStatistics Objects

```python
class ResultStatistics()
```

Collection of statistic analysis results for the procedure

<a id="pydrodelta.result_statistics.ResultStatistics.__init__"></a>

#### \_\_init\_\_

```python
def __init__(obs: list = list(),
             sim: list = list(),
             metadata: dict = None,
             calibration_period: list = None,
             group: str = "cal",
             compute: bool = False)
```

Initiate collection of statistic analysis for the procedue

**Arguments**:

  -----------
  obs : list of floats
  List of observed values
  
  sim : list of floats
  List of simulated values. Must be of the same length as obs
  
  metadata : dict or None
  Metadata of the node and the variable
  
  calibration_period : 2-length list  or None
  start and end date for splitting the data into calibration and validation periods
  
  group : str (defaults to 'cal')
  cal or val
  
  compute : bool (defaults to False)
  Compute statistical analysis

<a id="pydrodelta.result_statistics.ResultStatistics.compute"></a>

#### compute

```python
def compute() -> None
```

Compute the statistical analysis.

Saves the results inplace (returns None)

<a id="pydrodelta.result_statistics.ResultStatistics.toDict"></a>

#### toDict

```python
def toDict() -> dict
```

Convert result statistics into dict

**Returns**:

  --------
  dict

