# Table of Contents

* [pydrodelta.procedures.hosh4p1lnash](#pydrodelta.procedures.hosh4p1lnash)
  * [HOSH4P1LNashProcedureFunction](#pydrodelta.procedures.hosh4p1lnash.HOSH4P1LNashProcedureFunction)
    * [Proc](#pydrodelta.procedures.hosh4p1lnash.HOSH4P1LNashProcedureFunction.Proc)
    * [\_\_init\_\_](#pydrodelta.procedures.hosh4p1lnash.HOSH4P1LNashProcedureFunction.__init__)
    * [setParameters](#pydrodelta.procedures.hosh4p1lnash.HOSH4P1LNashProcedureFunction.setParameters)

<a id="pydrodelta.procedures.hosh4p1lnash"></a>

# pydrodelta.procedures.hosh4p1lnash

<a id="pydrodelta.procedures.hosh4p1lnash.HOSH4P1LNashProcedureFunction"></a>

## HOSH4P1LNashProcedureFunction Objects

```python
class HOSH4P1LNashProcedureFunction(HOSH4P1LProcedureFunction)
```

Modelo Operacional de Transformación de Precipitación en Escorrentía de 4 parámetros (estimables). Hidrología Operativa Síntesis de Hidrograma. Método NRCS, perfil de suelo con 2 reservorios de retención (sin efecto de base).

Routing with Nash cascade

<a id="pydrodelta.procedures.hosh4p1lnash.HOSH4P1LNashProcedureFunction.Proc"></a>

#### Proc

```python
@property
def Proc() -> str
```

Routing procedure (model parameter)

<a id="pydrodelta.procedures.hosh4p1lnash.HOSH4P1LNashProcedureFunction.__init__"></a>

#### \_\_init\_\_

```python
def __init__(parameters: Union[list, tuple, dict], **kwargs)
```

parameters : 

    Model parameters. Ordered list or dict

    Properties:
    - maxSurfaceStorage
    - maxSoilStorage
    - k of Nash cascade
    - n of Nash cascade

\**kwargs : keyword arguments (see [..hosh4p1l.HOSH4P1L][])

<a id="pydrodelta.procedures.hosh4p1lnash.HOSH4P1LNashProcedureFunction.setParameters"></a>

#### setParameters

```python
def setParameters(parameters: Union[list, tuple] = []) -> None
```

Parameters setter

**Arguments**:

  -----------
  parameters : Union[list,tuple] = []
  
  (maxSurfaceStorage : float, maxSoilStorage : float, k : float, n : float)

