# Table of Contents

* [pydrodelta.node\_serie\_prono](#pydrodelta.node_serie_prono)
  * [NodeSerieProno](#pydrodelta.node_serie_prono.NodeSerieProno)
    * [loadData](#pydrodelta.node_serie_prono.NodeSerieProno.loadData)

<a id="pydrodelta.node_serie_prono"></a>

# pydrodelta.node\_serie\_prono

<a id="pydrodelta.node_serie_prono.NodeSerieProno"></a>

## NodeSerieProno Objects

```python
class NodeSerieProno(NodeSerie)
```

Forecasted timeseries

<a id="pydrodelta.node_serie_prono.NodeSerieProno.loadData"></a>

#### loadData

```python
def loadData(timestart: datetime, timeend: datetime) -> None
```

Load forecasted data from source (input api). Retrieves forecast from input api using series_id, cal_id, timestart, and timeend

**Arguments**:

  -----------
  timestart : datetime
  Begin time of forecast
  
  timeend : datetime
  End time of forecast

