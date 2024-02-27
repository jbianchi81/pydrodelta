# Table of Contents

* [pydrodelta.procedure](#pydrodelta.procedure)
  * [Procedure](#pydrodelta.procedure.Procedure)
    * [getCalibrationPeriod](#pydrodelta.procedure.Procedure.getCalibrationPeriod)
    * [getResultIndex](#pydrodelta.procedure.Procedure.getResultIndex)
    * [toDict](#pydrodelta.procedure.Procedure.toDict)
    * [loadInput](#pydrodelta.procedure.Procedure.loadInput)
    * [loadOutputObs](#pydrodelta.procedure.Procedure.loadOutputObs)
    * [computeStatistics](#pydrodelta.procedure.Procedure.computeStatistics)
    * [read\_statistics](#pydrodelta.procedure.Procedure.read_statistics)
    * [read\_results](#pydrodelta.procedure.Procedure.read_results)
    * [run](#pydrodelta.procedure.Procedure.run)
    * [getOutputNodeData](#pydrodelta.procedure.Procedure.getOutputNodeData)
    * [outputToNodes](#pydrodelta.procedure.Procedure.outputToNodes)
    * [setIndexOfDataFrame](#pydrodelta.procedure.Procedure.setIndexOfDataFrame)
    * [testPlot](#pydrodelta.procedure.Procedure.testPlot)
    * [calibrate](#pydrodelta.procedure.Procedure.calibrate)

<a id="pydrodelta.procedure"></a>

# pydrodelta.procedure

<a id="pydrodelta.procedure.Procedure"></a>

## Procedure Objects

```python
class Procedure()
```

A Procedure defines a hydrological, hydrodinamic or static procedure which takes one or more NodeVariables from the Plan as boundary condition, one or more NodeVariables from the Plan as outputs and a ProcedureFunction. The input is read from the selected boundary NodeVariables and fed into the ProcedureFunction which produces an output, which is written into the output NodeVariables

**Arguments**:

  ----------
  
  id : int or str
  Identifier of the procedure
  
  function : dict
  ProcedureFunction configuration dict (see ProcedureFunction)
  
  plan : Plan
  Plan containing this procedure
  
  initial_states : list or None
  List of procedure initial states. The order of the states is defined in .function._states
  
  parameters : list or None
  List of procedure parameters. The order of the parameters is defined in .function._model_parameters
  
  time_interval : str or dict (time duration)
  Time step duration of the procedure
  
  time_offset : str or dict (time duration)
  Time offset duration of the procedure
  
  save_results : str or None
  Save procedure results into this file (csv pivoted table)
  
  overwrite : bool
  When exporting procedure results into the topology, overwrite observations in NodeVariable.data
  
  overwrite_original : bool
  When exporting procedure results into the topology, overwrite observations in NodeVariable.original_data
  
  calibration : dict
  Configuration for Downhill Simplex calibration procedure (see Calibration)

<a id="pydrodelta.procedure.Procedure.getCalibrationPeriod"></a>

#### getCalibrationPeriod

```python
def getCalibrationPeriod() -> Union[tuple, None]
```

Read the calibration period from the calibration configuration

<a id="pydrodelta.procedure.Procedure.getResultIndex"></a>

#### getResultIndex

```python
def getResultIndex() -> int
```

Read the calibration period from the calibration configuration

<a id="pydrodelta.procedure.Procedure.toDict"></a>

#### toDict

```python
def toDict() -> dict
```

Convert this instance into a dict

<a id="pydrodelta.procedure.Procedure.loadInput"></a>

#### loadInput

```python
def loadInput(inplace: bool = True,
              pivot: bool = False) -> Union[List[DataFrame], DataFrame]
```

Loads the boundary variables defined in self.function.boundaries. Takes .data from each element of self.function.boundaries and returns a list. If pivot=True, joins all variables into a single DataFrame

**Arguments**:

  ----------
  
  inplace : bool
  If True, saves result into self.data and returns None
  
- `pivot` - bool
  If true, joins all variables into a single DataFrame

<a id="pydrodelta.procedure.Procedure.loadOutputObs"></a>

#### loadOutputObs

```python
def loadOutputObs(inplace: bool = True, pivot: bool = False)
```

Load observed values of output variables defined in self.function.outputs. Used in error calculation.

**Arguments**:

  -----------
  
  inplace : bool
  If True, saves result into self.output_obs and returns None
  
- `pivot` - bool
  If true, joins all variables into a single DataFrame

<a id="pydrodelta.procedure.Procedure.computeStatistics"></a>

#### computeStatistics

```python
def computeStatistics(obs: Optional[list] = None,
                      sim: Optional[list] = None,
                      calibration_period: Optional[tuple] = None,
                      result_index: int = 0) -> Tuple[List[ResultStatistics]]
```

Compute statistics over procedure results.

**Arguments**:

  ----------
  
  obs : list of DataFrames or None
  List of observation DataFrames
  
  sim : list of DataFrames or None
  List of simulated values. Must be of the same length as obs
  
  calibration_period : tuple or None
  start and end date for split statistics computations between calibration and validation periods
  
  Returns
  -------
  (calibration_results, validation_results) : 2-length tuple of lists of ResultStatistics. The length of the lists equals that of obs

<a id="pydrodelta.procedure.Procedure.read_statistics"></a>

#### read\_statistics

```python
def read_statistics() -> dict
```

Get result statistics as a dict

Returns
-------
statistics : dict of the form:
    {
        "procedure_id": int,
        "function_type": str,
        "results": list[dict]
    }

<a id="pydrodelta.procedure.Procedure.read_results"></a>

#### read\_results

```python
def read_results() -> dict
```

Get results as a dict

Returns
-------
results : dict of the form:
    {
        "procedure_id": int,
        "function_type": str,
        "results": dict    
    }

<a id="pydrodelta.procedure.Procedure.run"></a>

#### run

```python
def run(inplace: bool = True,
        save_results: Optional[str] = None,
        parameters: Union[list, tuple] = None,
        initial_states: Union[list, tuple] = None,
        load_input: bool = True,
        load_output_obs: bool = True) -> Union[list[DataFrame], None]
```

Run self.function.run()

**Arguments**:

  ----------
  
  inplace : bool
  If True, writes output to self.output, else returns output (array of seriesData)
  save_results : str or None
  Save procedure reuslts into this file
  parameters : list, tuple or None
  Procedure function parameters
  initial_states : list, tuple or None
  Procedure function initial states
  load_input : bool
  If True, load input using .loadInput. Else, reads from .input
  load_output_obs : bool
  If True, load observed output using .loadOutputObs. Else, reads from .output_obs
  
  Returns
  -------
  None if inplace=True, else
  list of DataFrames

<a id="pydrodelta.procedure.Procedure.getOutputNodeData"></a>

#### getOutputNodeData

```python
def getOutputNodeData(node_id: int, var_id: int, tag=None) -> None
```

Extracts single series from output using node id and variable id

**Arguments**:

  ----------
  
  node_id : int
  Node identifier. Must be present in self.plan.topology.nodes
  var_id : int
  Variable identifier. Must be present in the selected node of self.plan.topology.nodes
  
  Returns
  ----------
  timeseries dataframe : DataFrame

<a id="pydrodelta.procedure.Procedure.outputToNodes"></a>

#### outputToNodes

```python
def outputToNodes(overwrite: bool = None,
                  overwrite_original: bool = None) -> None
```

Saves procedure output into the topology. Each element of self.output is concatenated into the .data property of the corresponding NodeVariable in self.plan.topology.nodes according the mapping defined in self.function.outputs.

**Arguments**:

  ----------
  
  overwrite : bool
  Overwrite observations in NodeVariable.data
  overwrite_original : bool
  Overwrite observations in NodeVariable.original_data

<a id="pydrodelta.procedure.Procedure.setIndexOfDataFrame"></a>

#### setIndexOfDataFrame

```python
def setIndexOfDataFrame(data: DataFrame,
                        time_interval: timedelta) -> DataFrame
```

Set index of data frame from topology begin and end dates and time_interval

<a id="pydrodelta.procedure.Procedure.testPlot"></a>

#### testPlot

```python
def testPlot(index: int = 0) -> None
```

Plot observed and simulated variable vs. time in the same chart.

**Arguments**:

  ----------
  
  index : int (default 0)
  Which element of self.output to plot

<a id="pydrodelta.procedure.Procedure.calibrate"></a>

#### calibrate

```python
def calibrate(inplace: bool = True) -> Union[tuple, None]
```

Run Nelder-Mead Downhill Simplex calibration procedure. Calibration configuration is read from self.calibration (set at class instantiation)

**Arguments**:

  ----------
  
  inplace : bool
  If true, set resulting parameters in self.function.parameters. Else, returns resulting parameters
  
  Returns
  -------
  if inplace = True
  None
  else:
  Tuple where first element is the list of resulting parameters and the second is the resulting objective function

