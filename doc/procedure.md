# Table of Contents

* [pydrodelta.procedure](#pydrodelta.procedure)
  * [Procedure](#pydrodelta.procedure.Procedure)
    * [loadInput](#pydrodelta.procedure.Procedure.loadInput)
    * [loadOutputObs](#pydrodelta.procedure.Procedure.loadOutputObs)
    * [run](#pydrodelta.procedure.Procedure.run)
    * [getOutputNodeData](#pydrodelta.procedure.Procedure.getOutputNodeData)

<a id="pydrodelta.procedure"></a>

# pydrodelta.procedure

<a id="pydrodelta.procedure.Procedure"></a>

## Procedure Objects

```python
class Procedure()
```

A Procedure defines an hydrological, hydrodinamic or static procedure which takes one or more NodeVariables from the Plan as boundary condition, one or more NodeVariables from the Plan as outputs and a ProcedureFunction. The input is read from the selected boundary NodeVariables and fed into the ProcedureFunction which produces an output, which is written into the output NodeVariables

<a id="pydrodelta.procedure.Procedure.loadInput"></a>

#### loadInput

```python
def loadInput(inplace=True, pivot=False)
```

Carga las variables de borde definidas en self.boundaries. De cada elemento de self.boundaries toma .data y lo concatena en una lista. Si pivot=True, devuelve un DataFrame con

<a id="pydrodelta.procedure.Procedure.loadOutputObs"></a>

#### loadOutputObs

```python
def loadOutputObs(inplace=True, pivot=False)
```

Carga las variables de output definidas en self.outputs. Para cálculo de error.

<a id="pydrodelta.procedure.Procedure.run"></a>

#### run

```python
def run(inplace=True,
        save_results: Optional[str] = None,
        parameters: Union[list, tuple] = None,
        initial_states: Union[list, tuple] = None,
        load_input=True,
        load_output_obs=True)
```

Run self.function.run()

**Arguments**:

- `inplace`: if True, writes output to self.output, else returns output (array of seriesData)

<a id="pydrodelta.procedure.Procedure.getOutputNodeData"></a>

#### getOutputNodeData

```python
def getOutputNodeData(node_id, var_id, tag=None)
```

Extracts single series from output using node id and variable id

**Arguments**:

- `node_id`: node id
- `var_id`: variable id

**Returns**:

timeseries dataframe

