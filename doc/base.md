# Table of Contents

* [pydrodelta.base](#pydrodelta.base)
  * [Base](#pydrodelta.base.Base)
    * [load](#pydrodelta.base.Base.load)

<a id="pydrodelta.base"></a>

# pydrodelta.base

<a id="pydrodelta.base.Base"></a>

## Base Objects

```python
class Base()
```

An abstract class

<a id="pydrodelta.base.Base.load"></a>

#### load

```python
@classmethod
def load(cls, file: str, **kwargs)
```

Load configuration from yaml file

**Arguments**:

- `file` _str_ - path of yaml configuration file
- `**kwargs` - additional configuration parameters (dependant on the specific class)
  

**Returns**:

- `Plan` - an object of this class according to the provided configuration

