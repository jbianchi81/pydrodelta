# Table of Contents

* [pydrodelta.util](#pydrodelta.util)
  * [interval2timedelta](#pydrodelta.util.interval2timedelta)
  * [tryParseAndLocalizeDate](#pydrodelta.util.tryParseAndLocalizeDate)
  * [serieRegular](#pydrodelta.util.serieRegular)
  * [serieFillNulls](#pydrodelta.util.serieFillNulls)
  * [removeOutliers](#pydrodelta.util.removeOutliers)
  * [detectJumps](#pydrodelta.util.detectJumps)
  * [adjustSeries](#pydrodelta.util.adjustSeries)
  * [linearCombination](#pydrodelta.util.linearCombination)
  * [readDataFromCsvFile](#pydrodelta.util.readDataFromCsvFile)
  * [groupByCalibrationPeriod](#pydrodelta.util.groupByCalibrationPeriod)

<a id="pydrodelta.util"></a>

# pydrodelta.util

<a id="pydrodelta.util.interval2timedelta"></a>

#### interval2timedelta

```python
def interval2timedelta(interval: Union[dict, float, timedelta])
```

Parses duration dict or number of days into datetime.timedelta object

**Arguments**:

  -----------
  interval : dict or float (decimal number of days) or datetime.timedelta
  If dict, allowed keys are:
  - days
  - seconds
  - microseconds
  - minutes
  - hours
  - weeks
  

**Returns**:

  --------
  duration : datetime.timedelta
  

**Examples**:

  
```
interval2timedelta({"hours":1, "minutes": 30})
interval2timedelta(1.5/24)
```

<a id="pydrodelta.util.tryParseAndLocalizeDate"></a>

#### tryParseAndLocalizeDate

```python
def tryParseAndLocalizeDate(
        date_string: Union[str, float, datetime],
        timezone: str = 'America/Argentina/Buenos_Aires') -> datetime
```

Datetime parser. If duration is provided, computes date relative to now.

**Arguments**:

  -----------
  date_string : str or float or datetime.datetime
  For absolute date: ISO-8601 datetime string or datetime.datetime.
  For relative date: dict (duration key-values) or float (decimal number of days)
  
  timezone : str
  Time zone string identifier. Default: America/Argentina/Buenos_Aires
  

**Returns**:

  --------
  datetime.datetime
  

**Examples**:

  ---------
``` 
tryParseAndLocalizeDate("2024-01-01T03:00:00.000Z")
tryParseAndLocalizeDate(1.5)
tryParseAndLocalizeDate({"days":1, "hours": 12}, timezone = "Africa/Casablanca")
```

<a id="pydrodelta.util.serieRegular"></a>

#### serieRegular

```python
def serieRegular(data: pandas.DataFrame,
                 time_interval: timedelta,
                 timestart=None,
                 timeend=None,
                 time_offset=None,
                 column="valor",
                 interpolate=True,
                 interpolation_limit=1,
                 tag_column=None,
                 extrapolate=False) -> pandas.DataFrame
```

genera serie regular y rellena nulos interpolando
if interpolate=False, interpolates only to the closest timestep of the regular timeseries. If observation is equidistant to preceding and following timesteps it interpolates to both.

<a id="pydrodelta.util.serieFillNulls"></a>

#### serieFillNulls

```python
def serieFillNulls(data: pandas.DataFrame,
                   other_data: pandas.DataFrame,
                   column: str = "valor",
                   other_column: str = "valor",
                   fill_value: float = None,
                   shift_by: int = 0,
                   bias: float = 0,
                   extend=False,
                   tag_column=None)
```

rellena nulos de data con valores de other_data donde coincide el index. Opcionalmente aplica traslado rígido en x (shift_by: n registros) y en y (bias: float)

si extend=True el índice del dataframe resultante será la unión de los índices de data y other_data (caso contrario será igual al índice de data)

<a id="pydrodelta.util.removeOutliers"></a>

#### removeOutliers

```python
def removeOutliers(data: pandas.DataFrame, limite_outliers, column="valor")
```

remove outliers inline and return outliers data frame

<a id="pydrodelta.util.detectJumps"></a>

#### detectJumps

```python
def detectJumps(data: pandas.DataFrame, lim_jump, column="valor")
```

returns jump rows as data frame

<a id="pydrodelta.util.adjustSeries"></a>

#### adjustSeries

```python
def adjustSeries(
    sim_df: pandas.DataFrame,
    truth_df: pandas.DataFrame,
    method: str = "lfit",
    plot: bool = True,
    return_adjusted_series: bool = True,
    tag_column: str = None,
    title: str = None,
    warmup: int = None,
    tail: int = None,
    sim_range: Tuple[float, float] = None
) -> Union[dict, Tuple[pandas.Series, pandas.Series, dict]]
```

Adjust sim_df with truth_df by means of a linear regression

**Arguments**:

- `sim_df` _pandas.DataFrame_ - data to adjust
- `truth_df` _pandas.DataFrame_ - truth data to adjust sim_df with
- `method` _str, optional_ - Regression method. Defaults to "lfit".
- `plot` _bool, optional_ - Plot data. Defaults to True.
- `return_adjusted_series` _bool, optional_ - If True, return tuple of (adjusted values (pandas.Series), adjusted series tag (pandas.Series), fit result stats (dict)). Else return only fit result stats (dict) . Defaults to True.
- `tag_column` _str, optional_ - Name of the tag column. Defaults to None.
- `title` _str, optional_ - Title of the plot. Defaults to None.
- `warmup` _int, optional_ - Number of initial rows to skip for the fit procedure. Defaults to None.
- `tail` _int, optional_ - Number of final steps to use for the fit procedure (discard the rest).
- `sim_range` _Tuple[float,float],optional_ - Select data pairs where sim is within this range.
  

**Raises**:

- `ValueError` - unknown method
  

**Returns**:

  Union[dict,Tuple[pandas.Series, pandas.Series, dict]]: If return_adjusted_seris is True, it returns a tuple of (adjusted values (pandas.Series), adjusted series tag (pandas.Series), fit result stats (dict)). Else it returns only fit result stats (dict)

<a id="pydrodelta.util.linearCombination"></a>

#### linearCombination

```python
def linearCombination(sim_df: pandas.DataFrame,
                      params: dict,
                      plot=True,
                      tag_column=None) -> pandas.Series
```

sim_df: DataFrame con las covariables
params: { intercept: float, coefficients: [float,...]
plot: Boolean

<a id="pydrodelta.util.readDataFromCsvFile"></a>

#### readDataFromCsvFile

```python
def readDataFromCsvFile(csv_file: str,
                        series_id: int,
                        timestart=None,
                        timeend=None) -> list
```

reads from csv_file and returns list of observaciones (dicts). series_id must be in the header of the column containing the values of the corresponding series. timestart column must be in iso format. Other columns are ignored

<a id="pydrodelta.util.groupByCalibrationPeriod"></a>

#### groupByCalibrationPeriod

```python
def groupByCalibrationPeriod(
    data: pandas.DataFrame, calibration_period: Tuple[datetime, datetime]
) -> Tuple[pandas.DataFrame, pandas.DataFrame]
```

Split data between calibration and validation periods

**Arguments**:

  data : pandas.DataFrame
  Series DataFrame to split
  calibration_period : Tuple[datetime, datetime]
  Begin and end dates of calibration period
  

**Returns**:

  Tuple[pandas.DataFrame, pandas.DataFrame] : calibration data (or None if data not  found), validation data (or None if data not  found).

