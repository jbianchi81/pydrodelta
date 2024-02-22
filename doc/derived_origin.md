# Table of Contents

* [pydrodelta.derived\_origin](#pydrodelta.derived_origin)
  * [DerivedOrigin](#pydrodelta.derived_origin.DerivedOrigin)
    * [node\_id](#pydrodelta.derived_origin.DerivedOrigin.node_id)
    * [var\_id](#pydrodelta.derived_origin.DerivedOrigin.var_id)
    * [x\_offset](#pydrodelta.derived_origin.DerivedOrigin.x_offset)
    * [y\_offset](#pydrodelta.derived_origin.DerivedOrigin.y_offset)
    * [origin](#pydrodelta.derived_origin.DerivedOrigin.origin)
    * [\_\_init\_\_](#pydrodelta.derived_origin.DerivedOrigin.__init__)

<a id="pydrodelta.derived_origin"></a>

# pydrodelta.derived\_origin

<a id="pydrodelta.derived_origin.DerivedOrigin"></a>

## DerivedOrigin Objects

```python
class DerivedOrigin()
```

Represents the origin node+variable of a derived node+variable

<a id="pydrodelta.derived_origin.DerivedOrigin.node_id"></a>

#### node\_id

Node identifier of the origin

<a id="pydrodelta.derived_origin.DerivedOrigin.var_id"></a>

#### var\_id

Variable identifier of the origin

<a id="pydrodelta.derived_origin.DerivedOrigin.x_offset"></a>

#### x\_offset

```python
@property
def x_offset() -> Union[timedelta, int]
```

Offset of the time index

<a id="pydrodelta.derived_origin.DerivedOrigin.y_offset"></a>

#### y\_offset

Offset of the values

<a id="pydrodelta.derived_origin.DerivedOrigin.origin"></a>

#### origin

```python
@property
def origin() -> NodeVariable
```

Origin NodeVariable

<a id="pydrodelta.derived_origin.DerivedOrigin.__init__"></a>

#### \_\_init\_\_

```python
def __init__(node_id: int,
             var_id: int,
             x_offset: Union[dict, int] = None,
             y_offset: float = None,
             topology=None)
```

**Arguments**:

  -----------
  node_id : int
  
  Node identifier of the origin
  
  var_id : int
  
  Variable identifier of the origin
  
  x_offset : Union[dict,int] = None
  
  Offset of the time index
  
  y_offset : float = None
  
  Offset of the values
  
  topology = None

