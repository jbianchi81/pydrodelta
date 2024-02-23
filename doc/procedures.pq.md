# Table of Contents

* [pydrodelta.procedures.pq](#pydrodelta.procedures.pq)
  * [PQProcedureFunction](#pydrodelta.procedures.pq.PQProcedureFunction)
    * [fill\_nulls](#pydrodelta.procedures.pq.PQProcedureFunction.fill_nulls)
    * [area](#pydrodelta.procedures.pq.PQProcedureFunction.area)
    * [ae](#pydrodelta.procedures.pq.PQProcedureFunction.ae)
    * [rho](#pydrodelta.procedures.pq.PQProcedureFunction.rho)
    * [wp](#pydrodelta.procedures.pq.PQProcedureFunction.wp)

<a id="pydrodelta.procedures.pq"></a>

# pydrodelta.procedures.pq

<a id="pydrodelta.procedures.pq.PQProcedureFunction"></a>

## PQProcedureFunction Objects

```python
class PQProcedureFunction(ProcedureFunction)
```

<a id="pydrodelta.procedures.pq.PQProcedureFunction.fill_nulls"></a>

#### fill\_nulls

```python
@property
def fill_nulls() -> bool
```

If missing PMAD values, fill up with zeros

<a id="pydrodelta.procedures.pq.PQProcedureFunction.area"></a>

#### area

```python
@property
def area() -> float
```

basin area in square meters

<a id="pydrodelta.procedures.pq.PQProcedureFunction.ae"></a>

#### ae

```python
@property
def ae() -> float
```

effective area (0-1)

<a id="pydrodelta.procedures.pq.PQProcedureFunction.rho"></a>

#### rho

```python
@property
def rho() -> float
```

soil porosity (0-1)

<a id="pydrodelta.procedures.pq.PQProcedureFunction.wp"></a>

#### wp

```python
@property
def wp() -> float
```

wilting point of soil (0-1)

