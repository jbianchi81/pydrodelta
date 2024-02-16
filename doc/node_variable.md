# Table of Contents

* [pydrodelta.node\_variable](#pydrodelta.node_variable)
  * [NodeVariable](#pydrodelta.node_variable.NodeVariable)
    * [id](#pydrodelta.node_variable.NodeVariable.id)
    * [metadata](#pydrodelta.node_variable.NodeVariable.metadata)
    * [fill\_value](#pydrodelta.node_variable.NodeVariable.fill_value)
    * [series\_output](#pydrodelta.node_variable.NodeVariable.series_output)
    * [series\_sim](#pydrodelta.node_variable.NodeVariable.series_sim)
    * [time\_support](#pydrodelta.node_variable.NodeVariable.time_support)
    * [adjust\_from](#pydrodelta.node_variable.NodeVariable.adjust_from)
    * [linear\_combination](#pydrodelta.node_variable.NodeVariable.linear_combination)
    * [interpolation\_limit](#pydrodelta.node_variable.NodeVariable.interpolation_limit)
    * [extrapolate](#pydrodelta.node_variable.NodeVariable.extrapolate)
    * [data](#pydrodelta.node_variable.NodeVariable.data)
    * [original\_data](#pydrodelta.node_variable.NodeVariable.original_data)
    * [adjust\_results](#pydrodelta.node_variable.NodeVariable.adjust_results)
    * [name](#pydrodelta.node_variable.NodeVariable.name)
    * [time\_interval](#pydrodelta.node_variable.NodeVariable.time_interval)
    * [\_\_init\_\_](#pydrodelta.node_variable.NodeVariable.__init__)
    * [setOriginalData](#pydrodelta.node_variable.NodeVariable.setOriginalData)
    * [toDict](#pydrodelta.node_variable.NodeVariable.toDict)
    * [toJSON](#pydrodelta.node_variable.NodeVariable.toJSON)
    * [dataAsDict](#pydrodelta.node_variable.NodeVariable.dataAsDict)
    * [originalDataAsDict](#pydrodelta.node_variable.NodeVariable.originalDataAsDict)
    * [getData](#pydrodelta.node_variable.NodeVariable.getData)
    * [toCSV](#pydrodelta.node_variable.NodeVariable.toCSV)
    * [mergeOutputData](#pydrodelta.node_variable.NodeVariable.mergeOutputData)
    * [outputToCSV](#pydrodelta.node_variable.NodeVariable.outputToCSV)
    * [toSerie](#pydrodelta.node_variable.NodeVariable.toSerie)
    * [toList](#pydrodelta.node_variable.NodeVariable.toList)
    * [outputToList](#pydrodelta.node_variable.NodeVariable.outputToList)
    * [pronoToList](#pydrodelta.node_variable.NodeVariable.pronoToList)
    * [adjust](#pydrodelta.node_variable.NodeVariable.adjust)
    * [apply\_linear\_combination](#pydrodelta.node_variable.NodeVariable.apply_linear_combination)
    * [applyMovingAverage](#pydrodelta.node_variable.NodeVariable.applyMovingAverage)
    * [adjustProno](#pydrodelta.node_variable.NodeVariable.adjustProno)
    * [setOutputData](#pydrodelta.node_variable.NodeVariable.setOutputData)
    * [uploadData](#pydrodelta.node_variable.NodeVariable.uploadData)
    * [pivotData](#pydrodelta.node_variable.NodeVariable.pivotData)
    * [pivotOutputData](#pydrodelta.node_variable.NodeVariable.pivotOutputData)
    * [seriesToDataFrame](#pydrodelta.node_variable.NodeVariable.seriesToDataFrame)
    * [saveSeries](#pydrodelta.node_variable.NodeVariable.saveSeries)
    * [concatenate](#pydrodelta.node_variable.NodeVariable.concatenate)
    * [concatenateOriginal](#pydrodelta.node_variable.NodeVariable.concatenateOriginal)
    * [concatenateProno](#pydrodelta.node_variable.NodeVariable.concatenateProno)
    * [interpolate](#pydrodelta.node_variable.NodeVariable.interpolate)
    * [saveData](#pydrodelta.node_variable.NodeVariable.saveData)
    * [plot](#pydrodelta.node_variable.NodeVariable.plot)
    * [plotProno](#pydrodelta.node_variable.NodeVariable.plotProno)

<a id="pydrodelta.node_variable"></a>

# pydrodelta.node\_variable

<a id="pydrodelta.node_variable.NodeVariable"></a>

## NodeVariable Objects

```python
class NodeVariable()
```

Variables represent the hydrologic observed/simulated properties at the node (such as discharge, precipitation, etc.). They are stored as a dictionary where and integer, the variable identifier, is used as the key, and the values are dictionaries. They may contain one or many ordered series, which contain the timestamped values. If series are missing from a variable, it is assumed that observations are not available for said variable at said node. Additionally, series_prono may be defined to represent timeseries of said variable at said node that are originated by an external modelling procedure. If series are available, said series_prono may be automatically fitted to the observed data by means of a linear regression. Such a procedure may be useful to extend the temporal extent of the variable into the forecast horizon so as to cover the full time domain of the plan. Finally, one or many series_sim may be added and it is where simulated data (as a result of a procedure) will be stored. All series have a series_id identifier which is used to read/write data from data source whether it be an alerta5DBIO instance or a csv file.

<a id="pydrodelta.node_variable.NodeVariable.id"></a>

#### id

Id of the variable

<a id="pydrodelta.node_variable.NodeVariable.metadata"></a>

#### metadata

Variable metadata

<a id="pydrodelta.node_variable.NodeVariable.fill_value"></a>

#### fill\_value

Value used to fill missing values

<a id="pydrodelta.node_variable.NodeVariable.series_output"></a>

#### series\_output

```python
@property
def series_output() -> List[NodeSerie]
```

Output series of the analysis procedure

<a id="pydrodelta.node_variable.NodeVariable.series_sim"></a>

#### series\_sim

```python
@property
def series_sim() -> List[NodeSerieProno]
```

Output series of the simulation procedure

<a id="pydrodelta.node_variable.NodeVariable.time_support"></a>

#### time\_support

Time support of the observations . The time interval that the observation is representative of.

<a id="pydrodelta.node_variable.NodeVariable.adjust_from"></a>

#### adjust\_from

Adjust configuration. 'truth' and 'sim' are the indexes of the .series to be used for the linear regression adjustment.

<a id="pydrodelta.node_variable.NodeVariable.linear_combination"></a>

#### linear\_combination

Linear combination configuration. 'intercept' is the additive term (bias) and the 'coefficients' are the ordered coefficients for each series (independent variables).

<a id="pydrodelta.node_variable.NodeVariable.interpolation_limit"></a>

#### interpolation\_limit

Maximum rows to interpolate

<a id="pydrodelta.node_variable.NodeVariable.extrapolate"></a>

#### extrapolate

If true, extrapolate data up to a distance of limit

<a id="pydrodelta.node_variable.NodeVariable.data"></a>

#### data

DataFrame containing the variable time series data

<a id="pydrodelta.node_variable.NodeVariable.original_data"></a>

#### original\_data

DataFrame containing the original variable time series data

<a id="pydrodelta.node_variable.NodeVariable.adjust_results"></a>

#### adjust\_results

Model resultant of the adjustment procedure

<a id="pydrodelta.node_variable.NodeVariable.name"></a>

#### name

```python
@property
def name() -> str
```

Name of the node_variable

<a id="pydrodelta.node_variable.NodeVariable.time_interval"></a>

#### time\_interval

Intended time spacing of the variable

<a id="pydrodelta.node_variable.NodeVariable.__init__"></a>

#### \_\_init\_\_

```python
def __init__(id: int,
             node,
             fill_value: float = None,
             series_output: List[Union[dict, NodeSerie]] = None,
             output_series_id: int = None,
             series_sim: List[Union[dict, NodeSerie]] = None,
             time_support: Union[datetime, dict, int, str] = None,
             adjust_from: AdjustFrom = None,
             linear_combination: LinearCombination = None,
             interpolation_limit: int = None,
             extrapolate: bool = False,
             time_interval: Union[timedelta, dict, float] = None)
```

**Arguments**:

  -----------
  id : int
  Id of the variable
  
  node : Node
  Node that contains this variable
  
  fill_value : float = None
  Value used to fill missing values
  
  series_output : List[Union[dict,NodeSerie]] = None
  Output series of the analysis procedure
  
  output_series_id : int = None
  Series id where to save the analysis procedure result
  
  series_sim : List[Union[dict,NodeSerie]] = None
  Output series of the simulation procedure
  
  time_support : Union[datetime,dict,int,str] = None
  Time support of the observations . The time interval that the observation is representative of.
  
  adjust_from : AdjustFrom = None
  Adjust configuration. 'truth' and 'sim' are the indexes of the .series to be used for the linear regression adjustment.
  
  linear_combination : LinearCombination = None
  Linear combination configuration. 'intercept' is the additive term (bias) and the 'coefficients' are the ordered coefficients for each series (independent variables)
  
  interpolation_limit : Union[timedelta,dict,float] = None
  Maximum rows to interpolate
  
  extrapolate : bool = False
  If true, extrapolate data up to a distance of limit
  
  time_interval : Union[timedelta,dict,float] = None
  Intended time spacing of the variable

<a id="pydrodelta.node_variable.NodeVariable.setOriginalData"></a>

#### setOriginalData

```python
def setOriginalData()
```

copies .data into .original_data

<a id="pydrodelta.node_variable.NodeVariable.toDict"></a>

#### toDict

```python
def toDict() -> dict
```

Convert this variable to dict

<a id="pydrodelta.node_variable.NodeVariable.toJSON"></a>

#### toJSON

```python
def toJSON() -> str
```

Convert this variable to JSON string

<a id="pydrodelta.node_variable.NodeVariable.dataAsDict"></a>

#### dataAsDict

```python
def dataAsDict() -> List[dict]
```

Convert this variable's data to a list of records (dict)

<a id="pydrodelta.node_variable.NodeVariable.originalDataAsDict"></a>

#### originalDataAsDict

```python
def originalDataAsDict() -> List[dict]
```

Convert this variable's original data to a list of records (dict)

<a id="pydrodelta.node_variable.NodeVariable.getData"></a>

#### getData

```python
def getData(include_series_id: bool = False) -> pandas.DataFrame
```

Read this variable's .data

**Arguments**:

  -----------
- `include_series_id` - bool = False
  Add a series_id column
  

**Returns**:

  --------
  data : DataFrame

<a id="pydrodelta.node_variable.NodeVariable.toCSV"></a>

#### toCSV

```python
def toCSV(include_series_id: bool = False, include_header: bool = True) -> str
```

Convert this variable's .data to a csv string

**Arguments**:

  -----------
  include_series_id : bool = False
  Add a series_id column
  
  include_header : bool = True
  Add a header row
  

**Returns**:

  --------
  A csv string : str

<a id="pydrodelta.node_variable.NodeVariable.mergeOutputData"></a>

#### mergeOutputData

```python
def mergeOutputData() -> pandas.DataFrame
```

Merges data of all self.series_output into a single dataframe

**Returns**:

  --------
  merged data : DataFrame

<a id="pydrodelta.node_variable.NodeVariable.outputToCSV"></a>

#### outputToCSV

```python
def outputToCSV(include_header: bool = True) -> str
```

Converts .data of self.series_output to a csv string

**Arguments**:

  -----------
  include_header : bool = True
  Add a header row
  

**Returns**:

  --------
  A csv string : str

<a id="pydrodelta.node_variable.NodeVariable.toSerie"></a>

#### toSerie

```python
def toSerie(include_series_id: bool = False,
            use_node_id: bool = False) -> Serie
```

Convert variable to Serie object using self.data as observaciones

**Arguments**:

  -----------
  include_series_id : bool = False
  Add series_id attribute to observaciones
  
  use_node_id : bool = False
  Use node id as series_id
  

**Returns**:

  --------
  A Serie object : Serie

<a id="pydrodelta.node_variable.NodeVariable.toList"></a>

#### toList

```python
def toList(include_series_id: bool = False,
           use_node_id: bool = False) -> List[dict]
```

Convert .data to list of records (dict)

**Arguments**:

  -----------
  include_series_id : bool = False
  Add series_id attribute to observaciones
  
  use_node_id : bool = False
  Use node id as series_id
  

**Returns**:

  --------
  A list of records : List[dict]

<a id="pydrodelta.node_variable.NodeVariable.outputToList"></a>

#### outputToList

```python
def outputToList(flatten: bool = True) -> Union[List[dict], List[Serie]]
```

Convert series_output to list of records (dict)

**Arguments**:

  -----------
  flatten : bool = True
  If True, merges observations into single list. Else, returns list of series objects: [{series_id:int, observaciones:[{obs1},{obs2},...]},...]
  

**Returns**:

  List of records (dict) or list of Series : Union[List[dict],List[Serie]]

<a id="pydrodelta.node_variable.NodeVariable.pronoToList"></a>

#### pronoToList

```python
def pronoToList(flatten: bool = True) -> Union[List[dict], List[Serie]]
```

Convert series_prono to list of records (dict)

**Arguments**:

  -----------
  flatten : bool = True
  If True, merges observations into single list. Else, returns list of series objects: [{series_id:int, observaciones:[{obs1},{obs2},...]},...]
  

**Returns**:

  List of records (dict) or list of Series : Union[List[dict],List[Serie]]

<a id="pydrodelta.node_variable.NodeVariable.adjust"></a>

#### adjust

```python
def adjust(plot: bool = True,
           error_band: bool = True,
           sim: int = None,
           truth: int = None) -> None
```

By means of a linear regression, adjust data of one of .series ('sim') from data of another .series ('truth')

**Arguments**:

  -----------
  plot : bool = True
  Plot results
  
  error_band : bool = True
  Add error band to results
  
  sim : int = None
  Index of the series to adjust. If None, takes .adjust_from["sim"]
  
  truth : int = None
  Index of the series to adjust from. In None, takes .adjust_from["truth"]

<a id="pydrodelta.node_variable.NodeVariable.apply_linear_combination"></a>

#### apply\_linear\_combination

```python
def apply_linear_combination(
        plot: bool = True,
        series_index: int = 0,
        linear_combination: LinearCombination = None) -> None
```

Apply linear combination

**Arguments**:

  -----------
  plot : bool = True
  Plot results
  
  series_index : int = 0
  Index of target series
  
  linear_combination : LinearCombination = None
  Linear combination parameters: "intercept" and "coefficients". If None, reads from self.linear_combination

<a id="pydrodelta.node_variable.NodeVariable.applyMovingAverage"></a>

#### applyMovingAverage

```python
def applyMovingAverage() -> None
```

For each serie in .series, apply moving average

<a id="pydrodelta.node_variable.NodeVariable.adjustProno"></a>

#### adjustProno

```python
def adjustProno(error_band: bool = True) -> None
```

For each serie in series_prono where adjust is True, perform adjustment against observed data (series[0].data). series_prono[x].data are updated with the results of the adjustment

**Arguments**:

  -----------
  error_band : bool = True
  Add error band to results

<a id="pydrodelta.node_variable.NodeVariable.setOutputData"></a>

#### setOutputData

```python
def setOutputData() -> None
```

Copies .data into each series_output .data, and applies offset where .x_offset and/or y_offset are set

<a id="pydrodelta.node_variable.NodeVariable.uploadData"></a>

#### uploadData

```python
def uploadData(include_prono: bool = False) -> list
```

Uploads series_output (analysis results) to output API. For each serie in series_output, it converts .data into a list of records, uploads the records using .series_id as the series identifier, then concatenates all responses into a single list which it returns

**Arguments**:

  -----------
  include_prono : bool = False
  Includes the forecast period of data
  

**Returns**:

  --------
  Created observations : list

<a id="pydrodelta.node_variable.NodeVariable.pivotData"></a>

#### pivotData

```python
def pivotData(include_prono: bool = True) -> pandas.DataFrame
```

Joins all series into a single pivoted DataFrame

**Arguments**:

  -----------
  include_prono : bool = True
  Join also all series in series_prono
  

**Returns**:

  --------
  pivoted data : DataFrame

<a id="pydrodelta.node_variable.NodeVariable.pivotOutputData"></a>

#### pivotOutputData

```python
def pivotOutputData(include_tag: bool = True) -> pandas.DataFrame
```

Joins all series in series_output into a single pivoted DataFrame

**Arguments**:

  -----------
  include_tag : bool = True
  Add columns for tags
  

**Returns**:

  --------
  pivoted data : DataFrame

<a id="pydrodelta.node_variable.NodeVariable.seriesToDataFrame"></a>

#### seriesToDataFrame

```python
def seriesToDataFrame(pivot: bool = False,
                      include_prono: bool = True) -> pandas.DataFrame
```

Joins all series in series_output into a single DataFrame

**Arguments**:

  -----------
  pivot : bool = False
  Pivot series into columns
  
  include_prono : bool = True
  Include forecast period
  

**Returns**:

  --------
  joined data : DataFrame

<a id="pydrodelta.node_variable.NodeVariable.saveSeries"></a>

#### saveSeries

```python
def saveSeries(output: str, format: str = "csv", pivot: bool = False) -> None
```

Joins all series into a single DataFrame and saves as a csv or json file

**Arguments**:

  -----------
  output : str
  The path of file to create
  
  format : str = "csv"
  The output format. Either "csv" or "json"
  
  pivot : bool = False
  Pivot series into columns

<a id="pydrodelta.node_variable.NodeVariable.concatenate"></a>

#### concatenate

```python
def concatenate(data: pandas.DataFrame,
                inline: bool = True,
                overwrite: bool = False,
                extend: bool = True) -> Union[pandas.DataFrame, None]
```

Concatenates self.data with data

**Arguments**:

  -----------
- `data` - pandas.DataFrame
  Input DataFrame to concatenate with self.data
  
  inline : bool = True
  Save result into self.data. If false, return concatenated result
  
  overwrite : bool = False
  Overwrite records in self.data with records in data
  
  extend : bool = True
  Extend index of self.data with that of data
  

**Returns**:

  --------
  None or DataFrame : Union[pandas.DataFrame,None]

<a id="pydrodelta.node_variable.NodeVariable.concatenateOriginal"></a>

#### concatenateOriginal

```python
def concatenateOriginal(
        data: pandas.DataFrame,
        inline: bool = True,
        overwrite: bool = False) -> Union[pandas.DataFrame, None]
```

Concatenates self.original_data with data

**Arguments**:

  -----------
  data : DataFrame
  Input data to concatenate with self.original_data
  
  inline : bool = True
  Save result into self.data. If false, return concatenated result
  
  overwrite : bool = False
  Overwrite records in self.data with records in data
  

**Returns**:

  --------
  None or DataFrame : Union[pandas.DataFrame,None]

<a id="pydrodelta.node_variable.NodeVariable.concatenateProno"></a>

#### concatenateProno

```python
def concatenateProno(
        inline: bool = True,
        ignore_warmup: bool = True) -> Union[pandas.DataFrame, None]
```

Fills nulls of data with prono

**Arguments**:

  -----------
  inline : bool = True
  Save into self.data. If False return concatenated dataframe
  
  ignore_warmup : bool = ture
  Ignore prono before last observation
  

**Returns**:

  --------
  None or DataFrame : Union[pandas.DataFrame,None]

<a id="pydrodelta.node_variable.NodeVariable.interpolate"></a>

#### interpolate

```python
def interpolate(limit: timedelta = None, extrapolate: bool = None) -> None
```

Interpolate missing values in .data

**Arguments**:

  -----------
  limit : timedelta = None
  Maximum interpolation distance
  
  extrapolate : bool = None
  Extrapolate up to a limit of limit

<a id="pydrodelta.node_variable.NodeVariable.saveData"></a>

#### saveData

```python
def saveData(output: str, format: str = "csv") -> None
```

Saves .data into csv or json file

**Arguments**:

  -----------
  output : str
  File path where to save
  
  format : str = "csv"
  Output format. Either "csv" or "json"

<a id="pydrodelta.node_variable.NodeVariable.plot"></a>

#### plot

```python
def plot() -> None
```

Plot .data together with .series

<a id="pydrodelta.node_variable.NodeVariable.plotProno"></a>

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
              station_name: str = None,
              ydisplay: float = None,
              text_xoffset: float = None,
              xytext: tuple = None,
              datum_template_string: str = None,
              title_template_string: str = None,
              x_label: str = None,
              y_label: str = None,
              xlim: tuple = None) -> None
```

For each serie in series_prono, plot .data time series together with observed data series[0].data

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

