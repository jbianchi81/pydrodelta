# Table of Contents

* [pydrodelta.procedures.linear\_channel](#pydrodelta.procedures.linear_channel)
  * [LinearChannelProcedureFunction](#pydrodelta.procedures.linear_channel.LinearChannelProcedureFunction)
    * [coefficients](#pydrodelta.procedures.linear_channel.LinearChannelProcedureFunction.coefficients)
    * [Proc](#pydrodelta.procedures.linear_channel.LinearChannelProcedureFunction.Proc)
    * [\_\_init\_\_](#pydrodelta.procedures.linear_channel.LinearChannelProcedureFunction.__init__)

<a id="pydrodelta.procedures.linear_channel"></a>

# pydrodelta.procedures.linear\_channel

<a id="pydrodelta.procedures.linear_channel.LinearChannelProcedureFunction"></a>

## LinearChannelProcedureFunction Objects

```python
class LinearChannelProcedureFunction(GenericLinearChannelProcedureFunction)
```

Nash Linear channel procedure (gamma distribution)

<a id="pydrodelta.procedures.linear_channel.LinearChannelProcedureFunction.coefficients"></a>

#### coefficients

```python
@property
def coefficients()
```

Linear channel coefficients (k, n)

<a id="pydrodelta.procedures.linear_channel.LinearChannelProcedureFunction.Proc"></a>

#### Proc

```python
@property
def Proc()
```

Linear channel procedure

<a id="pydrodelta.procedures.linear_channel.LinearChannelProcedureFunction.__init__"></a>

#### \_\_init\_\_

```python
def __init__(parameters: Union[dict, list, tuple], **kwargs)
```

Nash linear channel (gamma distribution)

**Arguments**:

  -----------
  parameters : dict
  
  properties:
  k : float residence time
  n : float number of reservoirs
  
  /**kwargs : keyword arguments
  
  Keyword arguments:
  ------------------
- `extra_pars` - dict
  properties
  dt : float calculation timestep

