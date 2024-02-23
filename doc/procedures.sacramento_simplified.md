# Table of Contents

* [pydrodelta.procedures.sacramento\_simplified](#pydrodelta.procedures.sacramento_simplified)
  * [SacramentoSimplifiedProcedureFunction](#pydrodelta.procedures.sacramento_simplified.SacramentoSimplifiedProcedureFunction)
    * [run](#pydrodelta.procedures.sacramento_simplified.SacramentoSimplifiedProcedureFunction.run)

<a id="pydrodelta.procedures.sacramento_simplified"></a>

# pydrodelta.procedures.sacramento\_simplified

<a id="pydrodelta.procedures.sacramento_simplified.SacramentoSimplifiedProcedureFunction"></a>

## SacramentoSimplifiedProcedureFunction Objects

```python
class SacramentoSimplifiedProcedureFunction(PQProcedureFunction)
```

<a id="pydrodelta.procedures.sacramento_simplified.SacramentoSimplifiedProcedureFunction.run"></a>

#### run

```python
def run(
    input: Optional[List[SeriesData]] = None
) -> Tuple[List[SeriesData], ProcedureFunctionResults]
```

Ejecuta la función. Si input es None, ejecuta self._procedure.loadInput para generar el input. input debe ser una lista de objetos SeriesData
Devuelve una lista de objetos SeriesData y opcionalmente un objeto ProcedureFunctionResults

