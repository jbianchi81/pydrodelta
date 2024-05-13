# Table of Contents

* [pydrodelta.topology](#pydrodelta.topology)
  * [Topology](#pydrodelta.topology.Topology)
    * [timestart](#pydrodelta.topology.Topology.timestart)
    * [timeend](#pydrodelta.topology.Topology.timeend)
    * [forecast\_timeend](#pydrodelta.topology.Topology.forecast_timeend)
    * [time\_offset\_start](#pydrodelta.topology.Topology.time_offset_start)
    * [time\_offset\_end](#pydrodelta.topology.Topology.time_offset_end)
    * [interpolation\_limit](#pydrodelta.topology.Topology.interpolation_limit)
    * [extrapolate](#pydrodelta.topology.Topology.extrapolate)
    * [nodes](#pydrodelta.topology.Topology.nodes)
    * [cal\_id](#pydrodelta.topology.Topology.cal_id)
    * [plot\_params](#pydrodelta.topology.Topology.plot_params)
    * [report\_file](#pydrodelta.topology.Topology.report_file)
    * [graph](#pydrodelta.topology.Topology.graph)
    * [no\_metadata](#pydrodelta.topology.Topology.no_metadata)
    * [include\_prono](#pydrodelta.topology.Topology.include_prono)
    * [output\_csv](#pydrodelta.topology.Topology.output_csv)
    * [output\_json](#pydrodelta.topology.Topology.output_json)
    * [pivot](#pydrodelta.topology.Topology.pivot)
    * [pretty](#pydrodelta.topology.Topology.pretty)
    * [\_\_init\_\_](#pydrodelta.topology.Topology.__init__)
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
    * [pivotSimData](#pydrodelta.topology.Topology.pivotSimData)
    * [plotVariable](#pydrodelta.topology.Topology.plotVariable)
    * [plotProno](#pydrodelta.topology.Topology.plotProno)
    * [printReport](#pydrodelta.topology.Topology.printReport)
    * [printGraph](#pydrodelta.topology.Topology.printGraph)
    * [toGraph](#pydrodelta.topology.Topology.toGraph)
    * [exportGraph](#pydrodelta.topology.Topology.exportGraph)
    * [saveSeries](#pydrodelta.topology.Topology.saveSeries)

<a id="pydrodelta.topology"></a>

# pydrodelta.topology

<a id="pydrodelta.topology.Topology"></a>

## Topology Objects

```python
class Topology(Base)
```

The topology defines a list of nodes which represent stations and basins. These nodes are identified with a node_id and must contain one or many variables each, which represent the hydrologic observed/simulated properties at that node (such as discharge, precipitation, etc.). They are identified with a variable_id and may contain one or many ordered series, which contain the timestamped values. If series are missing from a variable, it is assumed that observations are not available for said variable at said node. Additionally, series_prono may be defined to represent timeseries of said variable at said node that are originated by an external modelling procedure. If series are available, said series_prono may be automatically fitted to the observed data by means of a linear regression. Such a procedure may be useful to extend the temporal extent of the variable into the forecast horizon so as to cover the full time domain of the plan. Finally, one or many series_sim may be added and it is where simulated data (as a result of a procedure) will be stored. All series have a series_id identifier which is used to read/write data from data source whether it be an alerta5DBIO instance or a csv file.

<a id="pydrodelta.topology.Topology.timestart"></a>

#### timestart

start date of observations period

<a id="pydrodelta.topology.Topology.timeend"></a>

#### timeend

end date of observations period

<a id="pydrodelta.topology.Topology.forecast_timeend"></a>

#### forecast\_timeend

forecast horizon

<a id="pydrodelta.topology.Topology.time_offset_start"></a>

#### time\_offset\_start

time of day where first timestep start

<a id="pydrodelta.topology.Topology.time_offset_end"></a>

#### time\_offset\_end

time of day where last timestep ends

<a id="pydrodelta.topology.Topology.interpolation_limit"></a>

#### interpolation\_limit

maximum duration between observations for interpolation

<a id="pydrodelta.topology.Topology.extrapolate"></a>

#### extrapolate

Extrapolate observations outside the observation time domain, up to a maximum duration equal to .interpolation_limit

<a id="pydrodelta.topology.Topology.nodes"></a>

#### nodes

```python
@property
def nodes() -> TypedList[Node]
```

Nodes represent stations and basins. These nodes are identified with a node_id and must contain one or many variables each, which represent the hydrologic observed/simulated properties at that node (such as discharge, precipitation, etc.). They are identified with a variable_id and may contain one or many ordered series, which contain the timestamped values. If series are missing from a variable, it is assumed that observations are not available for said variable at said node. Additionally, series_prono may be defined to represent timeseries of said variable at said node that are originated by an external modelling procedure. If series are available, said series_prono may be automatically fitted to the observed data by means of a linear regression. Such a procedure may be useful to extend the temporal extent of the variable into the forecast horizon so as to cover the full time domain of the plan. Finally, one or many series_sim may be added and it is where simulated data (as a result of a procedure) will be stored. All series have a series_id identifier which is used to read/write data from data source whether it be an alerta5DBIO instance or a csv file.

<a id="pydrodelta.topology.Topology.cal_id"></a>

#### cal\_id

Identifier for saving analysis results as forecast (i.e. using .uploadDataAsProno)

<a id="pydrodelta.topology.Topology.plot_params"></a>

#### plot\_params

Plotting configuration. See .plotProno

<a id="pydrodelta.topology.Topology.report_file"></a>

#### report\_file

Write analysis report into this file

<a id="pydrodelta.topology.Topology.graph"></a>

#### graph

```python
@property
def graph() -> nx.DiGraph
```

Directional graph representing this topology

<a id="pydrodelta.topology.Topology.no_metadata"></a>

#### no\_metadata

Don't retrieve series metadata on load from api

<a id="pydrodelta.topology.Topology.include_prono"></a>

#### include\_prono

While executing .batchProcessInput, use series_prono to fill nulls of series

<a id="pydrodelta.topology.Topology.output_csv"></a>

#### output\_csv

Save analysis results as csv into this path (relative to PYDRODELTA_DIR)

<a id="pydrodelta.topology.Topology.output_json"></a>

#### output\_json

Save analysis results as json into this path (relative to PYDRODELTA_DIR)

<a id="pydrodelta.topology.Topology.pivot"></a>

#### pivot

If output_csv is set, pivot series into columns of the table (default True)

<a id="pydrodelta.topology.Topology.pretty"></a>

#### pretty

For output_json, prettify json

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
             nodes: List[Union[Node, NodeDict]] = list(),
             cal_id: Union[int, None] = None,
             plot_params: Union[PlotParamsDict, None] = None,
             report_file: Union[str, None] = None,
             plan=None,
             no_metadata: bool = False,
             plot_variable: List[PlotVariableParamsDict] = None,
             include_prono: bool = False,
             output_csv: str = None,
             output_json: str = None,
             pivot: bool = True,
             pretty: bool = True,
             **kwargs)
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
  
  nodes : List[Union[Node,NodeDict]]
  Nodes represent stations and basins. These nodes are identified with a node_id and must contain one or many variables each, which represent the hydrologic observed/simulated properties at that node (such as discharge, precipitation, etc.). They are identified with a variable_id and may contain one or many ordered series, which contain the timestamped values. If series are missing from a variable, it is assumed that observations are not available for said variable at said node. Additionally, series_prono may be defined to represent timeseries of said variable at said node that are originated by an external modelling procedure. If series are available, said series_prono may be automatically fitted to the observed data by means of a linear regression. Such a procedure may be useful to extend the temporal extent of the variable into the forecast horizon so as to cover the full time domain of the plan. Finally, one or many series_sim may be added and it is where simulated data (as a result of a procedure) will be stored. All series have a series_id identifier which is used to read/write data from data source whether it be an alerta5DBIO instance or a csv file.
  
  cal_id : int or None
  Identifier for saving analysis results as forecast (i.e. using .uploadDataAsProno)
  
  plot_params : dict or None
  Plotting configuration. See .plotProno
  
  report_file : str or None
  Write analysis report into this file
  
  plan : Plan
  Plan containing this topology
  
  no_metadata : bool = False
  Don't retrieve series metadata on load from api
  
  plot_variable : List[PlotVariableParamsDict] = None
  Print graphs to pdf files of the selected variables at every node where said variables are defined
  PlotVariableParamsDict:
  var_id : int
  output : str
  timestart : Union[datetime,str,dict], optional
  timeend : Union[datetime,str,dict], optional
  
  include_prono : bool = False
  While executing .batchProcessInput, use series_prono to fill nulls of series
  
  output_csv : str = None
  Save analysis results as csv into this path (relative to PYDRODELTA_DIR)
  
  output_json : str = None
  Save analysis results as json into this path (relative to PYDRODELTA_DIR)
  
  pivot : bool = True
  If output_csv is set, pivot series into columns of the table
  
  pretty : bool = True
  For output_json, prettify json

<a id="pydrodelta.topology.Topology.batchProcessInput"></a>

#### batchProcessInput

```python
def batchProcessInput(include_prono: bool = None,
                      input_api_config: dict = None) -> None
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
  
  input_api_config : dict
  Api connection parameters (used to load data). Overrides global config.input_api
  
  Properties:
  - url : str
  - token : str
  - proxy_dict : dict

<a id="pydrodelta.topology.Topology.loadData"></a>

#### loadData

```python
def loadData(include_prono: bool = True,
             input_api_config: dict = None,
             no_metadata: bool = None) -> None
```

For each series of each variable of each node, load data from the source.

**Arguments**:

  -----------
  
  include_prono : bool default True
  Load forecasted data
  
  input_api_config : dict
  Api connection parameters. Overrides global config.input_api
  
  Properties:
  - url : str
  - token : str
  - proxy_dict : dict
  
  no_metadata : bool = None
  Don't retrieve series metadata on load from api. If not given, reads from self.no_metadata

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
def uploadData(include_prono: bool, api_config: dict = None) -> list
```

Uploads analysis data (series_output) of all variables of all nodes as a5 observaciones (https://raw.githubusercontent.com/jbianchi81/alerta5DBIO/master/public/schemas/a5/observacion.yml)

**Arguments**:

  -----------
  include_prono : bool
  Include the forecast horizon
  
  api_config : dict = None
  Api connection parameters. Overrides global config.output_api
  
  Properties:
  - url : str
  - token : str
  - proxy_dict : dict
  

**Returns**:

  list of Observations

<a id="pydrodelta.topology.Topology.uploadDataAsProno"></a>

#### uploadDataAsProno

```python
def uploadDataAsProno(include_obs: bool = True,
                      include_prono: bool = False,
                      api_config: dict = None) -> dict
```

Uploads analysis data (series_output) of all variables of all nodes to output api as a5 pronosticos (https://github.com/jbianchi81/alerta5DBIO/blob/master/public/schemas/a5/pronostico.yml)

**Arguments**:

  -----------
  include_obs : bool
  Include period before the forecast date
  include_prono : bool
  Include period after the forecast date
  api_config : dict = None
  Api connection parameters. Overrides global config.output_api
  
  Properties:
  - url : str
  - token : str
  - proxy_dict : dict
  

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

<a id="pydrodelta.topology.Topology.pivotSimData"></a>

#### pivotSimData

```python
def pivotSimData() -> DataFrame
```

Pivot data of all series_sim of all variables of all nodes into columns of a single DataFrame

**Returns**:

  --------
  DataFrame

<a id="pydrodelta.topology.Topology.plotVariable"></a>

#### plotVariable

```python
def plotVariable(var_id: int,
                 timestart: datetime = None,
                 timeend: datetime = None,
                 output: str = None,
                 extra_sim_columns: bool = True) -> None
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
  
  extra_sim_columns : bool = True
  Add additional simulation series to plot

<a id="pydrodelta.topology.Topology.plotProno"></a>

#### plotProno

```python
def plotProno(**kwargs) -> None
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
  
  prono_fmt : str
  Style for forecast series
  
  annotate : bool
  Add observed data/forecast data/forecast date annotations
  
  table_columns : list = ["Fecha", "Nivel"]
  Which forecast dataframe columns to show. Options:
  -   Fecha
  -   Nivel
  -   Hora
  -   Fechap
  -   Dia
  
  date_form : str = "%H hrs
  %d-%b"
  Date formatting string for x axis tick labels
  
  xaxis_minor_tick_hours : list = [3,9,15,21]
  Hours of location of minor ticks of x axis
  
  errorBand : tuple[str,str] = None
  Columns to use as error band (lower bound, upper bound). If not set and series_prono.adjust_results is True, "error_band_01" and "error_band_99" resulting from the adjustment are used
  
  error_band_fmt : str = None
  style for error band. Set to 'errorbar' for error bars, else fmt parameter for plot function. Optionally, a 2-tuple may be used to set different styles for lower and upper bounds, respectively
  
  forecast_table : bool = True
  Print forecast table
  
  footnote_height : float = 0.2
  Height of space for footnote in inches

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

<a id="pydrodelta.topology.Topology.saveSeries"></a>

#### saveSeries

```python
def saveSeries()
```

For each series, series_prono, series_sim and series_output of each variable of each node, save data into file if .output_file is defined

