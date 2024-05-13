# Table of Contents

* [pydrodelta.types.basin\_pars\_dict](#pydrodelta.types.basin_pars_dict)
  * [BasinParsDict](#pydrodelta.types.basin_pars_dict.BasinParsDict)

<a id="pydrodelta.types.basin_pars_dict"></a>

# pydrodelta.types.basin\_pars\_dict

<a id="pydrodelta.types.basin_pars_dict.BasinParsDict"></a>

## BasinParsDict Objects

```python
class BasinParsDict(TypedDict)
```

area : float
    basin area in square meters
rho  : float
    soil porosity (0-1)
ae: float
    effective area (0-1)
wp : float
    wilting point of soil (0-1)
area_id : int
    Basin identifier at a5 input API

