# Table of Contents

* [pydrodelta.types.interpolated\_origin\_dict](#pydrodelta.types.interpolated_origin_dict)
  * [InterpolatedOriginDict](#pydrodelta.types.interpolated_origin_dict.InterpolatedOriginDict)

<a id="pydrodelta.types.interpolated_origin_dict"></a>

# pydrodelta.types.interpolated\_origin\_dict

<a id="pydrodelta.types.interpolated_origin_dict.InterpolatedOriginDict"></a>

## InterpolatedOriginDict Objects

```python
class InterpolatedOriginDict(TypedDict)
```

**Arguments**:

  -----------
  node_id_1 : int
  
  node_id_2 : int
  
  var_id_1 : int
  
  var_id_2 : int
  
  x_offset : Union[dict,datetime,float] = None
  
  y_offset : float = None
  
  interpolation_coefficient : float = 0.5

