# Table of Contents

* [pydrodelta.procedures.hosh4p1luh](#pydrodelta.procedures.hosh4p1luh)
  * [HOSH4P1LUHProcedureFunction](#pydrodelta.procedures.hosh4p1luh.HOSH4P1LUHProcedureFunction)
    * [Proc](#pydrodelta.procedures.hosh4p1luh.HOSH4P1LUHProcedureFunction.Proc)
    * [setParameters](#pydrodelta.procedures.hosh4p1luh.HOSH4P1LUHProcedureFunction.setParameters)

<a id="pydrodelta.procedures.hosh4p1luh"></a>

# pydrodelta.procedures.hosh4p1luh

<a id="pydrodelta.procedures.hosh4p1luh.HOSH4P1LUHProcedureFunction"></a>

## HOSH4P1LUHProcedureFunction Objects

```python
class HOSH4P1LUHProcedureFunction(HOSH4P1LProcedureFunction)
```

Modelo Operacional de Transformación de Precipitación en Escorrentía de 4 parámetros (estimables). Hidrología Operativa Síntesis de Hidrograma. Método NRCS, perfil de suelo con 2 reservorios de retención (sin efecto de base).

Routing with triangular hydrograph

<a id="pydrodelta.procedures.hosh4p1luh.HOSH4P1LUHProcedureFunction.Proc"></a>

#### Proc

```python
@property
def Proc() -> str
```

Routing procedure (model parameter)

<a id="pydrodelta.procedures.hosh4p1luh.HOSH4P1LUHProcedureFunction.setParameters"></a>

#### setParameters

```python
def setParameters(parameters: Union[list, tuple] = []) -> None
```

Setter for parameters

**Arguments**:

  ----------
  parameters (Union[list,tuple], optional)
  
  (maxSurfaceStorage : float, maxSoilStorage : float, T : float). Defaults to [].

