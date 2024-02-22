# Table of Contents

* [pydrodelta.derived\_node\_serie](#pydrodelta.derived_node_serie)
  * [DerivedNodeSerie](#pydrodelta.derived_node_serie.DerivedNodeSerie)
    * [derived\_from](#pydrodelta.derived_node_serie.DerivedNodeSerie.derived_from)
    * [interpolated\_from](#pydrodelta.derived_node_serie.DerivedNodeSerie.interpolated_from)
    * [data](#pydrodelta.derived_node_serie.DerivedNodeSerie.data)
    * [\_\_init\_\_](#pydrodelta.derived_node_serie.DerivedNodeSerie.__init__)
    * [deriveTag](#pydrodelta.derived_node_serie.DerivedNodeSerie.deriveTag)
    * [deriveOffsetIndex](#pydrodelta.derived_node_serie.DerivedNodeSerie.deriveOffsetIndex)
    * [derive](#pydrodelta.derived_node_serie.DerivedNodeSerie.derive)
    * [toCSV](#pydrodelta.derived_node_serie.DerivedNodeSerie.toCSV)
    * [toList](#pydrodelta.derived_node_serie.DerivedNodeSerie.toList)

<a id="pydrodelta.derived_node_serie"></a>

# pydrodelta.derived\_node\_serie

<a id="pydrodelta.derived_node_serie.DerivedNodeSerie"></a>

## DerivedNodeSerie Objects

```python
class DerivedNodeSerie()
```

Represents a timeseries of a variable at a node derived or interpolated from another timeseries, i.e. of the same variable at a nearby node or another variable at the same (or nearby) node

<a id="pydrodelta.derived_node_serie.DerivedNodeSerie.derived_from"></a>

#### derived\_from

```python
@property
def derived_from() -> DerivedOrigin
```

Derivation configuration

<a id="pydrodelta.derived_node_serie.DerivedNodeSerie.interpolated_from"></a>

#### interpolated\_from

```python
@property
def interpolated_from() -> InterpolatedOrigin
```

Interpolation configuration

<a id="pydrodelta.derived_node_serie.DerivedNodeSerie.data"></a>

#### data

DataFrame containing the timestamped values. Index is the time (with time zone), column 'valor' contains the values (floats) and column 'tag' contains the tag indicating the origin of the value (one of: observed, simulated, interpolated, moving_average, extrapolated, derived)

<a id="pydrodelta.derived_node_serie.DerivedNodeSerie.__init__"></a>

#### \_\_init\_\_

```python
def __init__(topology,
             series_id: int = None,
             derived_from: Union[DerivedOrigin, DerivedOriginDict] = None,
             interpolated_from: Union[InterpolatedOrigin,
                                      InterpolatedOriginDict] = None)
```

**Arguments**:

  -----------
  topology : Topology
  
  Topology that contains the node_variable that contains this series and the node_variable pointed out by derived_from/interpolated_from
  
  series_id : int
  
  Series identifier
  
  derived_from : DerivedOriginDict = None
  
  Derivation configuration
  
  interpolated_from : InterpolatedOriginDict = None

<a id="pydrodelta.derived_node_serie.DerivedNodeSerie.deriveTag"></a>

#### deriveTag

```python
def deriveTag(row: Series, tag_column: str, tag: str = "derived") -> str
```

Generate tag for derived row

<a id="pydrodelta.derived_node_serie.DerivedNodeSerie.deriveOffsetIndex"></a>

#### deriveOffsetIndex

```python
def deriveOffsetIndex(row: Series, x_offset: int) -> Union[int, timedelta]
```

Apply offset to index of row

<a id="pydrodelta.derived_node_serie.DerivedNodeSerie.derive"></a>

#### derive

```python
def derive(keep_index: bool = True) -> None
```

Derive this series from .derived_origin

**Arguments**:

  -----------
  keep_index : bool = True
  
  Don't overwrite index (apply offset in-place)

<a id="pydrodelta.derived_node_serie.DerivedNodeSerie.toCSV"></a>

#### toCSV

```python
def toCSV(include_series_id: bool = False) -> str
```

Convert series to csv string

**Arguments**:

  -----------
  include_series_id : bool = False
  
  Add series_id column
  

**Returns**:

  --------
  csv string : str

<a id="pydrodelta.derived_node_serie.DerivedNodeSerie.toList"></a>

#### toList

```python
def toList(include_series_id: bool = False,
           timeSupport: timedelta = None) -> List[TVP]
```

Convert series to list of time-value pair dicts

**Arguments**:

  -----------
  include_series_id : bool = False
  
  Add series_id property
  
  timeSupport : timedelta = None
  
  Time support of the timeseries (i.e., None for instantaneous observations, 1 day for daily mean)
  

**Returns**:

  --------
  List of time-value pair dicts : List[TVP]

