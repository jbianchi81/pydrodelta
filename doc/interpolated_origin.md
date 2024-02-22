# Table of Contents

* [pydrodelta.interpolated\_origin](#pydrodelta.interpolated_origin)
  * [InterpolatedOrigin](#pydrodelta.interpolated_origin.InterpolatedOrigin)
    * [node\_id\_1](#pydrodelta.interpolated_origin.InterpolatedOrigin.node_id_1)
    * [node\_id\_2](#pydrodelta.interpolated_origin.InterpolatedOrigin.node_id_2)
    * [var\_id\_1](#pydrodelta.interpolated_origin.InterpolatedOrigin.var_id_1)
    * [var\_id\_2](#pydrodelta.interpolated_origin.InterpolatedOrigin.var_id_2)
    * [x\_offset](#pydrodelta.interpolated_origin.InterpolatedOrigin.x_offset)
    * [y\_offset](#pydrodelta.interpolated_origin.InterpolatedOrigin.y_offset)
    * [interpolation\_coefficient](#pydrodelta.interpolated_origin.InterpolatedOrigin.interpolation_coefficient)
    * [origin\_1](#pydrodelta.interpolated_origin.InterpolatedOrigin.origin_1)
    * [origin\_2](#pydrodelta.interpolated_origin.InterpolatedOrigin.origin_2)
    * [\_\_init\_\_](#pydrodelta.interpolated_origin.InterpolatedOrigin.__init__)
    * [setOrigin](#pydrodelta.interpolated_origin.InterpolatedOrigin.setOrigin)

<a id="pydrodelta.interpolated_origin"></a>

# pydrodelta.interpolated\_origin

<a id="pydrodelta.interpolated_origin.InterpolatedOrigin"></a>

## InterpolatedOrigin Objects

```python
class InterpolatedOrigin()
```

Represents the origin node+variable of an interpolated node+variable

<a id="pydrodelta.interpolated_origin.InterpolatedOrigin.node_id_1"></a>

#### node\_id\_1

First node identifier

<a id="pydrodelta.interpolated_origin.InterpolatedOrigin.node_id_2"></a>

#### node\_id\_2

Second node identifier

<a id="pydrodelta.interpolated_origin.InterpolatedOrigin.var_id_1"></a>

#### var\_id\_1

First variable identifier

<a id="pydrodelta.interpolated_origin.InterpolatedOrigin.var_id_2"></a>

#### var\_id\_2

Second variable identifier

<a id="pydrodelta.interpolated_origin.InterpolatedOrigin.x_offset"></a>

#### x\_offset

```python
@property
def x_offset() -> Union[timedelta, int]
```

Offset if the time axis

<a id="pydrodelta.interpolated_origin.InterpolatedOrigin.y_offset"></a>

#### y\_offset

Offset of the values

<a id="pydrodelta.interpolated_origin.InterpolatedOrigin.interpolation_coefficient"></a>

#### interpolation\_coefficient

Interpolation weighting coefficient [0-1] (i.e., if 1, first node-variable gets all the weight)

<a id="pydrodelta.interpolated_origin.InterpolatedOrigin.origin_1"></a>

#### origin\_1

```python
@property
def origin_1() -> NodeVariable
```

First node-variable origin for interpolation

<a id="pydrodelta.interpolated_origin.InterpolatedOrigin.origin_2"></a>

#### origin\_2

```python
@property
def origin_2() -> NodeVariable
```

Second node-variable origin for interpolation

<a id="pydrodelta.interpolated_origin.InterpolatedOrigin.__init__"></a>

#### \_\_init\_\_

```python
def __init__(node_id_1: int,
             node_id_2: int,
             var_id_1: int,
             var_id_2: int,
             x_offset: Union[datetime, dict, float] = {"hours": 0},
             y_offset: float = 0,
             interpolation_coefficient: float = None,
             topology=None)
```

node_id_1 : int

    First node identifier

node_id_2 : int

    Second node identifier

var_id_1 : int

    First variable identifier

var_id_2 : int

    Second variable identifier

x_offset : Union[datetime,dict,float] = {"hours":0}

    Offset if the time axis

y_offset : float = 0

    Offset of the values

interpolation_coefficient : float = None

    Interpolation weighting coefficient [0-1] (i.e., if 1, first node-variable gets all the weight)

topology = None

    Topology that contains the origin node-variables

<a id="pydrodelta.interpolated_origin.InterpolatedOrigin.setOrigin"></a>

#### setOrigin

```python
def setOrigin() -> None
```

Set origin node-variables according to the stored identifiers (.node_id_1, .node_id_2, .var_id_1, .var_id_2)

