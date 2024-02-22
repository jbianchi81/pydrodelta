# Table of Contents

* [pydrodelta.procedures.expression](#pydrodelta.procedures.expression)
  * [ExpressionProcedureFunction](#pydrodelta.procedures.expression.ExpressionProcedureFunction)
    * [\_\_init\_\_](#pydrodelta.procedures.expression.ExpressionProcedureFunction.__init__)
    * [transformation\_function](#pydrodelta.procedures.expression.ExpressionProcedureFunction.transformation_function)
    * [run](#pydrodelta.procedures.expression.ExpressionProcedureFunction.run)

<a id="pydrodelta.procedures.expression"></a>

# pydrodelta.procedures.expression

<a id="pydrodelta.procedures.expression.ExpressionProcedureFunction"></a>

## ExpressionProcedureFunction Objects

```python
class ExpressionProcedureFunction(ProcedureFunction)
```

Procedure function that evaluates an arbitrary expression where 'value' is replaced with the values of input

<a id="pydrodelta.procedures.expression.ExpressionProcedureFunction.__init__"></a>

#### \_\_init\_\_

```python
def __init__(expression: str, **kwargs)
```

expression :str

    Expression to evaluate. For each step of input, 'value' is replaced with the value of input and the expression is evaluated

\**kwargs : keyword arguments (see ProcedureFunction)

<a id="pydrodelta.procedures.expression.ExpressionProcedureFunction.transformation_function"></a>

#### transformation\_function

```python
def transformation_function(value: float) -> float
```

Evaluates self.expression replacing 'value' with value

**Arguments**:

  -----------
  value : float
  The value to use in the expression
  

**Returns**:

  --------
  float

<a id="pydrodelta.procedures.expression.ExpressionProcedureFunction.run"></a>

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

