# Table of Contents

* [pydrodelta.procedures.junction](#pydrodelta.procedures.junction)
  * [JunctionProcedureFunction](#pydrodelta.procedures.junction.JunctionProcedureFunction)
    * [truncate\_negative](#pydrodelta.procedures.junction.JunctionProcedureFunction.truncate_negative)
    * [\_\_init\_\_](#pydrodelta.procedures.junction.JunctionProcedureFunction.__init__)
    * [run](#pydrodelta.procedures.junction.JunctionProcedureFunction.run)
    * [runJunction](#pydrodelta.procedures.junction.JunctionProcedureFunction.runJunction)

<a id="pydrodelta.procedures.junction"></a>

# pydrodelta.procedures.junction

<a id="pydrodelta.procedures.junction.JunctionProcedureFunction"></a>

## JunctionProcedureFunction Objects

```python
class JunctionProcedureFunction(ProcedureFunction)
```

Procedure function that represents the addition of two or more inputs

<a id="pydrodelta.procedures.junction.JunctionProcedureFunction.truncate_negative"></a>

#### truncate\_negative

```python
@property
def truncate_negative() -> bool
```

Replace negative output values to zero

<a id="pydrodelta.procedures.junction.JunctionProcedureFunction.__init__"></a>

#### \_\_init\_\_

```python
def __init__(extra_pars: dict = dict(), **kwargs)
```

extra_pars :dict

    Properties:
    - truncate_negative : bool = False

        Replace negative output values to zero

\**kwargs (see [..procedure_function.ProcedureFunction][])

<a id="pydrodelta.procedures.junction.JunctionProcedureFunction.run"></a>

#### run

```python
def run(
    input: List[DataFrame] = None
) -> tuple[List[DataFrame], ProcedureFunctionResults]
```

Run the procedure

**Arguments**:

  -----------
  input : list of DataFrames
  Procedure function input (boundary conditions). If None, loads using .loadInput()
  

**Returns**:

  --------
  tuple[List[DataFrame],ProcedureFunctionResults] : first element is the procedure function output (list of DataFrames), while second is a ProcedureFunctionResults object

<a id="pydrodelta.procedures.junction.JunctionProcedureFunction.runJunction"></a>

#### runJunction

```python
def runJunction(
    input: list[DataFrame] = None,
    substract: bool = False,
    truncate_negative: bool = None
) -> tuple[List[DataFrame], ProcedureFunctionResults]
```

Run junction procedure

**Arguments**:

- `input` _list[DataFrame], optional_ - Input series. Defaults to None.
- `substract` _bool, optional_ - Instead of adding, substract second input series from first. Defaults to False.
- `truncate_negative` _bool, optional_ - Set negative results to zero. Defaults to None.
  

**Returns**:

- `tuple[List[DataFrame],ProcedureFunctionResults]` - first element is the procedure function output (list of DataFrames), while second is a ProcedureFunctionResults object

