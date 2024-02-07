# Table of Contents

* [pydrodelta.plan](#pydrodelta.plan)
  * [Plan](#pydrodelta.plan.Plan)
    * [\_\_init\_\_](#pydrodelta.plan.Plan.__init__)
    * [execute](#pydrodelta.plan.Plan.execute)
    * [toCorrida](#pydrodelta.plan.Plan.toCorrida)
    * [uploadSim](#pydrodelta.plan.Plan.uploadSim)
    * [toCorridaJson](#pydrodelta.plan.Plan.toCorridaJson)
    * [toCorridaDataFrame](#pydrodelta.plan.Plan.toCorridaDataFrame)
    * [toCorridaCsv](#pydrodelta.plan.Plan.toCorridaCsv)
    * [toGraph](#pydrodelta.plan.Plan.toGraph)
    * [printGraph](#pydrodelta.plan.Plan.printGraph)
    * [exportGraph](#pydrodelta.plan.Plan.exportGraph)

<a id="pydrodelta.plan"></a>

# pydrodelta.plan

<a id="pydrodelta.plan.Plan"></a>

## Plan Objects

```python
class Plan()
```

Use this class to set up a modelling configuration, including the topology and the procedures.

A plan is the root element of a pydro configuration

<a id="pydrodelta.plan.Plan.__init__"></a>

#### \_\_init\_\_

```python
def __init__(name: str,
             id: int,
             topology: Union[dict, str],
             procedures: list = [],
             forecast_date: Union[dict, str] = datetime.now(),
             time_interval: Union[dict, str] = None,
             output_stats: str = None,
             output_analysis: str = None,
             pivot: bool = False,
             save_post: str = None,
             save_response: str = None)
```

A plan defines a modelling configuration, including the topology, the procedures, the forecast date, time interval and output options. It is the root element of a pydro configuration

**Arguments**:

  -----------
  
  name : str
  Name of the plan
  
  id : int
  numeric id of the plan. Used as identifier when saving into the output api
  
  topology : dict or filepath
  Either topology configuration dict or a topology configuration file path (see Topology)
  
  procedures : list
  List of procedure dicts (see Procedure)
  
  forecast_date : str or dict
  Execution timestamp of the plan. Defaults to now rounded down to time_interval
  
  time_interval : str or dict
  time step duration of the procedures
  
  output_stats : str or None
  file path where to save result statistics
  
  output_analysis : str or None
  file path where to save analysis results
  
  pivot : bool
  option to pivot the results table (set one column per variable). Default False
  
  save_post : str or None
  file path where to save the post data sent to the output api
  
  save_response : str or None
  file path where to save the output api response

<a id="pydrodelta.plan.Plan.execute"></a>

#### execute

```python
def execute(include_prono=True, upload=True, pretty=False)
```

Runs analysis and then each procedure sequentially

**Arguments**:

  -----------
  
  include_prono : bool
  If True (default), concatenates observed and forecasted boundary conditions. Else, reads only observed data.
  
  upload : bool
  If True (default), Uploads result into output api.
  
  pretty : bool
  Pretty print results. Default False
  

**Returns**:

  --------
  
  None

<a id="pydrodelta.plan.Plan.toCorrida"></a>

#### toCorrida

```python
def toCorrida() -> dict
```

Convert simulation results into dict according to alerta5DBIO schema (https://raw.githubusercontent.com/jbianchi81/alerta5DBIO/master/public/schemas/a5/corrida.yml)

**Returns**:

  --------
  
  dict

<a id="pydrodelta.plan.Plan.uploadSim"></a>

#### uploadSim

```python
def uploadSim() -> dict
```

Upload forecast into output api.

If self.save_post is not None, saves the post message before request into that filepath.

If self.save_response not None, saves server response (either the created forecast or an error message) into that filepath

**Returns**:

  --------
  
  dict : created forecast

<a id="pydrodelta.plan.Plan.toCorridaJson"></a>

#### toCorridaJson

```python
def toCorridaJson(filename, pretty=False) -> None
```

Saves forecast into filename (json) using alerta5DBIO schema (https://raw.githubusercontent.com/jbianchi81/alerta5DBIO/master/public/schemas/a5/corrida.yml)

**Arguments**:

  -----------
  filename : str
  File path where to save
  
  pretty : bool
  Pretty-print JSON (default False)
  

**Returns**:

  --------
  
  None

<a id="pydrodelta.plan.Plan.toCorridaDataFrame"></a>

#### toCorridaDataFrame

```python
def toCorridaDataFrame(pivot=False) -> DataFrame
```

Concatenates forecast data into a DataFrame

**Arguments**:

  -----------
  pivot : bool
  Pivot the DataFrame with one column per variable grouping by timestamp. Default False
  

**Returns**:

  --------
  
  DataFrame

<a id="pydrodelta.plan.Plan.toCorridaCsv"></a>

#### toCorridaCsv

```python
def toCorridaCsv(filename, pivot=False, include_header=True) -> None
```

Saves forecast as csv

**Arguments**:

  -----------
  
  filename : str
  Where to save the csv file
  
  pivot : bool
  Pivot the table with one column per variable grouping by timestamp. Default False
  
  include_header : bool
  Add a header to the csv file. Default True
  

**Returns**:

  --------
  
  None

<a id="pydrodelta.plan.Plan.toGraph"></a>

#### toGraph

```python
def toGraph(nodes: Union[list, None]) -> nx.DiGraph
```

Generate directioned graph from the plan. Topology nodes are linked to procedures according to the mapping provided at procedure.function.boundaries (node to procedure) and procedure.function.outputs (procedure to node)

**Arguments**:

  -----------
  nodes : list or None
  List of nodes to use for building the graph. If None, uses self.topology.nodes
  

**Returns**:

  --------
  NetworkX.DiGraph (See https://networkx.org for complete documentation)
  
  See also:
  ---------
  printGraph
  exportGraph

<a id="pydrodelta.plan.Plan.printGraph"></a>

#### printGraph

```python
def printGraph(nodes: Union[list, None] = None,
               output_file: Union[str, None] = None) -> None
```

Print directioned graph from the plan. Topology nodes are linked to procedures according to the mapping provided at procedure.function.boundaries (node to procedure) and procedure.function.outputs (procedure to node)

**Arguments**:

  -----------
  nodes : list or None
  List of nodes to use for building the graph. If None, uses self.topology.nodes
  
  output_file : str
  Where to save the graph file
  

**Returns**:

  --------
  None
  
  See also:
  ---------
  toGraph
  exportGraph

<a id="pydrodelta.plan.Plan.exportGraph"></a>

#### exportGraph

```python
def exportGraph(nodes: Union[list, None] = None,
                output_file: Union[str, None] = None) -> Union[str, None]
```

Creates directioned graph from the plan and converts it to JSON. Topology nodes are linked to procedures according to the mapping provided at procedure.function.boundaries (node to procedure) and procedure.function.outputs (procedure to node)

**Arguments**:

  -----------
  nodes : list or None
  List of nodes to use for building the graph. If None, uses self.topology.nodes
  
  output_file : str or None
  Where to save the JSON file. If None, returns the JSON string
  

**Returns**:

  --------
  str or None
  
  See also:
  ---------
  toGraph
  printGraph

