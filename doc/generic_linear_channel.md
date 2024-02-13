# Table of Contents

* [pydrodelta.procedures.generic\_linear\_channel](#pydrodelta.procedures.generic_linear_channel)
  * [GenericLinearChannelProcedureFunction](#pydrodelta.procedures.generic_linear_channel.GenericLinearChannelProcedureFunction)
    * [coefficients](#pydrodelta.procedures.generic_linear_channel.GenericLinearChannelProcedureFunction.coefficients)
    * [Proc](#pydrodelta.procedures.generic_linear_channel.GenericLinearChannelProcedureFunction.Proc)
    * [\_\_init\_\_](#pydrodelta.procedures.generic_linear_channel.GenericLinearChannelProcedureFunction.__init__)
    * [run](#pydrodelta.procedures.generic_linear_channel.GenericLinearChannelProcedureFunction.run)

<a id="pydrodelta.procedures.generic_linear_channel"></a>

# pydrodelta.procedures.generic\_linear\_channel

<a id="pydrodelta.procedures.generic_linear_channel.GenericLinearChannelProcedureFunction"></a>

## GenericLinearChannelProcedureFunction Objects

```python
class GenericLinearChannelProcedureFunction(ProcedureFunction)
```

Método de tránsito hidrológico implementado sobre la base de teoría de sistemas lineales. Así, considera al tránsito de energía, materia o información como un proceso lineal desde un nodo superior hacia un nodo inferior. Específicamente, sea I=[I1,I2,...,IN] el vector de pulsos generados por el borde superior y U=[U1,U2,..,UM] una función de distribución que representa el prorateo de un pulso unitario durante el tránsito desde un nodo superior (borde) hacia un nodo inferior (salida), el sistema opera aplicando las propiedades de proporcionalidad y aditividad, de manera tal que es posible propagar cada pulso a partir de U y luego mediante la suma de estos prorateos obtener el aporte de este tránsito sobre el nodo inferior (convolución).

<a id="pydrodelta.procedures.generic_linear_channel.GenericLinearChannelProcedureFunction.coefficients"></a>

#### coefficients

```python
@property
def coefficients()
```

Linear channel coefficients

<a id="pydrodelta.procedures.generic_linear_channel.GenericLinearChannelProcedureFunction.Proc"></a>

#### Proc

```python
@property
def Proc()
```

Linear channel procedure

<a id="pydrodelta.procedures.generic_linear_channel.GenericLinearChannelProcedureFunction.__init__"></a>

#### \_\_init\_\_

```python
def __init__(**kwargs)
```

Generic linear channel. Abstract class

**Arguments**:

  -----------
  /**kwargs : keyword arguments
  
  Keyword arguments:
  ------------------
  extra_pars : dict
  properties:
  dt : float
  calculation timestep

<a id="pydrodelta.procedures.generic_linear_channel.GenericLinearChannelProcedureFunction.run"></a>

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

