# Table of Contents

* [pydrodelta.procedures.uh\_linear\_channel](#pydrodelta.procedures.uh_linear_channel)
  * [UHLinearChannelProcedureFunction](#pydrodelta.procedures.uh_linear_channel.UHLinearChannelProcedureFunction)
    * [coefficients](#pydrodelta.procedures.uh_linear_channel.UHLinearChannelProcedureFunction.coefficients)
    * [Proc](#pydrodelta.procedures.uh_linear_channel.UHLinearChannelProcedureFunction.Proc)
    * [\_\_init\_\_](#pydrodelta.procedures.uh_linear_channel.UHLinearChannelProcedureFunction.__init__)

<a id="pydrodelta.procedures.uh_linear_channel"></a>

# pydrodelta.procedures.uh\_linear\_channel

<a id="pydrodelta.procedures.uh_linear_channel.UHLinearChannelProcedureFunction"></a>

## UHLinearChannelProcedureFunction Objects

```python
class UHLinearChannelProcedureFunction(GenericLinearChannelProcedureFunction)
```

<a id="pydrodelta.procedures.uh_linear_channel.UHLinearChannelProcedureFunction.coefficients"></a>

#### coefficients

```python
@property
def coefficients()
```

Linear channel coefficients (u)

<a id="pydrodelta.procedures.uh_linear_channel.UHLinearChannelProcedureFunction.Proc"></a>

#### Proc

```python
@property
def Proc()
```

Linear channel procedure

<a id="pydrodelta.procedures.uh_linear_channel.UHLinearChannelProcedureFunction.__init__"></a>

#### \_\_init\_\_

```python
def __init__(parameters: UHParameters,
             extra_pars: UHExtraPars = dict(),
             **kwargs)
```

Unit Hydrograph linear channel

**Arguments**:

  ------------------
  - parameters : UHParameters
  dict with properties: u: distribution function. list of floats
  
  - extra_pars: UHExtraPars
  dict with properties: dt: calculation timestep (default=1)
  

**Examples**:

  ---------
```
uh_linear_channel = UHLinearChannelProcedureFunction(
    parameters={"u": [0.2,0.5,0.3]},
    extra_pars:{"dt": 1}
)
```

