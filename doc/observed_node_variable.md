# Table of Contents

* [pydrodelta.observed\_node\_variable](#pydrodelta.observed_node_variable)
  * [ObservedNodeVariable](#pydrodelta.observed_node_variable.ObservedNodeVariable)
    * [series](#pydrodelta.observed_node_variable.ObservedNodeVariable.series)
    * [series\_prono](#pydrodelta.observed_node_variable.ObservedNodeVariable.series_prono)
    * [\_\_init\_\_](#pydrodelta.observed_node_variable.ObservedNodeVariable.__init__)
    * [loadData](#pydrodelta.observed_node_variable.ObservedNodeVariable.loadData)
    * [setDataWithNoValues](#pydrodelta.observed_node_variable.ObservedNodeVariable.setDataWithNoValues)
    * [removeOutliers](#pydrodelta.observed_node_variable.ObservedNodeVariable.removeOutliers)
    * [detectJumps](#pydrodelta.observed_node_variable.ObservedNodeVariable.detectJumps)
    * [applyOffset](#pydrodelta.observed_node_variable.ObservedNodeVariable.applyOffset)
    * [regularize](#pydrodelta.observed_node_variable.ObservedNodeVariable.regularize)
    * [fillNulls](#pydrodelta.observed_node_variable.ObservedNodeVariable.fillNulls)

<a id="pydrodelta.observed_node_variable"></a>

# pydrodelta.observed\_node\_variable

<a id="pydrodelta.observed_node_variable.ObservedNodeVariable"></a>

## ObservedNodeVariable Objects

```python
class ObservedNodeVariable(NodeVariable)
```

This class represents a variable observed at a node

<a id="pydrodelta.observed_node_variable.ObservedNodeVariable.series"></a>

#### series

```python
@property
def series() -> List[NodeSerie]
```

Series of observed data of this variable at this node. They may represent different data sources such as different instruments at the same station or different stations at (or near) the same site

<a id="pydrodelta.observed_node_variable.ObservedNodeVariable.series_prono"></a>

#### series\_prono

```python
@property
def series_prono() -> List[NodeSerieProno]
```

Series of forecasted data of this variable at this node. They may represent different data sources such as different model outputs

<a id="pydrodelta.observed_node_variable.ObservedNodeVariable.__init__"></a>

#### \_\_init\_\_

```python
def __init__(series: List[Union[dict, NodeSerie]] = None,
             series_prono: List[Union[dict, NodeSerieProno]] = None,
             **kwargs)
```

**Arguments**:

  -----------
  series : List[Union[dict,NodeSerie]]
  Series of observed data of this variable at this node. They may represent different data sources such as different instruments at the same station or different stations at (or near) the same site
  
  series_prono : List[Union[dict,NodeSerieProno]]
  Series of forecasted data of this variable at this node. They may represent different data sources such as different model outputs
  
  \**kwargs:
  Keyword arguments inherited from the parent class (see NodeVariable :func:`~pydrodelta.NodeVariable.__init__`)

<a id="pydrodelta.observed_node_variable.ObservedNodeVariable.loadData"></a>

#### loadData

```python
def loadData(timestart: datetime,
             timeend: datetime,
             include_prono: bool = True,
             forecast_timeend: datetime = None) -> None
```

Load data of each serie in .series from source

**Arguments**:

  -----------
  timestart : datetime
  Begin date of data
  
  timeend : datetime
  End date of data
  
  include_prono : bool = True
  Also load forecasted data for each serie in .series_prono
  
  forecast_timeend : datetime = None
  End date of forecasted data

<a id="pydrodelta.observed_node_variable.ObservedNodeVariable.setDataWithNoValues"></a>

#### setDataWithNoValues

```python
def setDataWithNoValues() -> None
```

Sets .data with null values and tags

<a id="pydrodelta.observed_node_variable.ObservedNodeVariable.removeOutliers"></a>

#### removeOutliers

```python
def removeOutliers() -> bool
```

For each serie in .series, remove outliers. Only series where lim_outliers is set are checked.

**Returns**:

  --------
  True if at least one outlier was found : bool

<a id="pydrodelta.observed_node_variable.ObservedNodeVariable.detectJumps"></a>

#### detectJumps

```python
def detectJumps() -> bool
```

For each serie in .series, detect jumps. Only series where lim_jump is set are checked

**Returns**:

  --------
  True if at least one jump was found : bool

<a id="pydrodelta.observed_node_variable.ObservedNodeVariable.applyOffset"></a>

#### applyOffset

```python
def applyOffset() -> None
```

For each serie in .series, apply offset where .x_offset and/or .y_offset is set

<a id="pydrodelta.observed_node_variable.ObservedNodeVariable.regularize"></a>

#### regularize

```python
def regularize(interpolate: bool = False) -> None
```

For each serie in .series, apply timestep regularization using parameters stored in ._node (timestart, timeend, time_interval, time_offset)

**Arguments**:

  -----------
  interpolate : bool = False
  Interpolate missing values up to a limit of self.interpolation_limit. If false, values will be assigned to closest regular step up to a distance of self.interpolation_limit

<a id="pydrodelta.observed_node_variable.ObservedNodeVariable.fillNulls"></a>

#### fillNulls

```python
def fillNulls(inline: bool = True,
              fill_value: bool = None) -> Union[DataFrame, None]
```

Copies data of first series and fills its null values with the other series
In the end it fills nulls with fill_value. If None, uses self.fill_value
If inline=True, saves result in self.data

**Arguments**:

  -----------
  inline : bool = True
  If True, save result into each series .data. Else, return null-filled DataFrame
  
  fill_value : bool = None
  Value to fill up with
  

**Returns**:

  --------
  DataFrame or None : Union[DataFrame,None]

