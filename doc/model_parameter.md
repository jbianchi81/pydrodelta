# Table of Contents

* [pydrodelta.model\_parameter](#pydrodelta.model_parameter)
  * [ModelParameter](#pydrodelta.model_parameter.ModelParameter)
    * [name](#pydrodelta.model_parameter.ModelParameter.name)
    * [min](#pydrodelta.model_parameter.ModelParameter.min)
    * [range\_min](#pydrodelta.model_parameter.ModelParameter.range_min)
    * [range\_max](#pydrodelta.model_parameter.ModelParameter.range_max)
    * [max](#pydrodelta.model_parameter.ModelParameter.max)
    * [\_\_init\_\_](#pydrodelta.model_parameter.ModelParameter.__init__)
    * [makeRandom](#pydrodelta.model_parameter.ModelParameter.makeRandom)

<a id="pydrodelta.model_parameter"></a>

# pydrodelta.model\_parameter

<a id="pydrodelta.model_parameter.ModelParameter"></a>

## ModelParameter Objects

```python
class ModelParameter()
```

Represents a procedure function parameter, described by a name and constraints.

Constraints:
- min: The minimum allowed value. A lower value is either physically impossible and/or would make the procedure crash
- range_min: The lower limit of the initial range of a random parameter set (for downhill simplex calibration)
- range_max: The upper limit of the initial range of a random parameter set (for downhill simplex calibration)
- max: The maximum allowed value. A higher value is either physically impossible or would make the procedure crash

<a id="pydrodelta.model_parameter.ModelParameter.name"></a>

#### name

The parameter name

<a id="pydrodelta.model_parameter.ModelParameter.min"></a>

#### min

The minimum allowed value. A lower value is either physically impossible and/or would make the procedure crash

<a id="pydrodelta.model_parameter.ModelParameter.range_min"></a>

#### range\_min

The lower limit of the initial range of a random parameter set (for downhill simplex calibration)

<a id="pydrodelta.model_parameter.ModelParameter.range_max"></a>

#### range\_max

The upper limit of the initial range of a random parameter set (for downhill simplex calibration)

<a id="pydrodelta.model_parameter.ModelParameter.max"></a>

#### max

The maximum allowed value. A higher value is either physically impossible or would make the procedure crash

<a id="pydrodelta.model_parameter.ModelParameter.__init__"></a>

#### \_\_init\_\_

```python
def __init__(name: str, constraints: tuple[float, float, float, float])
```

name : str

    The name of the parameter

constraints : tuple[float,float,float,float]

    tuple(min, range_min, range_max, max), where:
    - min: The minimum allowed value. A lower value is either physically impossible and/or would make the procedure crash
    - range_min: The lower limit of the initial range of a random parameter set (for downhill simplex calibration)
    - range_max: The upper limit of the initial range of a random parameter set (for downhill simplex calibration)
    - max: The maximum allowed value. A higher value is either physically impossible or would make the procedure crash

<a id="pydrodelta.model_parameter.ModelParameter.makeRandom"></a>

#### makeRandom

```python
def makeRandom(sigma: float = 0.25,
               limit: bool = True,
               range_min: float = None,
               range_max: float = None) -> float
```

Generates random value using normal distribution centered between self.range_min and self.range_max

The default sigma=0.25 (2-sigma) means that about 95% of the values will lie inside the range.

**Arguments**:

  -----------
  
  sigma : float = 0.25
  
  Ratio of the standard deviation of the initial distribution of the parameter values with the min-max range. sigma = stddev / (0.5 * (max_range - min_range)) I.e., if sigma=1, the standard deviation of the parameter values will be equal to half the min-max range
  
  limit : bool = True
  
  If limit=True (default), values lower than self.min will be set to self.lim and values higher that self.max will be set to self.max
  
  range_min : float = None
  
  Override self.range_min
  
  range_max : float = None
  
  Override self.range_max
  

**Returns**:

  --------
  float

