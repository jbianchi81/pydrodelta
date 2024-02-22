# Table of Contents

* [pydrodelta.procedure\_function\_results](#pydrodelta.procedure_function_results)
  * [ProcedureFunctionResults](#pydrodelta.procedure_function_results.ProcedureFunctionResults)
    * [\_\_init\_\_](#pydrodelta.procedure_function_results.ProcedureFunctionResults.__init__)
    * [setStatistics](#pydrodelta.procedure_function_results.ProcedureFunctionResults.setStatistics)
    * [setStatisticsVal](#pydrodelta.procedure_function_results.ProcedureFunctionResults.setStatisticsVal)
    * [save](#pydrodelta.procedure_function_results.ProcedureFunctionResults.save)
    * [toDict](#pydrodelta.procedure_function_results.ProcedureFunctionResults.toDict)

<a id="pydrodelta.procedure_function_results"></a>

# pydrodelta.procedure\_function\_results

<a id="pydrodelta.procedure_function_results.ProcedureFunctionResults"></a>

## ProcedureFunctionResults Objects

```python
class ProcedureFunctionResults()
```

The results of a ProcedureFunction run

<a id="pydrodelta.procedure_function_results.ProcedureFunctionResults.__init__"></a>

#### \_\_init\_\_

```python
def __init__(border_conditions: Union[List[DataFrame], DataFrame] = None,
             initial_states: Union[list, dict] = None,
             states: Union[list, DataFrame] = None,
             parameters: Union[list, dict] = None,
             statistics: Union[list, dict] = None,
             statistics_val: list = None,
             data: DataFrame = None,
             extra_pars: dict = None)
```

border_conditions : Union[List[DataFrame],DataFrame] = None

    Border conditions timeseries

initial_states : Union[list,dict] = None

    Initial states

states : Union[List[DataFrame],DataFrame] = None

    States timeseries

parameters : Union[list,dict] = None

    Procedure function calibratable parameters

statistics : Union[list,dict] = None

    Result statistics

statistics_val : list = None

    Validation result statistics

data : DataFrame = None

    Procedure function pivoted table. May include boundaries, states and/or outputs

extra_pars : dict = None

    Additional, non-calibratable parameters

<a id="pydrodelta.procedure_function_results.ProcedureFunctionResults.setStatistics"></a>

#### setStatistics

```python
def setStatistics(result_statistics: Optional[list] = None) -> None
```

Set .statistics from result_statistics

<a id="pydrodelta.procedure_function_results.ProcedureFunctionResults.setStatisticsVal"></a>

#### setStatisticsVal

```python
def setStatisticsVal(result_statistics: Optional[list] = None) -> None
```

Set .statistics_val from result_statistics

<a id="pydrodelta.procedure_function_results.ProcedureFunctionResults.save"></a>

#### save

```python
def save(output: str) -> None
```

Save procedure function data as csv file

**Arguments**:

  -----------
  output : str
  
  Path of csv file to write

<a id="pydrodelta.procedure_function_results.ProcedureFunctionResults.toDict"></a>

#### toDict

```python
def toDict() -> dict
```

Convert procedure function results to dict

