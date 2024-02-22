# Table of Contents

* [pydrodelta.node\_serie\_prono\_metadata](#pydrodelta.node_serie_prono_metadata)
  * [NodeSeriePronoMetadata](#pydrodelta.node_serie_prono_metadata.NodeSeriePronoMetadata)
    * [series\_id](#pydrodelta.node_serie_prono_metadata.NodeSeriePronoMetadata.series_id)
    * [cal\_id](#pydrodelta.node_serie_prono_metadata.NodeSeriePronoMetadata.cal_id)
    * [cor\_id](#pydrodelta.node_serie_prono_metadata.NodeSeriePronoMetadata.cor_id)
    * [forecast\_date](#pydrodelta.node_serie_prono_metadata.NodeSeriePronoMetadata.forecast_date)
    * [qualifier](#pydrodelta.node_serie_prono_metadata.NodeSeriePronoMetadata.qualifier)
    * [\_\_init\_\_](#pydrodelta.node_serie_prono_metadata.NodeSeriePronoMetadata.__init__)
    * [to\_dict](#pydrodelta.node_serie_prono_metadata.NodeSeriePronoMetadata.to_dict)

<a id="pydrodelta.node_serie_prono_metadata"></a>

# pydrodelta.node\_serie\_prono\_metadata

<a id="pydrodelta.node_serie_prono_metadata.NodeSeriePronoMetadata"></a>

## NodeSeriePronoMetadata Objects

```python
class NodeSeriePronoMetadata()
```

Forecasted series metadata

<a id="pydrodelta.node_serie_prono_metadata.NodeSeriePronoMetadata.series_id"></a>

#### series\_id

Series identifier

<a id="pydrodelta.node_serie_prono_metadata.NodeSeriePronoMetadata.cal_id"></a>

#### cal\_id

Procedure configuration identifier

<a id="pydrodelta.node_serie_prono_metadata.NodeSeriePronoMetadata.cor_id"></a>

#### cor\_id

Procedure run identifier

<a id="pydrodelta.node_serie_prono_metadata.NodeSeriePronoMetadata.forecast_date"></a>

#### forecast\_date

Procedure execution date

<a id="pydrodelta.node_serie_prono_metadata.NodeSeriePronoMetadata.qualifier"></a>

#### qualifier

Forecast qualifier

<a id="pydrodelta.node_serie_prono_metadata.NodeSeriePronoMetadata.__init__"></a>

#### \_\_init\_\_

```python
def __init__(series_id: int = None,
             cal_id: int = None,
             cor_id: int = None,
             forecast_date: str = None,
             qualifier: str = None)
```

series_id : int = None

    Series identifier

cal_id : int = None

    Procedure configuration identifier

cor_id : int = None

    Procedure run identifier

forecast_date : str = None

    Procedure execution date

qualifier : str = None

    Forecast qualifier

<a id="pydrodelta.node_serie_prono_metadata.NodeSeriePronoMetadata.to_dict"></a>

#### to\_dict

```python
def to_dict() -> dict
```

Convert to dict

