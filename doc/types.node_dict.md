# Table of Contents

* [pydrodelta.types.node\_dict](#pydrodelta.types.node_dict)
  * [NodeDict](#pydrodelta.types.node_dict.NodeDict)

<a id="pydrodelta.types.node_dict"></a>

# pydrodelta.types.node\_dict

<a id="pydrodelta.types.node_dict.NodeDict"></a>

## NodeDict Objects

```python
class NodeDict(TypedDict)
```

**Arguments**:

  -----------
  id : int,
  
  name : str,
  
  time_interval : Union[dict,int],
  
  tipo : str="puntual",
  
  timestart : datetime = None,
  
  timeend : datetime = None,
  
  forecast_timeend : datetime = None,
  
  plan = None,
  
  time_offset : timedelta = None,
  
  topology = None,
  
  hec_node : dict = None,
  
  variables : List[Union[DerivedNodeVariable,ObservedNodeVariable]] = list(),
  
  node_type : str = "station",
  
  description : str = None,
  
  basin_pars : dict = None,
  
  api_config : dict = None

