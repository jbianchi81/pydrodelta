# Table of Contents

* [pydrodelta.types.node\_variable\_dict](#pydrodelta.types.node_variable_dict)
  * [NodeVariableDict](#pydrodelta.types.node_variable_dict.NodeVariableDict)

<a id="pydrodelta.types.node_variable_dict"></a>

# pydrodelta.types.node\_variable\_dict

<a id="pydrodelta.types.node_variable_dict.NodeVariableDict"></a>

## NodeVariableDict Objects

```python
class NodeVariableDict(TypedDict)
```

id : int,
node = None,
fill_value : float = None,
series_output : List[Union[NodeSerie,SeriesDict]] = None,
output_series_id : int = None,
series_sim : List[Union[NodeSerie,SeriesDict]] = None,
time_support : Union[datetime,dict,int,str] = None,
adjust_from : AdjustFromDict = None,
linear_combination : LinearCombinationDict = None,
interpolation_limit : int = None,
extrapolate : bool = None,
time_interval : Union[timedelta,dict,float] = None,
name : str = None,
timestart : datetime = None,
timeend : datetime = None,
time_offset : timedelta = None,
forecast_timeend : datetime = None

