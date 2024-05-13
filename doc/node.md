# Table of Contents

* [pydrodelta.node](#pydrodelta.node)
  * [Node](#pydrodelta.node.Node)
    * [id](#pydrodelta.node.Node.id)
    * [tipo](#pydrodelta.node.Node.tipo)
    * [name](#pydrodelta.node.Node.name)
    * [timestart](#pydrodelta.node.Node.timestart)
    * [timeend](#pydrodelta.node.Node.timeend)
    * [forecast\_timeend](#pydrodelta.node.Node.forecast_timeend)
    * [time\_interval](#pydrodelta.node.Node.time_interval)
    * [time\_offset](#pydrodelta.node.Node.time_offset)
    * [hec\_node](#pydrodelta.node.Node.hec_node)
    * [description](#pydrodelta.node.Node.description)
    * [variables](#pydrodelta.node.Node.variables)
    * [node\_type](#pydrodelta.node.Node.node_type)
    * [basin\_pars](#pydrodelta.node.Node.basin_pars)
    * [api\_config](#pydrodelta.node.Node.api_config)
    * [\_\_init\_\_](#pydrodelta.node.Node.__init__)
    * [setOriginalData](#pydrodelta.node.Node.setOriginalData)
    * [toDict](#pydrodelta.node.Node.toDict)
    * [createDatetimeIndex](#pydrodelta.node.Node.createDatetimeIndex)
    * [toCSV](#pydrodelta.node.Node.toCSV)
    * [outputToCSV](#pydrodelta.node.Node.outputToCSV)
    * [variablesToSeries](#pydrodelta.node.Node.variablesToSeries)
    * [variablesOutputToList](#pydrodelta.node.Node.variablesOutputToList)
    * [variablesPronoToList](#pydrodelta.node.Node.variablesPronoToList)
    * [adjust](#pydrodelta.node.Node.adjust)
    * [apply\_linear\_combination](#pydrodelta.node.Node.apply_linear_combination)
    * [adjustProno](#pydrodelta.node.Node.adjustProno)
    * [setOutputData](#pydrodelta.node.Node.setOutputData)
    * [uploadData](#pydrodelta.node.Node.uploadData)
    * [pivotData](#pydrodelta.node.Node.pivotData)
    * [pivotOutputData](#pydrodelta.node.Node.pivotOutputData)
    * [pivotSimData](#pydrodelta.node.Node.pivotSimData)
    * [seriesToDataFrame](#pydrodelta.node.Node.seriesToDataFrame)
    * [saveSeries](#pydrodelta.node.Node.saveSeries)
    * [concatenateProno](#pydrodelta.node.Node.concatenateProno)
    * [interpolate](#pydrodelta.node.Node.interpolate)
    * [plot](#pydrodelta.node.Node.plot)
    * [plotProno](#pydrodelta.node.Node.plotProno)
    * [loadData](#pydrodelta.node.Node.loadData)
    * [removeOutliers](#pydrodelta.node.Node.removeOutliers)
    * [detectJumps](#pydrodelta.node.Node.detectJumps)
    * [applyOffset](#pydrodelta.node.Node.applyOffset)
    * [regularize](#pydrodelta.node.Node.regularize)
    * [fillNulls](#pydrodelta.node.Node.fillNulls)
    * [derive](#pydrodelta.node.Node.derive)
    * [applyMovingAverage](#pydrodelta.node.Node.applyMovingAverage)
    * [saveSeries](#pydrodelta.node.Node.saveSeries)

<a id="pydrodelta.node"></a>

# pydrodelta.node

<a id="pydrodelta.node.Node"></a>

## Node Objects

```python
class Node()
```

<a id="pydrodelta.node.Node.id"></a>

#### id

Numeric identifier of the node

<a id="pydrodelta.node.Node.tipo"></a>

#### tipo

Type of node according to its geometry. Either 'puntual', 'areal' or 'raster'

<a id="pydrodelta.node.Node.name"></a>

#### name

Name of the node

<a id="pydrodelta.node.Node.timestart"></a>

#### timestart

Start time of the observations

<a id="pydrodelta.node.Node.timeend"></a>

#### timeend

End time of the observations

<a id="pydrodelta.node.Node.forecast_timeend"></a>

#### forecast\_timeend

Time end of the forecast

<a id="pydrodelta.node.Node.time_interval"></a>

#### time\_interval

Intended time step of the observations/forecasts

<a id="pydrodelta.node.Node.time_offset"></a>

#### time\_offset

Start time of the observations/forecasts relative to zero local time

<a id="pydrodelta.node.Node.hec_node"></a>

#### hec\_node

Mapping of this node to HECRAS geometry

<a id="pydrodelta.node.Node.description"></a>

#### description

Node description

<a id="pydrodelta.node.Node.variables"></a>

#### variables

```python
@property
def variables() -> Dict[int, Union[ObservedNodeVariable, DerivedNodeVariable]]
```

Variables represent the hydrologic observed/simulated properties at the node (such as discharge, precipitation, etc.). They are stored as a dictionary where an integer, the variable identifier, is used as the key, and the values are dictionaries. They may contain one or many ordered series, which contain the timestamped values. If series are missing from a variable, it is assumed that observations are not available for said variable at said node. Additionally, series_prono may be defined to represent timeseries of said variable at said node that are originated by an external modelling procedure. If series are available, said series_prono may be automatically fitted to the observed data by means of a linear regression. Such a procedure may be useful to extend the temporal extent of the variable into the forecast horizon so as to cover the full time domain of the plan. Finally, one or many series_sim may be added and it is where simulated data (as a result of a procedure) will be stored. All series have a series_id identifier which is used to read/write data from data source whether it be an alerta5DBIO instance or a csv file.

<a id="pydrodelta.node.Node.node_type"></a>

#### node\_type

The type of node: either 'station' or 'basin'

<a id="pydrodelta.node.Node.basin_pars"></a>

#### basin\_pars

Basin parameters. For nodes of type='basin'

Properties:
-----------
- area : float - Basin area in square meters
- ae : float - Basin effective drainage area ([0-1] fraction)
- rho : float - Basin mean soil porosity ([0-1] fraction)
- wp : float - Basin mean wilting point  ([0-1] fraction)
- area_id : int - Basin identifier at a5 input API

<a id="pydrodelta.node.Node.api_config"></a>

#### api\_config

"Input api configuration

Properties:
-----------
- url : str - api base url
- token : str - api authorization token

<a id="pydrodelta.node.Node.__init__"></a>

#### \_\_init\_\_

```python
def __init__(id: int,
             name: str,
             time_interval: Union[dict, int],
             tipo: str = "puntual",
             timestart: datetime = None,
             timeend: datetime = None,
             forecast_timeend: datetime = None,
             plan=None,
             time_offset: timedelta = None,
             topology=None,
             hec_node: dict = None,
             variables: List[Union[DerivedNodeVariableDict,
                                   ObservedNodeVariableDict,
                                   DerivedNodeVariable,
                                   ObservedNodeVariable]] = list(),
             node_type: str = "station",
             description: str = None,
             basin_pars: dict = None,
             api_config: dict = None)
```

Nodes represent stations and basins. These nodes are identified with a node_id and must contain one or many variables each, which represent the hydrologic observed/simulated properties at that node (such as discharge, precipitation, etc.). They are identified with a variable_id and may contain one or many ordered series, which contain the timestamped values. If series are missing from a variable, it is assumed that observations are not available for said variable at said node. Additionally, series_prono may be defined to represent timeseries of said variable at said node that are originated by an external modelling procedure. If series are available, said series_prono may be automatically fitted to the observed data by means of a linear regression. Such a procedure may be useful to extend the temporal extent of the variable into the forecast horizon so as to cover the full time domain of the plan. Finally, one or many series_sim may be added and it is where simulated data (as a result of a procedure) will be stored. All series have a series_id identifier which is used to read/write data from data source whether it be an alerta5DBIO instance or a csv file.

**Arguments**:

  -----------
  id : int
  The node identifier
  
  name : str
  The node name
  
  time_interval : Union[dict,int]
  Intended time step of the observations/forecasts
  
  tipo : str="puntual"
  Type of node according to its geometry. Either 'puntual', 'areal' or 'raster'
  
  timestart : datetime = None
  Start time of the observations
  
  timeend : datetime = None
  End time of the observations
  
  forecast_timeend : datetime = None
  Time end of the forecast
  
  plan : Plan = None
  Plan that contains the topology that contains this node
  
  time_offset : timedelta = None
  Start time of the observations/forecasts relative to zero local time
  
  topology : Topology = None
  The topology that contains this node
  
  hec_node : dict = None
  Mapping of this node to HECRAS geometry
  
  variables : List[Union[DerivedNodeVariable,ObservedNodeVariable]] = list()
  The hydrologic observed/simulated properties at this node
  
  node_type : str = "station"
  The type of node: either 'station' or 'basin'
  
  basin_pars : dict = None
  Basin parameters. For nodes of type = 'basin'
  
  api_config : dict = None
  Override global input api configuration
  
  - url : str
  - token : str

<a id="pydrodelta.node.Node.setOriginalData"></a>

#### setOriginalData

```python
def setOriginalData()
```

For each variable in .variables, set original data

<a id="pydrodelta.node.Node.toDict"></a>

#### toDict

```python
def toDict() -> dict
```

Convert node to dict

<a id="pydrodelta.node.Node.createDatetimeIndex"></a>

#### createDatetimeIndex

```python
def createDatetimeIndex() -> DatetimeIndex
```

Create DatetimeIndex from .time_interval, .timestart, .timeend and .time_offset

<a id="pydrodelta.node.Node.toCSV"></a>

#### toCSV

```python
def toCSV(include_series_id: bool = True, include_header: bool = True) -> str
```

returns self.variables.data as csv

**Arguments**:

  -----------
  include_series_id : bool = True
  Add a column with series_id
  
  include_header : bool = True
  Add a header row
  

**Returns**:

  --------
  csv string : str

<a id="pydrodelta.node.Node.outputToCSV"></a>

#### outputToCSV

```python
def outputToCSV(include_header: bool = True) -> str
```

returns data of self.variables.series_output as csv

**Arguments**:

  -----------
  include_header : bool = True
  Add a header row
  

**Returns**:

  --------
  csv string : csv

<a id="pydrodelta.node.Node.variablesToSeries"></a>

#### variablesToSeries

```python
def variablesToSeries(include_series_id: bool = False,
                      use_node_id: bool = False) -> List[Serie]
```

return node variables as array of Series objects using self.variables.data as observaciones

**Arguments**:

  -----------
  include_series_id : bool = False
  Add series_id property to items of Series
  
  use_node_id : bool = False
  Use node_id as series_id
  

**Returns**:

  --------
  list of Series : List[Serie]

<a id="pydrodelta.node.Node.variablesOutputToList"></a>

#### variablesOutputToList

```python
def variablesOutputToList(flatten: bool = True) -> list
```

For each variable in .variables, converts series_output to list of dict

**Arguments**:

  -----------
  flatten : bool = True
  If True, merges observations into single list. Else, returns list of series objects: [{series_id:int, observaciones:[{obs1},{obs2},...]},...]
  

**Returns**:

  --------
  list

<a id="pydrodelta.node.Node.variablesPronoToList"></a>

#### variablesPronoToList

```python
def variablesPronoToList(flatten: bool = True) -> list
```

For each variable in .variables, returns series_prono as a list

**Arguments**:

  -----------
  flatten : bool = True
  If True, returns list of dict each containing one forecast time-value pair (pronosticos). Else returns list of dict each containing series_id:int and pronosticos:list
  

**Returns**:

  --------
  list

<a id="pydrodelta.node.Node.adjust"></a>

#### adjust

```python
def adjust(plot: bool = True, error_band: bool = True) -> None
```

For each variable in .variables, if adjust_from is set, run .adjust()

**Arguments**:

  -----------
  plot : bool = True
  Generate plot
  
  error_band : bool = True
  Add 01-99 error band to result data

<a id="pydrodelta.node.Node.apply_linear_combination"></a>

#### apply\_linear\_combination

```python
def apply_linear_combination(plot: bool = True, series_index: int = 0) -> None
```

For each variable in .variables, if linear_combination is set, run .apply_linear_combination()

**Arguments**:

  -----------
  plot : bool = True
  Generate plot
  
  series_index : int = 0
  Index of the series to apply the linear combination

<a id="pydrodelta.node.Node.adjustProno"></a>

#### adjustProno

```python
def adjustProno(error_band: bool = True) -> None
```

For each variable in .variables run .adjustProno()

**Arguments**:

  -----------
  error_band : bool = True
  Add 01-99 error band to result data

<a id="pydrodelta.node.Node.setOutputData"></a>

#### setOutputData

```python
def setOutputData() -> None
```

For each variable in .variables run setOutputData()

<a id="pydrodelta.node.Node.uploadData"></a>

#### uploadData

```python
def uploadData(include_prono: bool = False, api_config: dict = None) -> list
```

For each variable in .variables run .uploadData()

**Arguments**:

  -----------
  include_prono : bool = False
  Concatenate forecast into the data to upload
  

**Returns**:

  --------
  created observations : list
  
  api_config : dict = None
  Api connection parameters. Overrides global config.output_api
  
  Properties:
  - url : str
  - token : str
  - proxy_dict : dict

<a id="pydrodelta.node.Node.pivotData"></a>

#### pivotData

```python
def pivotData(include_prono: bool = True) -> DataFrame
```

Join all variables' data into a single pivoted DataFrame

**Arguments**:

  -----------
  include_prono : bool = False
  Concatenate forecast into the observed data
  

**Returns**:

  --------
  joined, pivoted data : DataFrame

<a id="pydrodelta.node.Node.pivotOutputData"></a>

#### pivotOutputData

```python
def pivotOutputData(include_tag: bool = True) -> DataFrame
```

Join all variables' output data into a single pivoted DataFrame

**Arguments**:

  -----------
  include_tag : bool = True
  Include tag columns
  

**Returns**:

  --------
  joined, pivoted data : DataFrame

<a id="pydrodelta.node.Node.pivotSimData"></a>

#### pivotSimData

```python
def pivotSimData() -> DataFrame
```

Join all variables' sim data into a single pivoted DataFrame

**Returns**:

  --------
  joined, pivoted data : DataFrame

<a id="pydrodelta.node.Node.seriesToDataFrame"></a>

#### seriesToDataFrame

```python
def seriesToDataFrame(pivot: bool = False,
                      include_prono: bool = True) -> DataFrame
```

Join all variables' series data into a single DataFrame

**Arguments**:

  -----------
  include_prono : bool = False
  Concatenate forecast into the observed data
  
  pivot : bool = True
  Pivot series into columns
  

**Returns**:

  --------
  data : DataFrame

<a id="pydrodelta.node.Node.saveSeries"></a>

#### saveSeries

```python
def saveSeries(output: str, format: str = "csv", pivot: bool = False) -> None
```

Join all variables' series data into a single DataFrame and save as csv or json file

**Arguments**:

  -----------
  output : str
  File path where to save
  
  format : str = "csv"
  Output format, either "csv" or "json"
  
  pivot : bool = True
  Pivot series into columns

<a id="pydrodelta.node.Node.concatenateProno"></a>

#### concatenateProno

```python
def concatenateProno(inline: bool = True,
                     ignore_warmup: bool = True) -> DataFrame
```

Join every variable in .variables, run .concatenateProno().

**Arguments**:

  -----------
  inline : bool = True
  If True, stores concatenation results into each variables' data
  If set to False, appends all results together and returns the resulting DataFrame
  
  ignore_warmup : bool = True
  Skips data values where timestart predates the forecast_date
  

**Returns**:

  --------
  None or DataFrame

<a id="pydrodelta.node.Node.interpolate"></a>

#### interpolate

```python
def interpolate(limit: timedelta = None, extrapolate: bool = None) -> None
```

Join every variable in .variables, run .interpolate().

**Arguments**:

  -----------
  limit : timedelta = None
  Maximum time distance to interpolate
  
  extrapolate : bool = None
  If true, extrapolate data up to a distance of limit

<a id="pydrodelta.node.Node.plot"></a>

#### plot

```python
def plot() -> None
```

For each variable of .variables run .plot()

<a id="pydrodelta.node.Node.plotProno"></a>

#### plotProno

```python
def plotProno(**kwargs) -> None
```

For each variable in .variables run .plotProno()

**Arguments**:

  -----------
  output_dir : str = None
  Directory path where to save the plots
  
  figsize : tuple = None
  Figure size (width, height) in cm
  
- `title` - str = None
  Figure title
  
  markersize : int = None
  Size of marker in points
  
  obs_label : str = None
  Label for observed data
  
  tz : str = None
  Time zone for horizontal axis
  
  prono_label : str = None
  Label for forecast data
  
  footnote : str = None
  Footnote text
  
  errorBandLabel : str = None
  Label for error band
  
  obsLine : bool = None
  Add a line to observed data
  
  prono_annotation : str = None
  Annotation for forecast data
  
  obs_annotation : str = None
  Annotation for observed data
  
  forecast_date_annotation : str = None
  Annotation for forecast date
  
  ylim : tuple = None
  Y axis range (min, max)
  
  station_name : str = None
  Station name
  
  ydisplay : float = None
  Y position of annotations
  
  text_xoffset : float = None
  X offset of annotations
  
  xytext : tuple = None
  Not used
  
  datum_template_string : str = None
  Template string for datum text
  
  title_template_string : str = None
  Template string for title
  
  x_label : str = None
  Label for x axis
  
  y_label : str = None
  Label for y axis
  
  xlim : tuple = None
  Range of x axis (min, max)
  
  prono_fmt : str = '-'
  Style for forecast series
  
  annotate : bool = True
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

<a id="pydrodelta.node.Node.loadData"></a>

#### loadData

```python
def loadData(timestart: Union[datetime, str, dict],
             timeend: Union[datetime, str, dict],
             include_prono: bool = True,
             forecast_timeend: Union[datetime, str, dict] = None,
             input_api_config: dict = None,
             no_metadata: bool = False) -> None
```

For each variable in variables, if variable is an ObservedNodeVariable run .loadData()

**Arguments**:

  -----------
  timestart : Union[datetime,str,dict]
  Begin date
  
  timeend : Union[datetime,str,dict]
  End date
  
  include_prono : bool = True
  For each variable, load forecast data for each series of .series_prono
  
  forecast_timeend : Union[datetime,str,dict] = None
  End date of forecast retrieval. If None, uses timeend
  
  input_api_config : dict
  Api connection parameters. Overrides global config.input_api
  
  Properties:
  - url : str
  - token : str
  - proxy_dict : dict
  
  no_metadata : bool = False
  Don't retrieve series metadata on load from api

<a id="pydrodelta.node.Node.removeOutliers"></a>

#### removeOutliers

```python
def removeOutliers() -> bool
```

For each variable of .variables, if variable is an ObservedNodeVariable, run .removeOutliers(). Removes outilers and returns True if any outliers were removed

**Returns**:

  --------
  bool

<a id="pydrodelta.node.Node.detectJumps"></a>

#### detectJumps

```python
def detectJumps() -> bool
```

For each variable of .variables, if variable is an ObservedNodeVariable, run .detectJumps(). Returns True if any jumps were found

**Returns**:

  --------
  bool

<a id="pydrodelta.node.Node.applyOffset"></a>

#### applyOffset

```python
def applyOffset() -> None
```

For each variable of .variables, if variable is an ObservedNodeVariable, run .applyOffset()

<a id="pydrodelta.node.Node.regularize"></a>

#### regularize

```python
def regularize(interpolate: bool = False) -> None
```

For each variable of .variables, if variable is an ObservedNodeVariable, run .regularize().

**Arguments**:

  -----------
  interpolate : bool = False
  Interpolate missing values

<a id="pydrodelta.node.Node.fillNulls"></a>

#### fillNulls

```python
def fillNulls(inline: bool = True, fill_value: float = None) -> None
```

For each variable of .variables, if variable is an ObservedNodeVariable, run .fillNulls().

**Arguments**:

  -----------
  inline : bool = True
  Store result in variables' data property
  
  fill_value : float = None
  Fill missing values with this value

<a id="pydrodelta.node.Node.derive"></a>

#### derive

```python
def derive() -> None
```

For each variable of .variables, if variable is a DerivedNodeVariable, run .derive()

<a id="pydrodelta.node.Node.applyMovingAverage"></a>

#### applyMovingAverage

```python
def applyMovingAverage() -> None
```

For each variable of .variables fun applyMovingAverage()

<a id="pydrodelta.node.Node.saveSeries"></a>

#### saveSeries

```python
def saveSeries()
```

For each series, series_prono, series_sim and series_output of each variable, save data into file if .output_file is defined

