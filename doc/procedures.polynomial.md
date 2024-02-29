# Table of Contents

* [pydrodelta.procedures.polynomial](#pydrodelta.procedures.polynomial)
  * [PolynomialTransformationProcedureFunction](#pydrodelta.procedures.polynomial.PolynomialTransformationProcedureFunction)
    * [coefficients](#pydrodelta.procedures.polynomial.PolynomialTransformationProcedureFunction.coefficients)
    * [intercept](#pydrodelta.procedures.polynomial.PolynomialTransformationProcedureFunction.intercept)
    * [\_\_init\_\_](#pydrodelta.procedures.polynomial.PolynomialTransformationProcedureFunction.__init__)
    * [transformation\_function](#pydrodelta.procedures.polynomial.PolynomialTransformationProcedureFunction.transformation_function)
    * [run](#pydrodelta.procedures.polynomial.PolynomialTransformationProcedureFunction.run)

<a id="pydrodelta.procedures.polynomial"></a>

# pydrodelta.procedures.polynomial

<a id="pydrodelta.procedures.polynomial.PolynomialTransformationProcedureFunction"></a>

## PolynomialTransformationProcedureFunction Objects

```python
class PolynomialTransformationProcedureFunction(ProcedureFunction)
```

Polynomial transformation procedure

<a id="pydrodelta.procedures.polynomial.PolynomialTransformationProcedureFunction.coefficients"></a>

#### coefficients

```python
@property
def coefficients() -> List[float]
```

coefficients : list of float of length >= 1 - first is the linear coefficient, second is the quadratic

<a id="pydrodelta.procedures.polynomial.PolynomialTransformationProcedureFunction.intercept"></a>

#### intercept

```python
@property
def intercept() -> float
```

intercept : float - default 0

<a id="pydrodelta.procedures.polynomial.PolynomialTransformationProcedureFunction.__init__"></a>

#### \_\_init\_\_

```python
def __init__(parameters: Union[dict, list, tuple], **kwargs)
```

_summary_

**Arguments**:

  ----------
- `parameters` _Union[dict,list,tuple]_ - Model parameters
  
  Properties:
  - coefficients : list of float of length >= 1 - first is the linear coefficient, second is the quadratic coefficient, and so on
  - intercept : float - default 0
  
  \**kwargs : see ..procedure_function.ProcedureFunction

<a id="pydrodelta.procedures.polynomial.PolynomialTransformationProcedureFunction.transformation_function"></a>

#### transformation\_function

```python
def transformation_function(value: float) -> float
```

Return polynomial function result. self.intercept + self.coefficients[0] * value [ + self.coefficients[1] * value**2 + and so on ]

**Arguments**:

  -----------
  value : float
  value of the independent variable
  

**Returns**:

  --------
  float

<a id="pydrodelta.procedures.polynomial.PolynomialTransformationProcedureFunction.run"></a>

#### run

```python
def run(
    input: List[DataFrame] = None
) -> Tuple[List[DataFrame], ProcedureFunctionResults]
```

Run the function procedure

**Arguments**:

  -----------
  input : list of DataFrames
  Boundary conditions. If None, runs .loadInput
  

**Returns**:

  Tuple[List[DataFrame],ProcedureFunctionResults] : first element is the procedure function output (list of DataFrames), while second is a ProcedureFunctionResults object

