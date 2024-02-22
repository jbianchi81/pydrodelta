# Table of Contents

* [pydrodelta.model\_state](#pydrodelta.model_state)
  * [ModelState](#pydrodelta.model_state.ModelState)
    * [name](#pydrodelta.model_state.ModelState.name)
    * [min](#pydrodelta.model_state.ModelState.min)
    * [max](#pydrodelta.model_state.ModelState.max)
    * [default](#pydrodelta.model_state.ModelState.default)
    * [\_\_init\_\_](#pydrodelta.model_state.ModelState.__init__)

<a id="pydrodelta.model_state"></a>

# pydrodelta.model\_state

<a id="pydrodelta.model_state.ModelState"></a>

## ModelState Objects

```python
class ModelState()
```

Represents a procedure function state described by a name, a constraint range (min, max) and a default value

<a id="pydrodelta.model_state.ModelState.name"></a>

#### name

The state name

<a id="pydrodelta.model_state.ModelState.min"></a>

#### min

The minimum allowed value. A lower value is either physically impossible and/or would make the procedure crash

<a id="pydrodelta.model_state.ModelState.max"></a>

#### max

The maximum allowed value. A higher value is either physically impossible or would make the procedure crash

<a id="pydrodelta.model_state.ModelState.default"></a>

#### default

The default value

<a id="pydrodelta.model_state.ModelState.__init__"></a>

#### \_\_init\_\_

```python
def __init__(name: str, constraints: tuple[float, float], default=None)
```

name : str

    The state name

constraints : tuple[float,float]

    tuple(min,max) where:
    - min: The minimum allowed value. A lower value is either physically impossible and/or would make the procedure crash
    - max: The maximum allowed value. A higher value is either physically impossible or would make the procedure crash

default = None

    The default value

