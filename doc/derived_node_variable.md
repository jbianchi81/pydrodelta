# Table of Contents

* [pydrodelta.derived\_node\_variable](#pydrodelta.derived_node_variable)
  * [DerivedNodeVariable](#pydrodelta.derived_node_variable.DerivedNodeVariable)
    * [derived\_from](#pydrodelta.derived_node_variable.DerivedNodeVariable.derived_from)
    * [interpolated\_from](#pydrodelta.derived_node_variable.DerivedNodeVariable.interpolated_from)
    * [series](#pydrodelta.derived_node_variable.DerivedNodeVariable.series)
    * [series\_prono](#pydrodelta.derived_node_variable.DerivedNodeVariable.series_prono)
    * [\_\_init\_\_](#pydrodelta.derived_node_variable.DerivedNodeVariable.__init__)
    * [derive](#pydrodelta.derived_node_variable.DerivedNodeVariable.derive)

<a id="pydrodelta.derived_node_variable"></a>

# pydrodelta.derived\_node\_variable

<a id="pydrodelta.derived_node_variable.DerivedNodeVariable"></a>

## DerivedNodeVariable Objects

```python
class DerivedNodeVariable(NodeVariable)
```

This class represents a variable at a node where it is not observed, but values are derived from observations of the same variable at a nearby node or from observations of another variable at the same  (or nearby) node

<a id="pydrodelta.derived_node_variable.DerivedNodeVariable.derived_from"></a>

#### derived\_from

Derivation configuration

<a id="pydrodelta.derived_node_variable.DerivedNodeVariable.interpolated_from"></a>

#### interpolated\_from

Interpolation configuration

<a id="pydrodelta.derived_node_variable.DerivedNodeVariable.series"></a>

#### series

```python
@property
def series() -> List[DerivedNodeSerie]
```

Series of derived data of this variable at this node.

<a id="pydrodelta.derived_node_variable.DerivedNodeVariable.series_prono"></a>

#### series\_prono

```python
@property
def series_prono() -> List[NodeSerieProno]
```

Series of forecasted data of this variable at this node. They may represent different data sources such as different model outputs

<a id="pydrodelta.derived_node_variable.DerivedNodeVariable.__init__"></a>

#### \_\_init\_\_

```python
def __init__(derived_from: DerivedOriginDict = None,
             interpolated_from: InterpolatedOriginDict = None,
             series: List[Union[dict, NodeSerie]] = None,
             series_prono: List[Union[dict, NodeSerieProno]] = None,
             derived: bool = True,
             **kwargs)
```

derived_from : DerivedOriginDict = None

    Derivation configuration

interpolated_from : InterpolatedOriginDict = None

    Interpolation configuration

series : List[Union[dict,NodeSerie]] = None

    Additional timeseries

series_prono : List[Union[dict,NodeSerieProno]] = None

    Forecast timeseries

**kwargs

    Keyword arguments. See NodeVariable (:class:`~pydrodelta.NodeVariable`)

<a id="pydrodelta.derived_node_variable.DerivedNodeVariable.derive"></a>

#### derive

```python
def derive() -> None
```

Derive observations of .series[0] from associated node-variables

