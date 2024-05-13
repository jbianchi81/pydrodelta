# Table of Contents

* [pydrodelta.types.derived\_node\_variable\_dict](#pydrodelta.types.derived_node_variable_dict)
  * [DerivedNodeVariableDict](#pydrodelta.types.derived_node_variable_dict.DerivedNodeVariableDict)

<a id="pydrodelta.types.derived_node_variable_dict"></a>

# pydrodelta.types.derived\_node\_variable\_dict

<a id="pydrodelta.types.derived_node_variable_dict.DerivedNodeVariableDict"></a>

## DerivedNodeVariableDict Objects

```python
class DerivedNodeVariableDict(NodeVariableDict)
```

series : List[Union[SeriesDict,NodeSerie]]
series_prono : List[Union[SeriesPronoDict,NodeSerieProno]]
derived_from : DerivedOriginDict
interpolated_from : InterpolatedOriginDict
derived : bool

