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
    * [setOutputData](#pydrodelta.topology.Topology.setOutputData)
    * [toCSV](#pydrodelta.topology.Topology.toCSV)
    * [outputToCSV](#pydrodelta.topology.Topology.outputToCSV)
    * [toSeries](#pydrodelta.topology.Topology.toSeries)
    * [toList](#pydrodelta.topology.Topology.toList)
    * [outputToList](#pydrodelta.topology.Topology.outputToList)
    * [saveData](#pydrodelta.topology.Topology.saveData)
    * [saveOutputData](#pydrodelta.topology.Topology.saveOutputData)
    * [uploadData](#pydrodelta.topology.Topology.uploadData)
    * [uploadDataAsProno](#pydrodelta.topology.Topology.uploadDataAsProno)
    * [pivotData](#pydrodelta.topology.Topology.pivotData)
    * [pivotOutputData](#pydrodelta.topology.Topology.pivotOutputData)
    * [plotVariable](#pydrodelta.topology.Topology.plotVariable)
    * [plotProno](#pydrodelta.topology.Topology.plotProno)
    * [printReport](#pydrodelta.topology.Topology.printReport)
    * [printGraph](#pydrodelta.topology.Topology.printGraph)
    * [toGraph](#pydrodelta.topology.Topology.toGraph)
    * [exportGraph](#pydrodelta.topology.Topology.exportGraph)

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

<a id="pydrodelta.topology.Topology.setOutputData"></a>

#### setOutputData

```python
def setOutputData() -> None
```

For each series_output of each variable of each node, copy variable.data into series_output.data. If x_offset or y_offset are not 0, applies the offset

<a id="pydrodelta.topology.Topology.toCSV"></a>

#### toCSV

```python
def toCSV(pivot: bool = False) -> str
```

Generates csv table from all variables of all nodes

**Arguments**:

  -----------
  pivot : bool
  If true, pivots variables into columns
  

**Returns**:

  --------
  str

<a id="pydrodelta.topology.Topology.outputToCSV"></a>

#### outputToCSV

```python
def outputToCSV(pivot=False) -> str
```

Generates csv table of all series_output of all variables of all nodes

**Arguments**:

  -----------
  pivot : bool
  If true, pivots variables into columns
  

**Returns**:

  --------
  str

<a id="pydrodelta.topology.Topology.toSeries"></a>

#### toSeries

```python
def toSeries(use_node_id: bool = False) -> list
```

returns list of Series objects. Same as toList(flatten=True)

**Arguments**:

  -----------
  use_node_id : bool
  use node_id as series identifier
  

**Returns**:

  --------
  list of Observations

<a id="pydrodelta.topology.Topology.toList"></a>

#### toList

```python
def toList(pivot: bool = False,
           use_node_id: bool = False,
           flatten: bool = True) -> list
```

returns list of all data in nodes[0..n].data

**Arguments**:

  -----------
  pivot : bool
  pivot variables into columns
  
  use_node_id : bool
  use node.id as series_id instead of node.output_series[0].id
  
  flatten : bool
  If set to False, return list of Series: [{"series_id":int,observaciones:[obs,obs,...]},...] (ignored if pivot=True). If True, return list of Observations: [{"timestart":str,"valor":float,"series_id":int},...]
  

**Returns**:

  --------
  list of Series or list of Observations

<a id="pydrodelta.topology.Topology.outputToList"></a>

#### outputToList

```python
def outputToList(pivot: bool = False, flatten: bool = False) -> list
```

returns list of data of all output_series of all variables of all nodes

**Arguments**:

  -----------
  pivot : bool
  pivot variables into columns
  
  flatten : bool
  If set to False, return list of Series: [{"series_id":int,observaciones:[obs,obs,...]},...] (ignored if pivot=True). If True, return list of Observations: [{"timestart":str,"valor":float,"series_id":int},...]
  

**Returns**:

  --------
  list of Series or list of Observations

<a id="pydrodelta.topology.Topology.saveData"></a>

#### saveData

```python
def saveData(file: str,
             format: str = "csv",
             pivot: bool = False,
             pretty: bool = False) -> None
```

Save data of all variables of all nodes to a file in the desired format

**Arguments**:

  -----------
  file : str
  Where to save the data
  
  format : str
  File format: csv or json
  
  pivot : bool
  pivot variables into columns
  
  pretty : bool
  Pretty-print JSON (w/ indentation)

<a id="pydrodelta.topology.Topology.saveOutputData"></a>

#### saveOutputData

```python
def saveOutputData(file: str,
                   format: str = "csv",
                   pivot: bool = False,
                   pretty: bool = False) -> None
```

Save data of all series_output of all variables of all nodes to a file in the desired format

**Arguments**:

  -----------
  file : str
  Where to save the data
  
  format : str
  File format: csv or json
  
  pivot : bool
  pivot variables into columns
  
  pretty : bool
  Pretty-print JSON (w/ indentation)

<a id="pydrodelta.topology.Topology.uploadData"></a>

#### uploadData

```python
def uploadData(include_prono: bool) -> list
```

Uploads analysis data (series_output) of all variables of all nodes as a5 observaciones (https://raw.githubusercontent.com/jbianchi81/alerta5DBIO/master/public/schemas/a5/observacion.yml)

**Arguments**:

  -----------
  include_prono : bool
  Include the forecast horizon
  

**Returns**:

  list of Observations

<a id="pydrodelta.topology.Topology.uploadDataAsProno"></a>

#### uploadDataAsProno

```python
def uploadDataAsProno(include_obs: bool = True,
                      include_prono: bool = False) -> dict
```

Uploads analysis data (series_output) of all variables of all nodes to output api as a5 pronosticos (https://github.com/jbianchi81/alerta5DBIO/blob/master/public/schemas/a5/pronostico.yml)

**Arguments**:

  -----------
  include_obs : bool
  Include period before the forecast date
  include_prono : bool
  Include period after the forecast date
  

**Returns**:

  --------
  dict : server response. Either a successfully created forecast (https://github.com/jbianchi81/alerta5DBIO/blob/master/public/schemas/a5/corrida.yml) or an error message

<a id="pydrodelta.topology.Topology.pivotData"></a>

#### pivotData

```python
def pivotData(include_tag: bool = True,
              use_output_series_id: bool = True,
              use_node_id: bool = False,
              nodes: list = None) -> DataFrame
```

Pivot variables of all nodes into columns of a single DataFrame

**Arguments**:

  -----------
  include_tag : bool (default True)
  Add columns for tags
  
  use_output_series_id : bool (default True)
  Use series_output[x].series_id as column header
  
  use_node_id : bool (default False)
  Use node.id + variable.id as column header
  
  nodes : list or None
  Nodes of the topology to read. If None, reads all self.nodes
  

**Returns**:

  --------
  DataFrame

<a id="pydrodelta.topology.Topology.pivotOutputData"></a>

#### pivotOutputData

```python
def pivotOutputData(include_tag: bool = True) -> DataFrame
```

Pivot data of all output_series of all variables of all nodes into columns of a single DataFrame

**Arguments**:

  -----------
  include_tag : bool (default True)
  Add columns for tags
  

**Returns**:

  --------
  DataFrame

<a id="pydrodelta.topology.Topology.plotVariable"></a>

#### plotVariable

```python
def plotVariable(var_id: int,
                 timestart: datetime = None,
                 timeend: datetime = None,
                 output: str = None) -> None
```

Generates time-value plots for a selected variable, one per node where this variable is found.

**Arguments**:

  ----------
  var_id : int
  Variable identifier
  
  timestart : datetime or None
  If not None, start time of the plot
  
  timeend : datetime or None
  If not None, end time of the plot
  
  output : str or None
  If not None, save the result into a pdf file

<a id="pydrodelta.topology.Topology.plotProno"></a>

#### plotProno

```python
def plotProno(output_dir: str = None,
              figsize: tuple = None,
              title: str = None,
              markersize: int = None,
              obs_label: str = None,
              tz: str = None,
              prono_label: str = None,
              footnote: str = None,
              errorBandLabel: str = None,
              obsLine: bool = None,
              prono_annotation: str = None,
              obs_annotation: str = None,
              forecast_date_annotation: str = None,
              ylim: tuple = None,
              datum_template_string: str = None,
              title_template_string: str = None,
              x_label: str = None,
              y_label: str = None,
              xlim: tuple = None,
              text_xoffset: tuple = None) -> None
```

For each series_prono (where plot_params is defined) of each variable of each node, print time-value chart including observed data

**Arguments**:

  -----------
  output_dir : str
  Output directory path
  
  figsize : tuple
  figure size in cm (width, length)
  
  title : str
  Chart title
  
  markersize : int
  Marker size in points
  
  obs_label : str
  label for observed data
  
  tz : str
  time zone
  
  prono_label : str
  Label for forecast data
  
  footnote : str
  Footnote text
  
  errorBandLabel : str
  Label for error band
  
  obsLine : bool
  Add line to observed data
  
  prono_annotation : str
  Annotation text for forecast period
  
  obs_annotation : str
  Annotation text for observations period
  
  forecast_date_annotation : str
  Annotation text for forecast date
  
  ylim : tuple
  range of y axis (min, max)
  
  datum_template_string : str
  Template string for datum text
  
  title_template_string : str
  Template string for title text
  
  x_label : str
  Label for x axis
  
  y_label : str
  Label for y axis
  
  xlim : tuple
  range of x axis (min, max)
  
  text_xoffset : tuple
  Offset of text position

<a id="pydrodelta.topology.Topology.printReport"></a>

#### printReport

```python
def printReport() -> dict
```

Print topology report

**Returns**:

  -------
  dict

<a id="pydrodelta.topology.Topology.printGraph"></a>

#### printGraph

```python
def printGraph(nodes: list = None, output_file: str = None) -> None
```

Print topology directioned graph

**Arguments**:

  -----------
  nodes : list
  If not None, use only these nodes
  
  output_file : str
  Save graph into this file (png format)
  
  See also:
  ---------
  toGraph
  exportGraph

<a id="pydrodelta.topology.Topology.toGraph"></a>

#### toGraph

```python
def toGraph(nodes=None) -> nx.DiGraph
```

Generate directioned graph from the topology.

**Arguments**:

  -----------
  nodes : list or None
  List of nodes to use for building the graph. If None, uses self.topology.nodes
  

**Returns**:

  --------
  NetworkX.DiGraph (See https://networkx.org for complete documentation)
  
  See also:
  ---------
  printGraph
  exportGraph

<a id="pydrodelta.topology.Topology.exportGraph"></a>

#### exportGraph

```python
def exportGraph(nodes: list = None, output_file: str = None) -> str
```

Creates directioned graph from the plan and converts it to JSON.

**Arguments**:

  -----------
  nodes : list or None
  List of nodes to use for building the graph. If None, uses self.topology.nodes
  
  output_file : str or None
  Where to save the JSON file. If None, returns the JSON string
  

**Returns**:

  --------
  str or None
  
  See also:
  ---------
  toGraph
  printGraph

