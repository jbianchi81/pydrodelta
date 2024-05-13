# Table of Contents

* [pydrodelta.procedures.linear\_fit](#pydrodelta.procedures.linear_fit)
  * [LinearFitProcedureFunction](#pydrodelta.procedures.linear_fit.LinearFitProcedureFunction)
    * [warmup\_steps](#pydrodelta.procedures.linear_fit.LinearFitProcedureFunction.warmup_steps)
    * [tail\_steps](#pydrodelta.procedures.linear_fit.LinearFitProcedureFunction.tail_steps)
    * [linear\_model](#pydrodelta.procedures.linear_fit.LinearFitProcedureFunction.linear_model)
    * [use\_forecast\_range](#pydrodelta.procedures.linear_fit.LinearFitProcedureFunction.use_forecast_range)
    * [sim\_range](#pydrodelta.procedures.linear_fit.LinearFitProcedureFunction.sim_range)
    * [\_\_init\_\_](#pydrodelta.procedures.linear_fit.LinearFitProcedureFunction.__init__)
    * [run](#pydrodelta.procedures.linear_fit.LinearFitProcedureFunction.run)
    * [getSimRange](#pydrodelta.procedures.linear_fit.LinearFitProcedureFunction.getSimRange)

<a id="pydrodelta.procedures.linear_fit"></a>

# pydrodelta.procedures.linear\_fit

<a id="pydrodelta.procedures.linear_fit.LinearFitProcedureFunction"></a>

## LinearFitProcedureFunction Objects

```python
class LinearFitProcedureFunction(ProcedureFunction)
```

Procedure function that fits a linear function between an independent variable (input) and a response and then applies the resulting function to the input values to produce the output

<a id="pydrodelta.procedures.linear_fit.LinearFitProcedureFunction.warmup_steps"></a>

#### warmup\_steps

Skip this number of initial steps for fit procedure

<a id="pydrodelta.procedures.linear_fit.LinearFitProcedureFunction.tail_steps"></a>

#### tail\_steps

Use only this number of final steps for fit procedure

<a id="pydrodelta.procedures.linear_fit.LinearFitProcedureFunction.linear_model"></a>

#### linear\_model

Results of the fit procedure

<a id="pydrodelta.procedures.linear_fit.LinearFitProcedureFunction.use_forecast_range"></a>

#### use\_forecast\_range

Fit using only pairs where sim is within forecasted range of values

<a id="pydrodelta.procedures.linear_fit.LinearFitProcedureFunction.sim_range"></a>

#### sim\_range

```python
@property
def sim_range() -> Tuple[float, float]
```

Inmutable. Values range used for fit

<a id="pydrodelta.procedures.linear_fit.LinearFitProcedureFunction.__init__"></a>

#### \_\_init\_\_

```python
def __init__(**kwargs)
```

\**kwargs : keyword arguments (see ProcedureFunction)

<a id="pydrodelta.procedures.linear_fit.LinearFitProcedureFunction.run"></a>

#### run

```python
def run(input: list = None) -> tuple
```

Ejecuta la función. Si input es None, ejecuta self._procedure.loadInput para generar el input. input debe ser una lista de objetos SeriesData
Devuelve una lista de objetos SeriesData y opcionalmente un objeto ProcedureFunctionResults

**Arguments**:

  -----------
  input : list of DataFrames
  Procedure function input (boundary conditions). If None, loads using .loadInput()
  

**Returns**:

  --------
  2-tuple : first element is the procedure function output (list of DataFrames), while second is a ProcedureFunctionResults object

<a id="pydrodelta.procedures.linear_fit.LinearFitProcedureFunction.getSimRange"></a>

#### getSimRange

```python
def getSimRange(data, expand: float = None) -> Tuple[float, float]
```

Get values range of data in the forecasted period

**Arguments**:

- `data` _DataFrame_ - Series DataFrame
- `expand` _float, optional_ - Expand the range by this fraction (of max - min). Defaults to None.
  

**Returns**:

- `Tuple[float,float]` - (lower bound, upper bound)

