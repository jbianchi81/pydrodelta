# Table of Contents

* [pydrodelta.topology](#pydrodelta.topology)
  * [Topology](#pydrodelta.topology.Topology)
    * [\_\_init\_\_](#pydrodelta.topology.Topology.__init__)
    * [addNode](#pydrodelta.topology.Topology.addNode)
    * [batchProcessInput](#pydrodelta.topology.Topology.batchProcessInput)
    * [loadData](#pydrodelta.topology.Topology.loadData)
    * [setOriginalData](#pydrodelta.topology.Topology.setOriginalData)
    * [removeOutliers](#pydrodelta.topology.Topology.removeOutliers)
    * [detectJumps](#pydrodelta.topology.Topology.detectJumps)
    * [applyMovingAverage](#pydrodelta.topology.Topology.applyMovingAverage)
    * [applyOffset](#pydrodelta.topology.Topology.applyOffset)
    * [regularize](#pydrodelta.topology.Topology.regularize)
    * [fillNulls](#pydrodelta.topology.Topology.fillNulls)
    * [derive](#pydrodelta.topology.Topology.derive)
    * [adjust](#pydrodelta.topology.Topology.adjust)
    * [concatenateProno](#pydrodelta.topology.Topology.concatenateProno)
    * [interpolate](#pydrodelta.topology.Topology.interpolate)
    * [toSeries](#pydrodelta.topology.Topology.toSeries)
    * [toList](#pydrodelta.topology.Topology.toList)
    * [uploadData](#pydrodelta.topology.Topology.uploadData)
    * [uploadDataAsProno](#pydrodelta.topology.Topology.uploadDataAsProno)

<a id="pydrodelta.topology"></a>

# pydrodelta.topology

<a id="pydrodelta.topology.Topology"></a>

## Topology Objects

```python
class Topology()
```

The topology defines a list of nodes which represent stations and basins. These nodes are identified with a node_id and must contain one or many variables each, which represent the hydrologic observed/simulated properties at that node (such as discharge, precipitation, etc.). They are identified with a variable_id and may contain one or many ordered series, which contain the timestamped values. If series are missing from a variable, it is assumed that observations are not available for said variable at said node. Additionally, series_prono may be defined to represent timeseries of said variable at said node that are originated by an external modelling procedure. If series are available, said series_prono may be automatically fitted to the observed data by means of a linear regression. Such a procedure may be useful to extend the temporal extent of the variable into the forecast horizon so as to cover the full time domain of the plan. Finally, one or many series_sim may be added and it is where simulated data (as a result of a procedure) will be stored. All series have a series_id identifier which is used to read/write data from data source whether it be an alerta5DBIO instance or a csv file.

<a id="pydrodelta.topology.Topology.__init__"></a>

#### \_\_init\_\_

```python
def __init__(timestart: Union[str, dict],
             timeend: Union[str, dict],
             forecast_timeend: Union[str, dict, None] = None,
             time_offset: Union[str, dict, None] = None,
             time_offset_start: Union[str, dict, None] = None,
             time_offset_end: Union[str, dict, None] = None,
             interpolation_limit: Union[dict, int] = None,
             extrapolate: bool = False,
             nodes: list = list(),
             cal_id: Union[int, None] = None,
             plot_params: Union[dict, None] = None,
             report_file: Union[str, None] = None,
             plan=None)
```

Initiate topology

**Arguments**:

  -----------
  timestart : str or dict
  start date of observations period (datetime or timedelta relative to now)
  
  timeend :  str or dict
  end date of observations period (datetime or timedelta relative to now)
  
  forecast_timeend :  str, dict or None
  forecast horizon (datetime or timedelta relative to timeend)
  
  time_offset :    str, dict or None
  time of day where timesteps start
  
  time_offset_start : str, dict or None
  time of day where first timestep start. Defaults to 0 hours
  
  time_offset_end : str, dict or None
  time of day where last timestep ends. Defaults to timeend.hour
  
  interpolation_limit : dict or int
  maximum duration between observations for interpolation (default: 0)
  
  extrapolate : boolean (default: False)
  Extrapolate observations outside the observation time domain, up to a maximum duration equal to interpolation_limit
  
  nodes : List[Node]
  Nodes represent stations and basins. These nodes are identified with a node_id and must contain one or many variables each, which represent the hydrologic observed/simulated properties at that node (such as discharge, precipitation, etc.). They are identified with a variable_id and may contain one or many ordered series, which contain the timestamped values. If series are missing from a variable, it is assumed that observations are not available for said variable at said node. Additionally, series_prono may be defined to represent timeseries of said variable at said node that are originated by an external modelling procedure. If series are available, said series_prono may be automatically fitted to the observed data by means of a linear regression. Such a procedure may be useful to extend the temporal extent of the variable into the forecast horizon so as to cover the full time domain of the plan. Finally, one or many series_sim may be added and it is where simulated data (as a result of a procedure) will be stored. All series have a series_id identifier which is used to read/write data from data source whether it be an alerta5DBIO instance or a csv file.
  
  cal_id : int or None
  Identifier for saving analysis results as forecast (i.e. using .uploadDataAsProno)
  
  plot_params : dict or None
  Plotting configuration. See .plotProno
  
  report_file : str or None
  Write analysis report into this file
  
  plan : Plan
  Plan containing this topology

<a id="pydrodelta.topology.Topology.addNode"></a>

#### addNode

```python
def addNode(node, plan=None) -> None
```

Append node into .nodes

**Arguments**:

  -----------
  node : dict
  Node to append
  
  plan : Node or None
  Plan that contains the topology

<a id="pydrodelta.topology.Topology.batchProcessInput"></a>

#### batchProcessInput

```python
def batchProcessInput(include_prono=False) -> None
```

Run input processing sequence. This includes (in this order):

- .loadData()
- .removeOutliers()
- .detectJumps()
- .applyOffset()
- .regularize()
- .applyMovingAverage()
- .fillNulls()
- .adjust()
- .concatenateProno() (if include_prono is True)
- .derive()
- .interpolate()
- .setOriginalData()
- .setOutputData()
- .plotProno()
- .printReport() if ().report_file is not None)

**Arguments**:

  -----------
  include_prono : bool default False
  For each variable, fill missing observations with values from series_prono

<a id="pydrodelta.topology.Topology.loadData"></a>

#### loadData

```python
def loadData(include_prono=True) -> None
```

For each series of each variable of each node, load data from the source.

**Arguments**:

  -----------
  
  include_prono : bool default True
  Load forecasted data

<a id="pydrodelta.topology.Topology.setOriginalData"></a>

#### setOriginalData

```python
def setOriginalData() -> None
```

For each variable of each node, copy .data into .original_data

<a id="pydrodelta.topology.Topology.removeOutliers"></a>

#### removeOutliers

```python
def removeOutliers() -> None
```

For each serie of each variable of each node, perform outlier removal (only in series where lim_outliers is not None).

<a id="pydrodelta.topology.Topology.detectJumps"></a>

#### detectJumps

```python
def detectJumps() -> None
```

For each serie of each variable of each node, perform jumps detection (only in series where lim_jump is not None). Results are saved in jumps_data of the series object.

<a id="pydrodelta.topology.Topology.applyMovingAverage"></a>

#### applyMovingAverage

```python
def applyMovingAverage() -> None
```

For each serie of each variable of each node, apply moving average (only in series where moving_average is not None)

<a id="pydrodelta.topology.Topology.applyOffset"></a>

#### applyOffset

```python
def applyOffset() -> None
```

For each serie of each variable of each node, apply x and/or y offset (only in series where x_offset (time) or y_offset (value) is defined)

<a id="pydrodelta.topology.Topology.regularize"></a>

#### regularize

```python
def regularize(interpolate=False) -> None
```

For each series and series_prono of each observed variable of each node, regularize the time step according to time_interval and time_offset

**Arguments**:

  ----------
  interpolate : bool default False
  if False, interpolates only to the closest timestep of the regular timeseries. If observation is equidistant to preceding and following timesteps it interpolates to both

<a id="pydrodelta.topology.Topology.fillNulls"></a>

#### fillNulls

```python
def fillNulls() -> None
```

For each observed variable of each node, copies data of first series and fills its null values with the other series. In the end it fills nulls with self.fill_value. Saves result in self.data

<a id="pydrodelta.topology.Topology.derive"></a>

#### derive

```python
def derive() -> None
```

For each derived variable of each node, derives data from related variable according to derived_from attribute

<a id="pydrodelta.topology.Topology.adjust"></a>

#### adjust

```python
def adjust() -> None
```

For each series_prono of each variable of each node, if observations are available, perform error correction by linear regression

<a id="pydrodelta.topology.Topology.concatenateProno"></a>

#### concatenateProno

```python
def concatenateProno() -> None
```

For each variable of each node, if series_prono are available, concatenate series_prono into variable.data

<a id="pydrodelta.topology.Topology.interpolate"></a>

#### interpolate

```python
def interpolate(limit: timedelta = None, extrapolate: bool = None) -> None
```

For each variable of each node, fill nulls of data by interpolation

**Arguments**:

  -----------
  limit : timedelta
  Maximum interpolation distance
  
  extrapolate : bool
  Extrapolate up to limit

<a id="pydrodelta.topology.Topology.toSeries"></a>

#### toSeries

```python
def toSeries(use_node_id=False) -> list
```

returns list of Series objects. Same as toList(flatten=True)

<a id="pydrodelta.topology.Topology.toList"></a>

#### toList

```python
def toList(pivot=False, use_node_id=False, flatten=True) -> list
```

returns list of all data in nodes[0..n].data

pivot: boolean              pivot observations on index (timestart)
use_node_id: boolean    uses node.id as series_id instead of node.output_series[0].id
flatten: boolean        if set to False, returns list of series objects:[{"series_id":int,observaciones:[obs,obs,...]},...] (ignored if pivot=True)

<a id="pydrodelta.topology.Topology.uploadData"></a>

#### uploadData

```python
def uploadData(include_prono) -> list
```

Uploads analysis data of all nodes as a5 observaciones

<a id="pydrodelta.topology.Topology.uploadDataAsProno"></a>

#### uploadDataAsProno

```python
def uploadDataAsProno(include_obs=True, include_prono=False) -> dict
```

Uploads analysis data of all nodes as a5 pronosticos

