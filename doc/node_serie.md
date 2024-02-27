# Table of Contents

* [pydrodelta.node\_serie](#pydrodelta.node_serie)
  * [NodeSerie](#pydrodelta.node_serie.NodeSerie)
    * [series\_id](#pydrodelta.node_serie.NodeSerie.series_id)
    * [type](#pydrodelta.node_serie.NodeSerie.type)
    * [lim\_outliers](#pydrodelta.node_serie.NodeSerie.lim_outliers)
    * [lim\_jump](#pydrodelta.node_serie.NodeSerie.lim_jump)
    * [x\_offset](#pydrodelta.node_serie.NodeSerie.x_offset)
    * [y\_offset](#pydrodelta.node_serie.NodeSerie.y_offset)
    * [moving\_average](#pydrodelta.node_serie.NodeSerie.moving_average)
    * [data](#pydrodelta.node_serie.NodeSerie.data)
    * [metadata](#pydrodelta.node_serie.NodeSerie.metadata)
    * [outliers\_data](#pydrodelta.node_serie.NodeSerie.outliers_data)
    * [jumps\_data](#pydrodelta.node_serie.NodeSerie.jumps_data)
    * [csv\_file](#pydrodelta.node_serie.NodeSerie.csv_file)
    * [observations](#pydrodelta.node_serie.NodeSerie.observations)
    * [save\_post](#pydrodelta.node_serie.NodeSerie.save_post)
    * [comment](#pydrodelta.node_serie.NodeSerie.comment)
    * [name](#pydrodelta.node_serie.NodeSerie.name)
    * [\_\_init\_\_](#pydrodelta.node_serie.NodeSerie.__init__)
    * [toDict](#pydrodelta.node_serie.NodeSerie.toDict)
    * [loadData](#pydrodelta.node_serie.NodeSerie.loadData)
    * [getThresholds](#pydrodelta.node_serie.NodeSerie.getThresholds)
    * [removeOutliers](#pydrodelta.node_serie.NodeSerie.removeOutliers)
    * [detectJumps](#pydrodelta.node_serie.NodeSerie.detectJumps)
    * [applyMovingAverage](#pydrodelta.node_serie.NodeSerie.applyMovingAverage)
    * [applyOffset](#pydrodelta.node_serie.NodeSerie.applyOffset)
    * [regularize](#pydrodelta.node_serie.NodeSerie.regularize)
    * [fillNulls](#pydrodelta.node_serie.NodeSerie.fillNulls)
    * [toCSV](#pydrodelta.node_serie.NodeSerie.toCSV)
    * [toList](#pydrodelta.node_serie.NodeSerie.toList)
    * [toDict](#pydrodelta.node_serie.NodeSerie.toDict)
    * [getSeriesTable](#pydrodelta.node_serie.NodeSerie.getSeriesTable)

<a id="pydrodelta.node_serie"></a>

# pydrodelta.node\_serie

<a id="pydrodelta.node_serie.NodeSerie"></a>

## NodeSerie Objects

```python
class NodeSerie()
```

Represents a timestamped series of observed or simulated values for a variable in a node.

<a id="pydrodelta.node_serie.NodeSerie.series_id"></a>

#### series\_id

Identifier of the series. If csv_file is set, reads the column identified in the header with this id. Else, unless observations is set, retrieves the identified series from the input api

<a id="pydrodelta.node_serie.NodeSerie.type"></a>

#### type

Type of the series (only for retrieval from input api). One of 'puntual', 'areal', 'raster'

<a id="pydrodelta.node_serie.NodeSerie.lim_outliers"></a>

#### lim\_outliers

```python
@property
def lim_outliers() -> tuple[float, float]
```

Minimum and maximum values for outliers removal (2-tuple of float)

<a id="pydrodelta.node_serie.NodeSerie.lim_jump"></a>

#### lim\_jump

Maximum absolute value for jump detection

<a id="pydrodelta.node_serie.NodeSerie.x_offset"></a>

#### x\_offset

Time offset applied to the timestamps of the input data on import

<a id="pydrodelta.node_serie.NodeSerie.y_offset"></a>

#### y\_offset

Offset applied to the values of the input data on import

<a id="pydrodelta.node_serie.NodeSerie.moving_average"></a>

#### moving\_average

Size of the time window used to compute a moving average to the input data

<a id="pydrodelta.node_serie.NodeSerie.data"></a>

#### data

DataFrame containing the timestamped values. Index is the time (with time zone), column 'valor' contains the values (floats) and column 'tag' contains the tag indicating the origin of the value (one of: observed, simulated, interpolated, moving_average, extrapolated, derived)

<a id="pydrodelta.node_serie.NodeSerie.metadata"></a>

#### metadata

Metadata of the series

<a id="pydrodelta.node_serie.NodeSerie.outliers_data"></a>

#### outliers\_data

Data rows containing removed outliers

<a id="pydrodelta.node_serie.NodeSerie.jumps_data"></a>

#### jumps\_data

Data rows containing detected jumps

<a id="pydrodelta.node_serie.NodeSerie.csv_file"></a>

#### csv\_file

Read data from this csv file. The csv file must have one column for the timestamps called 'timestart' and one column per series of data with the series_id in the header

<a id="pydrodelta.node_serie.NodeSerie.observations"></a>

#### observations

```python
@property
def observations() -> List[TVP]
```

Time-value pairs of data. List of dicts {'timestart':datetime, 'valor':float}, or list of 2-tuples (datetime,float)

<a id="pydrodelta.node_serie.NodeSerie.save_post"></a>

#### save\_post

Save upload payload into this file

<a id="pydrodelta.node_serie.NodeSerie.comment"></a>

#### comment

Comment about this series

<a id="pydrodelta.node_serie.NodeSerie.name"></a>

#### name

Series name

<a id="pydrodelta.node_serie.NodeSerie.__init__"></a>

#### \_\_init\_\_

```python
def __init__(series_id: int,
             tipo: str = "puntual",
             lim_outliers: tuple[float, float] = None,
             lim_jump: float = None,
             x_offset: timedelta = timedelta(seconds=0),
             y_offset: float = 0,
             moving_average: timedelta = None,
             csv_file: str = None,
             observations: Union[List[TVP], List[tuple[datetime,
                                                       float]]] = None,
             save_post: str = None,
             comment: str = None,
             name: str = None)
```

**Arguments**:

  -----------
  series_id : int
  Identifier of the series. If csv_file is set, reads the column identified in the header with this id. Else, unless observations is set, retrieves the identified series from the input api
  
  tipo : str = "puntual"
  Type of the series (only for retrieval from input api). One of 'puntual', 'areal', 'raster'
  
  lim_outliers : tuple[float,float] = None
  Minimum and maximum values for outliers removal (2-tuple of float)
  
  lim_jump : float = None
  Maximum absolute value for jump detection
  
  x_offset : timedelta = timedelta(seconds=0)
  Apply this time offset to the timestamps of the input data
  
  y_offset : float = 0
  Apply this offset to the values of the input data
  
  moving_average : timedelta = None
  Compute a moving average using a time window of this size to the input data
  
  csv_file : str = None
  Read data from this csv file. The csv file must have one column for the timestamps called 'timestart' and one column per series of data with the series_id in the header
  
  observations : Union[List[TVP],List[tuple[datetime,float]]] = None
  Time-value pairs of data. List of dicts {'timestart':datetime, 'valor':float}, or list of 2-tuples (datetime,float)
  
  save_post : str = None
  Save upload payload into this file

<a id="pydrodelta.node_serie.NodeSerie.toDict"></a>

#### toDict

```python
def toDict() -> dict
```

Convert series to dict

<a id="pydrodelta.node_serie.NodeSerie.loadData"></a>

#### loadData

```python
def loadData(timestart: timedelta, timeend: timedelta) -> None
```

Load data from source according to configuration.

Priority is in this order:
- if .observations is set, loads time-value pairs from there,
- else if .csv_file is set, loads data from said csv file,
- else loads from input api the series of id .series_id and of type .type

**Arguments**:

  -----------
  timestart : timedelta
  Begin time of the timeseries
  
  timeend : timedelta
  End time of the timeseries

<a id="pydrodelta.node_serie.NodeSerie.getThresholds"></a>

#### getThresholds

```python
def getThresholds() -> dict
```

Read level threshold information from .metadata

<a id="pydrodelta.node_serie.NodeSerie.removeOutliers"></a>

#### removeOutliers

```python
def removeOutliers() -> bool
```

If .lim_outliers is set, removes outilers and returns True if any outliers were removed. Removed data rows are saved into .outliers_data

<a id="pydrodelta.node_serie.NodeSerie.detectJumps"></a>

#### detectJumps

```python
def detectJumps() -> bool
```

If lim_jump is set, detects jumps. Returns True if any jumps were found. Data rows containing jumps are saved into .jumps_data

<a id="pydrodelta.node_serie.NodeSerie.applyMovingAverage"></a>

#### applyMovingAverage

```python
def applyMovingAverage() -> None
```

If .moving_average is set, apply a moving average with a time window size equal to .moving_average to the values of the series

<a id="pydrodelta.node_serie.NodeSerie.applyOffset"></a>

#### applyOffset

```python
def applyOffset() -> None
```

Applies .x_offset (time axis) and .y_offset (values axis) to the data

<a id="pydrodelta.node_serie.NodeSerie.regularize"></a>

#### regularize

```python
def regularize(timestart: datetime,
               timeend: datetime,
               time_interval: timedelta,
               time_offset: timedelta,
               interpolation_limit: timedelta,
               inline: bool = True,
               interpolate: bool = False) -> Union[None, DataFrame]
```

Regularize the time step of the timeseries

**Arguments**:

  -----------
  timestart : datetime
  Begin time of the output regular timeseries
  
  timeend : datetime
  End time of the output regular timeseries
  
  time_interval : timedelta
  time step of the output regular timeseries
  
  time_offset : timedelta
  Start time of the day of the output regular timeseries (overrides that of timestart)
  
  interpolation_limit : timedelta
  Maximum number of time steps to interpolate (default: 1)
  
  inline : bool = True
  If True, saves output regular timeseries to .data. Else, returns output regular timeseries
  
  interpolate : bool = False
  If True, interpolate missing values

<a id="pydrodelta.node_serie.NodeSerie.fillNulls"></a>

#### fillNulls

```python
def fillNulls(other_data: DataFrame,
              fill_value: float = None,
              x_offset: int = 0,
              y_offset: float = 0,
              inline: bool = False) -> Union[None, DataFrame]
```

Fills missing values of .data from other_data, optionally applying x_offset and y_offset. If for a missing value in .data, other_data is also missing, fill_value is set.

**Arguments**:

  -----------
  other_data : DataFrame
  Timeseries data to be used to fill missing values in .data. Index must be the localized time and a column 'valor' must contain the values
  
  fill_value : float = None
  If for a missing value in .data, other_data is also missing, set this value.
  
  x_offset : int = 0
  Shift other_data this number of rows
  
  y_offset : float = 0
  Apply this offset to other_data values
  
  inline : bool = False
  If True, save null-filled timeseries into .data. Else return null-filled timeseries

<a id="pydrodelta.node_serie.NodeSerie.toCSV"></a>

#### toCSV

```python
def toCSV(include_series_id: bool = False) -> str
```

Convert timeseries into csv string

**Arguments**:

  -----------
  include_series_id : bool = False
  Add a column with series_id

<a id="pydrodelta.node_serie.NodeSerie.toList"></a>

#### toList

```python
def toList(include_series_id: bool = False,
           timeSupport: timedelta = None,
           remove_nulls: bool = False,
           max_obs_date: datetime = None) -> List[TVP]
```

Convert timeseries to list of time-value pair dicts

**Arguments**:

  -----------
  include_series_id : bool = False
  Add series_id to TVP dicts
  
  timeSupport : timedelta = None
  Time support of the timeseries (i.e., None for instantaneous observations, 1 day for daily mean)
  
  remove_nulls : bool = False
  Remove null values
  
  max_obs_date : datetime = None
  Remove data beyond this date
  

**Returns**:

  --------
  list of time-value pair dicts : List[TVP]

<a id="pydrodelta.node_serie.NodeSerie.toDict"></a>

#### toDict

```python
def toDict(
        timeSupport: timedelta = None,
        as_prono: bool = False,
        remove_nulls: bool = False,
        max_obs_date: datetime = None) -> Union[SeriesDict, SeriesPronoDict]
```

Convert timeseries to series dict

**Arguments**:

  -----------
  timeSupport : timedelta = None
  Time support of the timeseries (i.e., None for instantaneous observations, 1 day for daily mean)
  as_prono : bool = False
  Return SeriesPronoDict instead of SeriesDict
  
  remove_nulls : bool = False
  Remove null values
  
  max_obs_date : datetime = None
  Remove data beyond this date
  

**Returns**:

  --------
  Dict containing
  - series_id: int
  - tipo: str
  - observaciones (or pronosticos, if as_prono=True): list of dict

<a id="pydrodelta.node_serie.NodeSerie.getSeriesTable"></a>

#### getSeriesTable

```python
def getSeriesTable() -> str
```

Retrieve series table name (of a5 schema) for this timeseries

