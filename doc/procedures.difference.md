# Table of Contents

* [pydrodelta.procedures.difference](#pydrodelta.procedures.difference)
  * [DifferenceProcedureFunction](#pydrodelta.procedures.difference.DifferenceProcedureFunction)
    * [run](#pydrodelta.procedures.difference.DifferenceProcedureFunction.run)

<a id="pydrodelta.procedures.difference"></a>

# pydrodelta.procedures.difference

<a id="pydrodelta.procedures.difference.DifferenceProcedureFunction"></a>

## DifferenceProcedureFunction Objects

```python
class DifferenceProcedureFunction(JunctionProcedureFunction)
```

Procedure function that substracts second boundary from the first

<a id="pydrodelta.procedures.difference.DifferenceProcedureFunction.run"></a>

#### run

```python
def run(input: list = None) -> tuple
```

Run the procedure

**Arguments**:

  -----------
  input : list of DataFrames
  Procedure function input (boundary conditions). If None, loads using .loadInput()
  

**Returns**:

  --------
  2-tuple : first element is the procedure function output (list of DataFrames), while second is a ProcedureFunctionResults object

