# Table of Contents

* [pydrodelta.node\_serie\_prono](#pydrodelta.node_serie_prono)
  * [NodeSerieProno](#pydrodelta.node_serie_prono.NodeSerieProno)
    * [metadata](#pydrodelta.node_serie_prono.NodeSerieProno.metadata)
    * [main\_qualifier](#pydrodelta.node_serie_prono.NodeSerieProno.main_qualifier)
    * [previous\_runs\_timestart](#pydrodelta.node_serie_prono.NodeSerieProno.previous_runs_timestart)
    * [forecast\_timestart](#pydrodelta.node_serie_prono.NodeSerieProno.forecast_timestart)
    * [loadData](#pydrodelta.node_serie_prono.NodeSerieProno.loadData)

<a id="pydrodelta.node_serie_prono"></a>

# pydrodelta.node\_serie\_prono

<a id="pydrodelta.node_serie_prono.NodeSerieProno"></a>

## NodeSerieProno Objects

```python
class NodeSerieProno(NodeSerie)
```

Forecasted timeseries

<a id="pydrodelta.node_serie_prono.NodeSerieProno.metadata"></a>

#### metadata

```python
@property
def metadata() -> dict
```

series metadata

<a id="pydrodelta.node_serie_prono.NodeSerieProno.main_qualifier"></a>

#### main\_qualifier

If qualifier == 'all', select this qualifier as the main qualifier

<a id="pydrodelta.node_serie_prono.NodeSerieProno.previous_runs_timestart"></a>

#### previous\_runs\_timestart

If set, retrieves previous forecast runs with forecast_date posterior to the chosen date and concatenates the results into a single series

<a id="pydrodelta.node_serie_prono.NodeSerieProno.forecast_timestart"></a>

#### forecast\_timestart

Begin date of last forecast run. If last forecast date is older than this value, it raises an error

<a id="pydrodelta.node_serie_prono.NodeSerieProno.loadData"></a>

#### loadData

```python
def loadData(timestart: datetime,
             timeend: datetime,
             input_api_config: dict = None,
             tag: str = "sim",
             previous_runs_timestart: datetime = None,
             forecast_timestart: datetime = None) -> None
```

Load forecasted data from source (input api). Retrieves forecast from input api using series_id, cal_id, timestart, and timeend

**Arguments**:

  -----------
  timestart : datetime
  Begin time of forecast
  
  timeend : datetime
  End time of forecast
  
  input_api_config : dict
  Api connection parameters. Overrides global config.input_api
  
  Properties:
  - url : str
  - token : str
  - proxy_dict : dict
  
  tag : str = "sim"
  Tag forecast records with this string
  
  previous_runs_timestart = DatetimeDescriptor()
  If set, retrieves previous forecast runs with forecast_date posterior to the chosen date and concatenates the results into a single series
  
  forecast_timestart : datetime = None
  Forecast date must be greater or equal to this value

