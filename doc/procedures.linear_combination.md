# Table of Contents

* [pydrodelta.procedures.linear\_combination](#pydrodelta.procedures.linear_combination)
  * [BoundaryCoefficients](#pydrodelta.procedures.linear_combination.BoundaryCoefficients)
    * [name](#pydrodelta.procedures.linear_combination.BoundaryCoefficients.name)
    * [value](#pydrodelta.procedures.linear_combination.BoundaryCoefficients.value)
    * [\_\_init\_\_](#pydrodelta.procedures.linear_combination.BoundaryCoefficients.__init__)
    * [toDict](#pydrodelta.procedures.linear_combination.BoundaryCoefficients.toDict)
  * [ForecastStep](#pydrodelta.procedures.linear_combination.ForecastStep)
    * [intercept](#pydrodelta.procedures.linear_combination.ForecastStep.intercept)
    * [boundaries](#pydrodelta.procedures.linear_combination.ForecastStep.boundaries)
    * [\_\_init\_\_](#pydrodelta.procedures.linear_combination.ForecastStep.__init__)
    * [toDict](#pydrodelta.procedures.linear_combination.ForecastStep.toDict)
  * [LinearCombinationProcedureFunction](#pydrodelta.procedures.linear_combination.LinearCombinationProcedureFunction)
    * [coefficients](#pydrodelta.procedures.linear_combination.LinearCombinationProcedureFunction.coefficients)
    * [\_\_init\_\_](#pydrodelta.procedures.linear_combination.LinearCombinationProcedureFunction.__init__)
    * [run](#pydrodelta.procedures.linear_combination.LinearCombinationProcedureFunction.run)

<a id="pydrodelta.procedures.linear_combination"></a>

# pydrodelta.procedures.linear\_combination

<a id="pydrodelta.procedures.linear_combination.BoundaryCoefficients"></a>

## BoundaryCoefficients Objects

```python
class BoundaryCoefficients()
```

Linear combination coefficients for a boundary at a given forecast step

<a id="pydrodelta.procedures.linear_combination.BoundaryCoefficients.name"></a>

#### name

Name of the boundary. Must map to a name of a procedureFunction's boundary

<a id="pydrodelta.procedures.linear_combination.BoundaryCoefficients.value"></a>

#### value

List of coefficients (floats). First is for the last observation time step, second is for the previous step, and so on

<a id="pydrodelta.procedures.linear_combination.BoundaryCoefficients.__init__"></a>

#### \_\_init\_\_

```python
def __init__(name: str, values: list[float], procedure_function)
```

**Arguments**:

- `name` _str_ - Name of the boundary. Must map to a name of a procedureFunction's boundary_
- `values` _list[float]_ - List of coefficients (floats). First is for the last observation time step, second is for the previous step, and so on
- `procedure_function` _ProcedureFunction_ - Reference to the ProcedureFunction that contains this
  

**Raises**:

- `Exception` - If length of values is not equal to procedure function lookback steps

<a id="pydrodelta.procedures.linear_combination.BoundaryCoefficients.toDict"></a>

#### toDict

```python
def toDict() -> dict
```

Convert to dict

<a id="pydrodelta.procedures.linear_combination.ForecastStep"></a>

## ForecastStep Objects

```python
class ForecastStep()
```

Linear combination parameters for a given forecast step

<a id="pydrodelta.procedures.linear_combination.ForecastStep.intercept"></a>

#### intercept

Intercept of the linear combination

<a id="pydrodelta.procedures.linear_combination.ForecastStep.boundaries"></a>

#### boundaries

```python
@boundaries.setter
def boundaries(boundaries: List[BoundaryDict]) -> None
```

**Arguments**:

- `boundaries` _List[dict]_ - List where each item is a dict with a name property that maps to the procedureFunction's boundaries and a values property that is a list of coefficients for that boundary
  

**Raises**:

- `Exception` - If a boundary name is not found in the procedureFunction's boundaries

<a id="pydrodelta.procedures.linear_combination.ForecastStep.__init__"></a>

#### \_\_init\_\_

```python
def __init__(intercept: float, boundaries: List[BoundaryDict],
             procedure_function)
```

**Arguments**:

- `intercept` _float_ - Intercept of the linear combination
- `boundaries` _List[dict]_ - List where each item is a dict with a name property that maps to the procedureFunction's boundaries and a values property that is a list of coefficients for that boundary
- `procedure_function` __type__ - Reference to the ProcedureFunction that contains this.

<a id="pydrodelta.procedures.linear_combination.ForecastStep.toDict"></a>

#### toDict

```python
def toDict() -> dict
```

Convert to dict

<a id="pydrodelta.procedures.linear_combination.LinearCombinationProcedureFunction"></a>

## LinearCombinationProcedureFunction Objects

```python
class LinearCombinationProcedureFunction(ProcedureFunction)
```

Multivariable linear combination procedure function - one linear combination for each forecast horizon. Being x [, y, ...] the boundary series, for each forecast time step t it returns intercept[t] + [ x[-l] * coefficients[t]boundaries['x'][l] for l in 1..lookback_steps ] and so on for additional boundaries and lookback steps.

<a id="pydrodelta.procedures.linear_combination.LinearCombinationProcedureFunction.coefficients"></a>

#### coefficients

```python
@property
def coefficients() -> List[ForecastStep]
```

Coefficients of the linear combination

<a id="pydrodelta.procedures.linear_combination.LinearCombinationProcedureFunction.__init__"></a>

#### \_\_init\_\_

```python
def __init__(parameters: LinearCombinationParametersDict, **kwargs)
```

**Arguments**:

  parameters : LinearCombinationParametersDict:
  Properties:
  - forecast_steps : int
  - lookback_steps : int
  - coefficients : List[ForecastStepDict]
  

**Raises**:

- `Exception` - _description_
- `Exception` - _description_

<a id="pydrodelta.procedures.linear_combination.LinearCombinationProcedureFunction.run"></a>

#### run

```python
def run(
    input: list[DataFrame] = None
) -> tuple[List[DataFrame], ProcedureFunctionResults]
```

Run the function procedure

**Arguments**:

  input : list of DataFrames
  Boundary conditions. If None, runs .loadInput
  

**Returns**:

  tuple[List[DataFrame],ProcedureFunctionResults] : first element is the procedure function output (list of DataFrames), while second is a ProcedureFunctionResults object
  

**Raises**:

  Exception : If data is missing in a boundary at a required timestep

