# Table of Contents

* [pydrodelta.downhill\_simplex](#pydrodelta.downhill_simplex)
  * [generate\_simplex](#pydrodelta.downhill_simplex.generate_simplex)
  * [centroid](#pydrodelta.downhill_simplex.centroid)
  * [DownhillSimplex](#pydrodelta.downhill_simplex.DownhillSimplex)
    * [\_\_init\_\_](#pydrodelta.downhill_simplex.DownhillSimplex.__init__)
    * [sort](#pydrodelta.downhill_simplex.DownhillSimplex.sort)
    * [reflection](#pydrodelta.downhill_simplex.DownhillSimplex.reflection)
    * [expansion](#pydrodelta.downhill_simplex.DownhillSimplex.expansion)
    * [contraction](#pydrodelta.downhill_simplex.DownhillSimplex.contraction)
    * [reduction](#pydrodelta.downhill_simplex.DownhillSimplex.reduction)
    * [limitVertex](#pydrodelta.downhill_simplex.DownhillSimplex.limitVertex)

<a id="pydrodelta.downhill_simplex"></a>

# pydrodelta.downhill\_simplex

<a id="pydrodelta.downhill_simplex.generate_simplex"></a>

#### generate\_simplex

```python
def generate_simplex(x0, step=0.1)
```

Create a simplex based at x0

<a id="pydrodelta.downhill_simplex.centroid"></a>

#### centroid

```python
def centroid(points)
```

Compute the centroid of a list points given as an array.

<a id="pydrodelta.downhill_simplex.DownhillSimplex"></a>

## DownhillSimplex Objects

```python
class DownhillSimplex(object)
```

<a id="pydrodelta.downhill_simplex.DownhillSimplex.__init__"></a>

#### \_\_init\_\_

```python
def __init__(f,
             points,
             no_improve_thr: Optional[float] = None,
             max_stagnations: Optional[int] = None,
             max_iter: Optional[int] = None,
             limit: bool = False,
             limits: List[Tuple[float, float]] = None)
```

f: (function): function to optimize, must return a scalar score 
    and operate over a numpy array of the same dimensions as x_start
points: (numpy array): initial position
no_improve_thr (float): break after max_stagnations iterations with an improvement lower than no_improv_thr
max_stagnations (int): break after max_stagnations iterations with an improvement lower than no_improv_thr
max_iter: maximum iterations
limit: if True, uses limits to limit parameter values on expansion and reflection
limits: if limit=True, use this ordered list of tuples (min, max) to limit parameter values

<a id="pydrodelta.downhill_simplex.DownhillSimplex.sort"></a>

#### sort

```python
def sort(res)
```

Order the points according to their value.

<a id="pydrodelta.downhill_simplex.DownhillSimplex.reflection"></a>

#### reflection

```python
def reflection(res, x0, refl)
```

Reflection-extension step.
refl: refl = 1 is a standard reflection

<a id="pydrodelta.downhill_simplex.DownhillSimplex.expansion"></a>

#### expansion

```python
def expansion(res, x0, ext)
```

ext: the amount of the expansion; ext=0 means no expansion

<a id="pydrodelta.downhill_simplex.DownhillSimplex.contraction"></a>

#### contraction

```python
def contraction(res, x0, cont)
```

cont: contraction parameter: should be between zero and one

<a id="pydrodelta.downhill_simplex.DownhillSimplex.reduction"></a>

#### reduction

```python
def reduction(res, red)
```

red: reduction parameter: should be between zero and one

<a id="pydrodelta.downhill_simplex.DownhillSimplex.limitVertex"></a>

#### limitVertex

```python
def limitVertex(vertex: List[float]) -> List[float]
```

Limit parameters with self.limits

**Arguments**:

- `vertex` _List[float]_ - parameter list
  

**Returns**:

- `List[float]` - limited parameter list

