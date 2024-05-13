# Table of Contents

* [pydrodelta.pydrology](#pydrodelta.pydrology)
  * [testPlot](#pydrodelta.pydrology.testPlot)
  * [shiftLeft](#pydrodelta.pydrology.shiftLeft)
  * [getDrivers](#pydrodelta.pydrology.getDrivers)
  * [makeBoundaries](#pydrodelta.pydrology.makeBoundaries)
  * [differentiate](#pydrodelta.pydrology.differentiate)
  * [integrate](#pydrodelta.pydrology.integrate)
  * [triangularDistribution](#pydrodelta.pydrology.triangularDistribution)
  * [gammaDistribution](#pydrodelta.pydrology.gammaDistribution)
  * [grXDistribution](#pydrodelta.pydrology.grXDistribution)
  * [getPulseMatrix](#pydrodelta.pydrology.getPulseMatrix)
  * [waterBalance](#pydrodelta.pydrology.waterBalance)
  * [computeEVR](#pydrodelta.pydrology.computeEVR)
  * [apportion](#pydrodelta.pydrology.apportion)
  * [curveNumberRunoff](#pydrodelta.pydrology.curveNumberRunoff)
  * [SimonovKhristoforov](#pydrodelta.pydrology.SimonovKhristoforov)
  * [RetentionReservoir](#pydrodelta.pydrology.RetentionReservoir)
    * [MaxStorage](#pydrodelta.pydrology.RetentionReservoir.MaxStorage)
    * [Inflow](#pydrodelta.pydrology.RetentionReservoir.Inflow)
    * [EVP](#pydrodelta.pydrology.RetentionReservoir.EVP)
    * [Storage](#pydrodelta.pydrology.RetentionReservoir.Storage)
    * [Runoff](#pydrodelta.pydrology.RetentionReservoir.Runoff)
    * [EV](#pydrodelta.pydrology.RetentionReservoir.EV)
    * [Proc](#pydrodelta.pydrology.RetentionReservoir.Proc)
    * [\_\_init\_\_](#pydrodelta.pydrology.RetentionReservoir.__init__)
  * [LinearReservoir](#pydrodelta.pydrology.LinearReservoir)
    * [K](#pydrodelta.pydrology.LinearReservoir.K)
    * [Inflow](#pydrodelta.pydrology.LinearReservoir.Inflow)
    * [EV](#pydrodelta.pydrology.LinearReservoir.EV)
    * [Storage](#pydrodelta.pydrology.LinearReservoir.Storage)
    * [Outflow](#pydrodelta.pydrology.LinearReservoir.Outflow)
    * [\_\_init\_\_](#pydrodelta.pydrology.LinearReservoir.__init__)
  * [ProductionStoreGR4J](#pydrodelta.pydrology.ProductionStoreGR4J)
    * [MaxSoilStorage](#pydrodelta.pydrology.ProductionStoreGR4J.MaxSoilStorage)
    * [Precipitation](#pydrodelta.pydrology.ProductionStoreGR4J.Precipitation)
    * [EVP](#pydrodelta.pydrology.ProductionStoreGR4J.EVP)
    * [SoilStorage](#pydrodelta.pydrology.ProductionStoreGR4J.SoilStorage)
    * [NetEVP](#pydrodelta.pydrology.ProductionStoreGR4J.NetEVP)
    * [EVR](#pydrodelta.pydrology.ProductionStoreGR4J.EVR)
    * [NetRainfall](#pydrodelta.pydrology.ProductionStoreGR4J.NetRainfall)
    * [Recharge](#pydrodelta.pydrology.ProductionStoreGR4J.Recharge)
    * [Infiltration](#pydrodelta.pydrology.ProductionStoreGR4J.Infiltration)
    * [Runoff](#pydrodelta.pydrology.ProductionStoreGR4J.Runoff)
    * [\_\_init\_\_](#pydrodelta.pydrology.ProductionStoreGR4J.__init__)
  * [RoutingStoreGR4J](#pydrodelta.pydrology.RoutingStoreGR4J)
    * [MaxStorage](#pydrodelta.pydrology.RoutingStoreGR4J.MaxStorage)
    * [waterExchange](#pydrodelta.pydrology.RoutingStoreGR4J.waterExchange)
    * [Inflow](#pydrodelta.pydrology.RoutingStoreGR4J.Inflow)
    * [Leakages](#pydrodelta.pydrology.RoutingStoreGR4J.Leakages)
    * [Runoff](#pydrodelta.pydrology.RoutingStoreGR4J.Runoff)
    * [Storage](#pydrodelta.pydrology.RoutingStoreGR4J.Storage)
    * [\_\_init\_\_](#pydrodelta.pydrology.RoutingStoreGR4J.__init__)
  * [SCSReservoirs](#pydrodelta.pydrology.SCSReservoirs)
    * [MaxSurfaceStorage](#pydrodelta.pydrology.SCSReservoirs.MaxSurfaceStorage)
    * [MaxStorage](#pydrodelta.pydrology.SCSReservoirs.MaxStorage)
    * [Precipitation](#pydrodelta.pydrology.SCSReservoirs.Precipitation)
    * [SurfaceStorage](#pydrodelta.pydrology.SCSReservoirs.SurfaceStorage)
    * [SoilStorage](#pydrodelta.pydrology.SCSReservoirs.SoilStorage)
    * [Runoff](#pydrodelta.pydrology.SCSReservoirs.Runoff)
    * [Infiltration](#pydrodelta.pydrology.SCSReservoirs.Infiltration)
    * [CumPrecip](#pydrodelta.pydrology.SCSReservoirs.CumPrecip)
    * [NetRainfall](#pydrodelta.pydrology.SCSReservoirs.NetRainfall)
    * [\_\_init\_\_](#pydrodelta.pydrology.SCSReservoirs.__init__)
  * [SCSReservoirsMod](#pydrodelta.pydrology.SCSReservoirsMod)
    * [MaxSurfaceStorage](#pydrodelta.pydrology.SCSReservoirsMod.MaxSurfaceStorage)
    * [MaxStorage](#pydrodelta.pydrology.SCSReservoirsMod.MaxStorage)
    * [K](#pydrodelta.pydrology.SCSReservoirsMod.K)
    * [Precipitation](#pydrodelta.pydrology.SCSReservoirsMod.Precipitation)
    * [SurfaceStorage](#pydrodelta.pydrology.SCSReservoirsMod.SurfaceStorage)
    * [SoilStorage](#pydrodelta.pydrology.SCSReservoirsMod.SoilStorage)
    * [Runoff](#pydrodelta.pydrology.SCSReservoirsMod.Runoff)
    * [Infiltration](#pydrodelta.pydrology.SCSReservoirsMod.Infiltration)
    * [CumPrecip](#pydrodelta.pydrology.SCSReservoirsMod.CumPrecip)
    * [NetRainfall](#pydrodelta.pydrology.SCSReservoirsMod.NetRainfall)
    * [BaseFlow](#pydrodelta.pydrology.SCSReservoirsMod.BaseFlow)
    * [\_\_init\_\_](#pydrodelta.pydrology.SCSReservoirsMod.__init__)
  * [LinearReservoirCascade](#pydrodelta.pydrology.LinearReservoirCascade)
    * [K](#pydrodelta.pydrology.LinearReservoirCascade.K)
    * [N](#pydrodelta.pydrology.LinearReservoirCascade.N)
    * [dt](#pydrodelta.pydrology.LinearReservoirCascade.dt)
    * [\_\_init\_\_](#pydrodelta.pydrology.LinearReservoirCascade.__init__)
  * [MuskingumChannel](#pydrodelta.pydrology.MuskingumChannel)
    * [K](#pydrodelta.pydrology.MuskingumChannel.K)
    * [X](#pydrodelta.pydrology.MuskingumChannel.X)
    * [dt](#pydrodelta.pydrology.MuskingumChannel.dt)
    * [Inflow](#pydrodelta.pydrology.MuskingumChannel.Inflow)
    * [Outflow](#pydrodelta.pydrology.MuskingumChannel.Outflow)
    * [N](#pydrodelta.pydrology.MuskingumChannel.N)
    * [M](#pydrodelta.pydrology.MuskingumChannel.M)
    * [tau](#pydrodelta.pydrology.MuskingumChannel.tau)
    * [\_\_init\_\_](#pydrodelta.pydrology.MuskingumChannel.__init__)
  * [LinearChannel](#pydrodelta.pydrology.LinearChannel)
    * [Inflow](#pydrodelta.pydrology.LinearChannel.Inflow)
    * [dt](#pydrodelta.pydrology.LinearChannel.dt)
    * [Proc](#pydrodelta.pydrology.LinearChannel.Proc)
    * [\_\_init\_\_](#pydrodelta.pydrology.LinearChannel.__init__)
  * [LinearNet](#pydrodelta.pydrology.LinearNet)
    * [pars](#pydrodelta.pydrology.LinearNet.pars)
    * [Inflows](#pydrodelta.pydrology.LinearNet.Inflows)
    * [Proc](#pydrodelta.pydrology.LinearNet.Proc)
    * [dt](#pydrodelta.pydrology.LinearNet.dt)
    * [\_\_init\_\_](#pydrodelta.pydrology.LinearNet.__init__)
  * [HOSH4P1L](#pydrodelta.pydrology.HOSH4P1L)
    * [maxSurfaceStorage](#pydrodelta.pydrology.HOSH4P1L.maxSurfaceStorage)
    * [maxSoilStorage](#pydrodelta.pydrology.HOSH4P1L.maxSoilStorage)
    * [Proc](#pydrodelta.pydrology.HOSH4P1L.Proc)
    * [Precipitation](#pydrodelta.pydrology.HOSH4P1L.Precipitation)
    * [SurfaceStorage](#pydrodelta.pydrology.HOSH4P1L.SurfaceStorage)
    * [SoilStorage](#pydrodelta.pydrology.HOSH4P1L.SoilStorage)
    * [Runoff](#pydrodelta.pydrology.HOSH4P1L.Runoff)
    * [Infiltration](#pydrodelta.pydrology.HOSH4P1L.Infiltration)
    * [CumPrecip](#pydrodelta.pydrology.HOSH4P1L.CumPrecip)
    * [NetRainfall](#pydrodelta.pydrology.HOSH4P1L.NetRainfall)
    * [EVR1](#pydrodelta.pydrology.HOSH4P1L.EVR1)
    * [EVR2](#pydrodelta.pydrology.HOSH4P1L.EVR2)
    * [Q](#pydrodelta.pydrology.HOSH4P1L.Q)
    * [\_\_init\_\_](#pydrodelta.pydrology.HOSH4P1L.__init__)
  * [HOSH4P2L](#pydrodelta.pydrology.HOSH4P2L)
    * [maxSurfaceStorage](#pydrodelta.pydrology.HOSH4P2L.maxSurfaceStorage)
    * [maxSoilStorage](#pydrodelta.pydrology.HOSH4P2L.maxSoilStorage)
    * [Proc](#pydrodelta.pydrology.HOSH4P2L.Proc)
    * [Precipitation](#pydrodelta.pydrology.HOSH4P2L.Precipitation)
    * [SurfaceStorage](#pydrodelta.pydrology.HOSH4P2L.SurfaceStorage)
    * [SoilStorage](#pydrodelta.pydrology.HOSH4P2L.SoilStorage)
    * [Runoff](#pydrodelta.pydrology.HOSH4P2L.Runoff)
    * [Infiltration](#pydrodelta.pydrology.HOSH4P2L.Infiltration)
    * [CumPrecip](#pydrodelta.pydrology.HOSH4P2L.CumPrecip)
    * [NetRainfall](#pydrodelta.pydrology.HOSH4P2L.NetRainfall)
    * [EVR1](#pydrodelta.pydrology.HOSH4P2L.EVR1)
    * [EVR2](#pydrodelta.pydrology.HOSH4P2L.EVR2)
    * [Q](#pydrodelta.pydrology.HOSH4P2L.Q)
    * [\_\_init\_\_](#pydrodelta.pydrology.HOSH4P2L.__init__)
  * [GR4J](#pydrodelta.pydrology.GR4J)
    * [Precipitation](#pydrodelta.pydrology.GR4J.Precipitation)
    * [EVP](#pydrodelta.pydrology.GR4J.EVP)
    * [Runoff](#pydrodelta.pydrology.GR4J.Runoff)
    * [Q](#pydrodelta.pydrology.GR4J.Q)
    * [\_\_init\_\_](#pydrodelta.pydrology.GR4J.__init__)

<a id="pydrodelta.pydrology"></a>

# pydrodelta.pydrology

<a id="pydrodelta.pydrology.testPlot"></a>

#### testPlot

```python
def testPlot(Inflow: Union[np.ndarray, List[float]],
             Outflow: Union[np.ndarray, List[float]])
```

Genera una gráfica de prueba comparando 2 señales

**Arguments**:

  Inflow : Union[np.ndarray,List[float]]
  Hidrograma, lista de números (float)
  Outflow : Union[np.ndarray,List[float]]
  Hidrograma, lista de números (float)

<a id="pydrodelta.pydrology.shiftLeft"></a>

#### shiftLeft

```python
def shiftLeft(array1d: Union[np.ndarray, List[float]],
              fill: float = 0) -> np.ndarray
```

Desplaza una serie hacia la izquierda (valor de índice en lista)

**Arguments**:

  array1d : Union[np.ndarray,List[float]]
  Serie numérica
  fill : float
  valor de relleno para datos nulos
  

**Returns**:

  Devuelve la lista original con el índice desplazado hacia la izquiera

<a id="pydrodelta.pydrology.getDrivers"></a>

#### getDrivers

```python
def getDrivers(file: str, tCol: str = 't') -> pd.DataFrame
```

Dummy para importar series temporales almacenadas en archivos CSV

**Arguments**:

  file : str
  ruta a archivo CSV
  tCol : str
  nombre de columna con índices temporales (fecha/hora)
  

**Returns**:

  Devuelve un dataframe python (serie temporal, indexada)

<a id="pydrodelta.pydrology.makeBoundaries"></a>

#### makeBoundaries

```python
def makeBoundaries(p: Union[List[float], np.ndarray] = [0],
                   evp: Union[List[float], np.ndarray] = [0]) -> np.ndarray
```

Dummy para generación de series de borde en modelos PQ operacionales (para cada polígono)

**Arguments**:

  p : [List[float],np.ndarray]
  serie de datos de precipitación acumulada
  evp : [List[float],np.ndarray]
  serie de datos de evapotranspiración potencial acumulada
  

**Returns**:

  Devuelve un array 2d

<a id="pydrodelta.pydrology.differentiate"></a>

#### differentiate

```python
def differentiate(lista_valores: List[float],
                  asume_initial: bool = True) -> List[float]
```

Diferencia la serie de valores

**Arguments**:

  lista_valores : List[float]
  lista de números (float)
  asume_initial : bool
  indica si el primer elemento de la lista es el valor inicial, caso contrario asume que el valor inicial es 0
  

**Returns**:

  Devuelve una lista con los valores diferenciados

<a id="pydrodelta.pydrology.integrate"></a>

#### integrate

```python
def integrate(lista_valores: List[float], dt: float) -> float
```

Integra por método del trapecio la serie de valores

**Arguments**:

  lista_valores : List[float]
  lista de números (float)
  dt : float
  longitud de paso de cómputo
  

**Returns**:

  Devuelve una lista con los valores integrados por método trapecio

<a id="pydrodelta.pydrology.triangularDistribution"></a>

#### triangularDistribution

```python
def triangularDistribution(pars: Union[List[float], float],
                           distribution: str = 'Symmetric',
                           dt: float = 0.01,
                           shift: bool = True,
                           approx: bool = True) -> np.ndarray
```

Computa Hidrogramas Unitarios Triangulares (función respuesta a pulso unitario, función de transferencia)

**Arguments**:

  pars :  Union[List[float],float]
  lista de parámetros (tiempo al pico)
  distribution : str
  tipo de distribución (simétrica, método SCS, asimétrica 'pbT')
  

**Returns**:

  Devuelve un array1d con las ordenadas del HU

<a id="pydrodelta.pydrology.gammaDistribution"></a>

#### gammaDistribution

```python
def gammaDistribution(n: float,
                      k: float,
                      dt: float = 1,
                      m: float = 10,
                      approx: bool = True,
                      shift: bool = True) -> np.ndarray
```

Computa Hidrogramas Unitarios (función respuesta a pulso unitario, función de transferencia) sobre la base de una función respuesta a impulso unitaria suponiendo n reservorios lineales en cascada con tiempo de residencia k (función de transferencia tipo gamma)

**Arguments**:

  n : float
  cantidad de reservorios en la cascada (admite números reales)
  k : float
  tiempo de residencia
  m :
  factor de tiempo de basse (longitud de base, expresada como 'mxn')
- `approx` - bool
  en caso de 'True', fuerza que la integral sea igual a 1
  shift:
  en caso de 'True', desplaza a la izquierda a las ordenadas
  

**Returns**:

  Devuelve un array1d con las ordenadas del HU

<a id="pydrodelta.pydrology.grXDistribution"></a>

#### grXDistribution

```python
def grXDistribution(T: float, distribution: str = 'SH1') -> np.ndarray
```

Computa Hidrogramas Unitarios (función respuesta a pulso unitario, función de transferencia) propuestos por SEMAGREF (GR4J, GP)

**Arguments**:

  T : float
  tiempo al pico
  distribution : str
  tipo de distribución 'SH1' corresponde a HU de 'flujo demorado', 'SH2' coresponde a HU de 'flujo rápido'
  

**Returns**:

  Devuelve un array1d con las ordenadas del HU

<a id="pydrodelta.pydrology.getPulseMatrix"></a>

#### getPulseMatrix

```python
def getPulseMatrix(inflows: Union[float, List[float], np.ndarray],
                   u: np.ndarray) -> np.ndarray
```

Computa matriz de convolución a partir de una lista o array1d de 'Inflows' (hidrograma de entrada) y sobre la base de una función de transferenciaa o HU 'u'

**Arguments**:

  Inflows : Union[float,List[float],np.ndarray]
  lista o array1d con hidrograma de entrada
  u : np.ndarray
  función de transferencia (HU)
  

**Returns**:

  Devuelve un array2d con la matriz de convolución

<a id="pydrodelta.pydrology.waterBalance"></a>

#### waterBalance

```python
def waterBalance(Storage: float = 0,
                 Inflow: float = 0,
                 Outflow: float = 0) -> float
```

Computa la ecuación de conservación del volumen (balance hídrico)

**Arguments**:

- `Storage` - float
  Almacenamiento
  Inflow : float
  Suma de entradas (en paso de cálculo)
  Outflow : float
  Suma de salidas  (en paso de cálculo)
  

**Returns**:

  Devuelve el valor inicial de almacenamiento (a fin de paso de cálculo)

<a id="pydrodelta.pydrology.computeEVR"></a>

#### computeEVR

```python
def computeEVR(P: float, EV0: float, Storage: float,
               MaxStorage: float) -> float
```

Computa la evapotranspiración real de acuerdo a las hipótesis de Thornthwaite, siguiendo la ecuación formulada por Giordano (2019)

**Arguments**:

- `Storage` - float
  Almacenamiento a inicios de paso de cálculo
- `MaxStorage` - float
  Almacenamiento máximo (parámetro del modelo)
  EV0 : float
  Evapotranspiración potencial durante paso de cálculo
  P : float
  Precipitación acumulada durante paso de cálculo
  

**Returns**:

  Devuelve el valor de la evapotranspiración real acumulada durante el paso de cálculo

<a id="pydrodelta.pydrology.apportion"></a>

#### apportion

```python
def apportion(Inflow: Union[float, List[float], np.ndarray],
              phi: float = 0.1) -> Union[float, List[float], np.ndarray]
```

Proratea un hidrograma

**Arguments**:

- `Inflow` - Union[float,List[float],np.ndarray]
  Hidorgrama de entrada

**Returns**:

  Devuelve el hidrograma prorateado

<a id="pydrodelta.pydrology.curveNumberRunoff"></a>

#### curveNumberRunoff

```python
def curveNumberRunoff(NetRainfall: float, MaxStorage: float,
                      Storage: float) -> float
```

Computa la escorrentía sobre la base de las hipótesis del método de SCS (Mockus, 1949)

**Arguments**:

  
- `Storage` - float
  Almacenamiento a inicios de paso de cálculo
  
- `MaxStorage` - float
  Almacenamiento máximo (parámetro del modelo)
  
  NetRainfall:
  Precipitación neta durante el paso de cálculo
  

**Returns**:

  Devuelve el valor de escorrentía producida durante el intervalo de cálculo

<a id="pydrodelta.pydrology.SimonovKhristoforov"></a>

#### SimonovKhristoforov

```python
def SimonovKhristoforov(sim: np.array, obs: np.ndarray) -> np.ndarray
```

Realiza correción de sesgo por simple updating (método propuesto por el Servicio Ruso)

**Arguments**:

  
- `sim` - np.ndarray
  Serie simulada o sintética
  
- `obs` - np.ndarray
  Serie observada
  

**Returns**:

  Devuelve serie simulada con correción de sesgo

<a id="pydrodelta.pydrology.RetentionReservoir"></a>

## RetentionReservoir Objects

```python
class RetentionReservoir()
```

Reservorio de Retención. Un sólo parámetro (capacidad máxima de almacenamiento). Condiciones de borde: lista con hidrograma/hietograma de entrada. Condición inicial

<a id="pydrodelta.pydrology.RetentionReservoir.MaxStorage"></a>

#### MaxStorage

Almacenamiento Máximo

<a id="pydrodelta.pydrology.RetentionReservoir.Inflow"></a>

#### Inflow

Serie de datos con hidrograma/hietograma de entrada (condición de borde)

<a id="pydrodelta.pydrology.RetentionReservoir.EVP"></a>

#### EVP

Serie de datos de evapotranspiración potencial (condición de borde)

<a id="pydrodelta.pydrology.RetentionReservoir.Storage"></a>

#### Storage

Almacenamiento a inicios de paso de cálculo (proceso computado)

<a id="pydrodelta.pydrology.RetentionReservoir.Runoff"></a>

#### Runoff

Escorrentía (proceso computado)

<a id="pydrodelta.pydrology.RetentionReservoir.EV"></a>

#### EV

Evapotranspiración real (proceso computado)

<a id="pydrodelta.pydrology.RetentionReservoir.Proc"></a>

#### Proc

Procedimiento: Abstraction o CN_h0_continuous

<a id="pydrodelta.pydrology.RetentionReservoir.__init__"></a>

#### \_\_init\_\_

```python
def __init__(pars: List[float],
             InitialConditions: List[float] = [0],
             Boundaries: List[float] = [[0], [0]],
             Proc: str = 'Abstraction')
```

pars : list
    lista con el valor de almacenamiento máximo
InitialConditions 
    lista con el valor de la condición inicial de almacenamiento
Boundaries
    lista de longitud donde cada elemento es una lista que contiene los vectores de las condiciones de border (Caudal Afluente/Precipitación y Evapotranspiración Potencial)
Proc
    Procedimiento de cómputo para escorrentía. Admite 'Abstraction' o 'CN_h0_continuous'
dt
    Longitud del paso de cómputo

<a id="pydrodelta.pydrology.LinearReservoir"></a>

## LinearReservoir Objects

```python
class LinearReservoir()
```

Reservorio Lineal. Vector pars de un sólo parámetro: Tiempo de residencia (K). Vector de Condiciones Iniciales (InitialConditions): Storage, con el cual computa Outflow. Condiciones de Borde (Boundaries): Inflow y EV.

<a id="pydrodelta.pydrology.LinearReservoir.K"></a>

#### K

Constante de Recesión

<a id="pydrodelta.pydrology.LinearReservoir.Inflow"></a>

#### Inflow

Caudal Alfuente

<a id="pydrodelta.pydrology.LinearReservoir.EV"></a>

#### EV

"Evpotranspiraciòn

<a id="pydrodelta.pydrology.LinearReservoir.Storage"></a>

#### Storage

Almacenamiento

<a id="pydrodelta.pydrology.LinearReservoir.Outflow"></a>

#### Outflow

Caudal efluente

<a id="pydrodelta.pydrology.LinearReservoir.__init__"></a>

#### \_\_init\_\_

```python
def __init__(pars: list,
             InitialConditions: list = [0],
             Boundaries: List[float] = [[0], [0]],
             Proc: str = 'Agg',
             dt: float = 1)
```

pars : List[float]
    lista con el valor del coeficiente de recesión, expresado en dt unidades
InitialConditions : list 
    lista con el valor de la condición inicial de almacenamiento
Boundaries : List[float]
    lista de longitud 2 donde cada elemento es una lista que contiene los vectores de las condiciones de borde (Caudal Afluente y Evapotranspiración Potencial)
Proc : str
    Procedimiento de cómputo. Admite 'Agg' (Valor Agregado), 'API' o 'Instant' (Valor Instantáneo)
dt : float
    Longitud del paso de cómputo

<a id="pydrodelta.pydrology.ProductionStoreGR4J"></a>

## ProductionStoreGR4J Objects

```python
class ProductionStoreGR4J()
```

Reservorio de Producción de Escorrentía modelo GR4J

<a id="pydrodelta.pydrology.ProductionStoreGR4J.MaxSoilStorage"></a>

#### MaxSoilStorage

Almacenamiento Máximo en Perfil de Suelo

<a id="pydrodelta.pydrology.ProductionStoreGR4J.Precipitation"></a>

#### Precipitation

Precipitación (serie temporal)

<a id="pydrodelta.pydrology.ProductionStoreGR4J.EVP"></a>

#### EVP

Evapotranspiración potencial (serie temporal)

<a id="pydrodelta.pydrology.ProductionStoreGR4J.SoilStorage"></a>

#### SoilStorage

Almacenamiento en Perfil de Suelo (serie temporal)

<a id="pydrodelta.pydrology.ProductionStoreGR4J.NetEVP"></a>

#### NetEVP

Evapotranspiración Potencial Neta (serie temporal)

<a id="pydrodelta.pydrology.ProductionStoreGR4J.EVR"></a>

#### EVR

Evapotranspiración Real (serie temporal)

<a id="pydrodelta.pydrology.ProductionStoreGR4J.NetRainfall"></a>

#### NetRainfall

Precipitación Neta (serie temporal)

<a id="pydrodelta.pydrology.ProductionStoreGR4J.Recharge"></a>

#### Recharge

Transferencia vertical: Pérdidas por recarga de flujo demorado (serie temporal)

<a id="pydrodelta.pydrology.ProductionStoreGR4J.Infiltration"></a>

#### Infiltration

Ingresos Netos al reservorio por Infiltración (serie temporal)

<a id="pydrodelta.pydrology.ProductionStoreGR4J.Runoff"></a>

#### Runoff

Transferencia horizontal: Pérdidas por flujo directo (serie temporal)

<a id="pydrodelta.pydrology.ProductionStoreGR4J.__init__"></a>

#### \_\_init\_\_

```python
def __init__(pars: list,
             InitialConditions: float = 0,
             Boundaries: List[float] = [[0], [0]])
```

pars : list
    lista con el valor de almacenamiento máximo
InitialConditions : float
    lista con el valor de la condición inicial de almacenamiento
Boundaries : List[float]
    lista de longitud 2 donde cada elemento es una lista que contiene los vectores de las condiciones de borde (Precipitación y Evapotranspiración Potencial)

<a id="pydrodelta.pydrology.RoutingStoreGR4J"></a>

## RoutingStoreGR4J Objects

```python
class RoutingStoreGR4J()
```

Reservorio de Propagación de Escorrentía modelo GR4J

<a id="pydrodelta.pydrology.RoutingStoreGR4J.MaxStorage"></a>

#### MaxStorage

Almacenamiento Máximo

<a id="pydrodelta.pydrology.RoutingStoreGR4J.waterExchange"></a>

#### waterExchange

Coeficiente de trasvase

<a id="pydrodelta.pydrology.RoutingStoreGR4J.Inflow"></a>

#### Inflow

Recarga del reservorio (serie temporal)

<a id="pydrodelta.pydrology.RoutingStoreGR4J.Leakages"></a>

#### Leakages

trasvase (serie temporal)

<a id="pydrodelta.pydrology.RoutingStoreGR4J.Runoff"></a>

#### Runoff

Transferencia horizontal : pérdidas por flujo demorado

<a id="pydrodelta.pydrology.RoutingStoreGR4J.Storage"></a>

#### Storage

Almacenamiento

<a id="pydrodelta.pydrology.RoutingStoreGR4J.__init__"></a>

#### \_\_init\_\_

```python
def __init__(pars: Union[List[float], List[Tuple[float, float]]],
             InitialConditions: float = 0,
             Boundaries: List[float] = [0])
```

pars : Union[List[float],List[Tuple[float,float]]]
    lista con los valores de almacenamiento máximo (obligatorio) y del coeficiente de trasvase (opcional/puede omitirse, en cuyo caso se asigna el valor 0)
InitialConditions 
    lista con el valor de la condición inicial de almacenamiento 
Boundaries
    lista con el vector de la condición de borde (serie temporal de recarga de flujo demorado)

<a id="pydrodelta.pydrology.SCSReservoirs"></a>

## SCSReservoirs Objects

```python
class SCSReservoirs()
```

Sistema de 2 reservorios de retención (intercepción/abstracción superficial y retención en perfil de suelo - i.e. capacidad de campo-), con función de cómputo de escorrentía siguiendo el método propuesto por el Soil Conservation Service. Lista pars de dos parámetros: Máximo Almacenamiento Superficial (Abstraction) y Máximo Almacenamiento por Retención en Perfil de Suelo (MaxStorage). Condiciones iniciales: Almacenamiento Superficial y Almacenamiento en Perfil de Suelo (lista de valores). Condiciones de Borde: Hietograma (lista de valores).

<a id="pydrodelta.pydrology.SCSReservoirs.MaxSurfaceStorage"></a>

#### MaxSurfaceStorage

Almacenamiento Máximo en reservorio de retención

<a id="pydrodelta.pydrology.SCSReservoirs.MaxStorage"></a>

#### MaxStorage

Almacenamiento Máximo en reservorio de producción

<a id="pydrodelta.pydrology.SCSReservoirs.Precipitation"></a>

#### Precipitation

Precipitación (serie temporal)

<a id="pydrodelta.pydrology.SCSReservoirs.SurfaceStorage"></a>

#### SurfaceStorage

Almacenamiento en reservorio de retención (serie temporal)

<a id="pydrodelta.pydrology.SCSReservoirs.SoilStorage"></a>

#### SoilStorage

Almacenamiento en resservorio de producción (sserie temporal)

<a id="pydrodelta.pydrology.SCSReservoirs.Runoff"></a>

#### Runoff

Transferencia horizontal: escorrentía total (serie temporal)

<a id="pydrodelta.pydrology.SCSReservoirs.Infiltration"></a>

#### Infiltration

Recarga de reservorio de producción (serie temporal)

<a id="pydrodelta.pydrology.SCSReservoirs.CumPrecip"></a>

#### CumPrecip

Precipitación acumulada durante el evento (serie temporal)

<a id="pydrodelta.pydrology.SCSReservoirs.NetRainfall"></a>

#### NetRainfall

Precipitación neta (serie temporal)

<a id="pydrodelta.pydrology.SCSReservoirs.__init__"></a>

#### \_\_init\_\_

```python
def __init__(pars: Union[List[float], List[Tuple[float, float]]],
             InitialConditions: Union[List[float],
                                      List[Tuple[float, float]]] = [0, 0],
             Boundaries: List[float] = [0])
```

pars : Union[List[float],List[Tuple[float,float]]]
    lista con los valores de almacenamiento máximo (reservorio de retención y reservorio de producción) y con el valor del coeficiente de recesión (flujo demorado) 
InitialConditions : Union[List[float],List[Tuple[float,float]]]
    lista de longitud 2 con el valor de la condición inicial de almacenamiento en cada reservorio
Boundaries : List[float]
    lista con el vector de la condición de borde (serie temporal de precipitación)

<a id="pydrodelta.pydrology.SCSReservoirsMod"></a>

## SCSReservoirsMod Objects

```python
class SCSReservoirsMod()
```

Sistema de 2 reservorios de retención+detención (una capa de abstracción superficial/suelo y otra capa de retención/detención en resto perfil de suelo), con función de cómputo de escorrentía siguiendo el método propuesto por el Soil Conservation Service y añadiendo pérdida continua por flujo de base (primario). Lista pars de 3 parámetros: Máxima Abtracción por retención (Abstraction) y Máximo Almacenamiento por Retención+Detención en Perfil de Suelo (MaxStorage) y coefiente de pérdida K. Se añade pérdida continua. Condiciones iniciales: Almacenamiento Superficial y Almacenamiento en Perfil de Suelo (lista de valores). Condiciones de Borde: Hietograma (lista de valores).

<a id="pydrodelta.pydrology.SCSReservoirsMod.MaxSurfaceStorage"></a>

#### MaxSurfaceStorage

Almacenamiento Máximo en reservorio de retención

<a id="pydrodelta.pydrology.SCSReservoirsMod.MaxStorage"></a>

#### MaxStorage

Almacenamiento Máximo en reservorio de producción

<a id="pydrodelta.pydrology.SCSReservoirsMod.K"></a>

#### K

Coeficiente de recesión (autovalor dominante del sistema reservorio de produccción)

<a id="pydrodelta.pydrology.SCSReservoirsMod.Precipitation"></a>

#### Precipitation

Precipitación (serie temporal)

<a id="pydrodelta.pydrology.SCSReservoirsMod.SurfaceStorage"></a>

#### SurfaceStorage

Almacenamiento en reservorio de retención (serie temporal)

<a id="pydrodelta.pydrology.SCSReservoirsMod.SoilStorage"></a>

#### SoilStorage

Almacenamiento en resservorio de producción (sserie temporal)

<a id="pydrodelta.pydrology.SCSReservoirsMod.Runoff"></a>

#### Runoff

Transferencia horizontal: flujo directo (serie temporal)

<a id="pydrodelta.pydrology.SCSReservoirsMod.Infiltration"></a>

#### Infiltration

Recarga de reservorio de producción (serie temporal)

<a id="pydrodelta.pydrology.SCSReservoirsMod.CumPrecip"></a>

#### CumPrecip

Precipitación acumulada durante el evento (serie temporal)

<a id="pydrodelta.pydrology.SCSReservoirsMod.NetRainfall"></a>

#### NetRainfall

Precipitación neta (serie temporal)

<a id="pydrodelta.pydrology.SCSReservoirsMod.BaseFlow"></a>

#### BaseFlow

Transferencia vertical: recarga de flujo demorado (serie temporal)

<a id="pydrodelta.pydrology.SCSReservoirsMod.__init__"></a>

#### \_\_init\_\_

```python
def __init__(pars: Union[List[float], List[Tuple[float, float]]],
             InitialConditions: Union[List[float],
                                      List[Tuple[float, float]]] = [0, 0],
             Boundaries: List[float] = [0])
```

pars : Union[List[float],List[Tuple[float,float]]]
    lista con los valores de almacenamiento máximo (reservorio de retención y reservorio de producción) y con el valor del coeficiente de recesión (flujo demorado) 
InitialConditions : Union[List[float],List[Tuple[float,float]]]
    lista de longitud 2 con el valor de la condición inicial de almacenamiento en cada reservorio
Boundaries : List[float]
    lista con el vector de la condición de borde (serie temporal de precipitación)

<a id="pydrodelta.pydrology.LinearReservoirCascade"></a>

## LinearReservoirCascade Objects

```python
class LinearReservoirCascade()
```

Cascada de Reservorios Lineales (Discreta). Lista pars de dos parámetros: Tiempo de Residencia (K) y Número de Reservorios (N). Vector de Condiciones Iniciales (InitialConditions): Si es un escalar (debe ingresarse como elemento de lista) genera una matriz de 2xN con valor constante igual al escalar, también puede ingresarse una matriz de 2XN que represente el caudal inicial en cada reservorio de la cascada. Condiciones de Borde (Boundaries): vector Inflow.

<a id="pydrodelta.pydrology.LinearReservoirCascade.K"></a>

#### K

Tiempo de residencia en reservorio

<a id="pydrodelta.pydrology.LinearReservoirCascade.N"></a>

#### N

Número de reservorios en cascada

<a id="pydrodelta.pydrology.LinearReservoirCascade.dt"></a>

#### dt

Longitud del paso de cálculo

<a id="pydrodelta.pydrology.LinearReservoirCascade.__init__"></a>

#### \_\_init\_\_

```python
def __init__(pars: Union[List[float], List[Tuple[float, float]]],
             Boundaries: List[float] = [0],
             InitialConditions: List[float] = [0],
             dt=1)
```

pars : Union[List[float],List[Tuple[float,float]]]
    lista con los valores del tiempo de residencia y de la cantidad de reservorios lineales en cascada 
InitialConditions : List [float]
    lista con el valor de la condición inicial de almacenamiento en cada reservorio (puede brindarse un valor solamente, común a todos los reservorios, por defecto si se omite este es igual a 0)
Boundaries : List[float]
    lista con el vector de la condición de borde (serie temporal de caudal afluente)

<a id="pydrodelta.pydrology.MuskingumChannel"></a>

## MuskingumChannel Objects

```python
class MuskingumChannel()
```

Método de tránsito hidrológico de la Oficina del río Muskingum. Lista pars de dos parámetros: Tiempo de Tránsito (K) y Factor de forma (X). Condiciones Iniciales (InitialConditions): lista con array de condiciones iniciales o valor escalar constante. Condiciones de borde: lista con hidrograma en nodo superior de tramo. A fin de mantener condiciones de estabilidad numérica en la propagación (conservar volumen), sobre la base de la restricción 2KX<=dt<=2K(1-X) (Chin,2000) y como dt viene fijo por la condición de borde (e.g. por defecto 'una unidad') y además se pretende respetar el valor de K, se propone incrementar la resolución espacial dividiendo el tramo en N' subtramos de igual longitud, con tiempo de residencia mínimo T'=K/N', para el caso dt<2KX (frecuencia de muestreo demasiado alta). Así para obtener el valor N', se aplica el criterio de Chin estableciendo que el valor crítico debe satisfacer dt=uT', específicamente con u=2X y T' = K/N'--> N'=2KX/dt. Al mismo tiempo si dt>2K(1-X) (frecuencia de muestreo demasiado baja), el paso de cálculo se subdivide en M subpasos de longitud dT=2K(1-X) de forma tal que dT/dt=dv y M=dt/dv. El atributo self.tau resultante especifica el subpaso de cálculo (siendo self.M la cantidad de subintervalos utilizados) y self.N la cantidad de subtramos.

<a id="pydrodelta.pydrology.MuskingumChannel.K"></a>

#### K

Tiempo de tránsito, parámetro del modelo

<a id="pydrodelta.pydrology.MuskingumChannel.X"></a>

#### X

Factor de forma, parámetro del modelo

<a id="pydrodelta.pydrology.MuskingumChannel.dt"></a>

#### dt

Longitud del paso de cálculo

<a id="pydrodelta.pydrology.MuskingumChannel.Inflow"></a>

#### Inflow

"Hidrogama de ingresos al tramo (serie temporal)

<a id="pydrodelta.pydrology.MuskingumChannel.Outflow"></a>

#### Outflow

Hidrograma de descragas del tramo (serie temporal)

<a id="pydrodelta.pydrology.MuskingumChannel.N"></a>

#### N

Cantidad de subtramos en tramo

<a id="pydrodelta.pydrology.MuskingumChannel.M"></a>

#### M

Cantidad de subpasos de cálculo en paso

<a id="pydrodelta.pydrology.MuskingumChannel.tau"></a>

#### tau

Longitud de subpaso de cómputo

<a id="pydrodelta.pydrology.MuskingumChannel.__init__"></a>

#### \_\_init\_\_

```python
def __init__(pars: List[float],
             Boundaries: List[float] = [0],
             InitialConditions: List[float] = [0],
             dt: float = 1)
```

pars : List[float]
    lista con los valores del tiempo de tránsito (K) y del factor de forma (X) 
InitialConditions : List [float]
    lista con el valor de la condición inicial de almacenamiento en tramo 
Boundaries : List[float]
    lista con el hidrograma de entrada, de resolución dt
dt : float
    resolución del hidrograma de entrada, por defecto se establece en la unidad

<a id="pydrodelta.pydrology.LinearChannel"></a>

## LinearChannel Objects

```python
class LinearChannel()
```

Método de tránsito hidrológico implementado sobre la base de teoría de sistemas lineales. Así, considera al tránsito de energía, materia o información como un proceso lineal desde un nodo superior hacia un nodo inferior. Específicamente, sea I=[I1,I2,...,IN] el vector de pulsos generados por el borde superior y U=[U1,U2,..,UM] una función de distribución que representa el prorateo de un pulso unitario durante el tránsito desde un nodo superior (borde) hacia un nodo inferior (salida), el sistema opera aplicando las propiedades de proporcionalidad y aditividad, de manera tal que es posible propagar cada pulso a partir de U y luego mediante la suma de estos prorateos obtener el aporte de este tránsito sobre el nodo inferior (convolución).

<a id="pydrodelta.pydrology.LinearChannel.Inflow"></a>

#### Inflow

Hidrograma de entrada (serie temporal)

<a id="pydrodelta.pydrology.LinearChannel.dt"></a>

#### dt

Longitud de paso de cálculo

<a id="pydrodelta.pydrology.LinearChannel.Proc"></a>

#### Proc

Tipo de Procedimiento. Admite 'Nash' (cascada de reservorios lineales, debe proveerse lista de pars k y n) y 'UH' (Hidrograma Unitario, debe proveerse lista con array conteniendo ordenadas de UH a paso dt)

<a id="pydrodelta.pydrology.LinearChannel.__init__"></a>

#### \_\_init\_\_

```python
def __init__(pars: Union[List[Tuple[float, float]], List[float], np.ndarray],
             Boundaries: List[float] = [0],
             Proc: str = 'Nash',
             dt: float = 1)
```

pars : Union[List[Tuple[float,float]],List[float],np.ndarray]
    Lista de flotantes o tuplas con los valores del tiempo de residencia (k) y número de reservorios (n), en caso que Proc='Nash', o lista, tupla o array con ordenadas de Hidrograma Unitario, en caso que  Proc='UH'
InitialConditions : List [float]
    Lista  con el valor de la condición inicial de almacenamiento en tramo 
Boundaries : List[float]
    Lista con el hidrograma de entrada, de resolución dt
dt : float
    Resolución del hidrograma de entrada, por defecto se establece en la unidad
Proc: str
    Procedimiento para transferencia: 'Nash' (cascada de Nash, debe proveerse k y n) y 'UH' (Hidrograma Unitario, lista, tupla o array con valoress de ordenadass)

<a id="pydrodelta.pydrology.LinearNet"></a>

## LinearNet Objects

```python
class LinearNet()
```

Método de tránsito hidrológico implementado sobre la base de teoría de sistemas lineales. Así, considera al tránsito de energía, materia o información como un proceso lineal desde N nodos superiores hacia un nodo inferior. Específicamente, sea I=[I1,I2,...,IN] un vector de pulsos generados por un borde y U=[U1,U2,..,UM] una función de distribución que representa el prorateo de un pulso unitario durante el tránsito desde un nodo superior (borde) hacia un nodo inferior (salida), aplicando las propiedades de proporcionalidad y aditividad es posible propagar cada pulso a partir de U y luego mediante su suma obtener el aporte de este tránsito sobre el nodo inferior, mediante convolución. Numéricamente el sistema se representa como una transformación matricial (matriz de pulsos*u=vector de aportes). Consecuentemente, el tránsito se realiza para cada borde y la suma total de estos tránsitos constituye la señal transitada sobre el nodo inferior.  Condiciones de borde: array 2D con hidrogramas en nodos superiores del tramo, por columna. Parámetros: función de distribución (proc='UH') o tiempo de residencia (k) y número de reservorios (n), si se desea utilizar el método de hidrograma unitario de Nash (proc='Nash'), pars es un array bidimensional en donde la información necesaria para cada nodo se presenta por fila (parámetros de nodo). El parámetro dt refiere a la longitud de paso de cálculo para el método de integración, siendo dt=1 la resolución nativa de los hidrogramas de entrada provistos. Importante, las funciones de transferencia deben tener la misma cantidad de ordenadas (dimensión del vector)

<a id="pydrodelta.pydrology.LinearNet.pars"></a>

#### pars

Matriz con parámetros de propagación (j-vectores fila)

<a id="pydrodelta.pydrology.LinearNet.Inflows"></a>

#### Inflows

Matriz con hidrogramas de entrada (j-vectores columna)

<a id="pydrodelta.pydrology.LinearNet.Proc"></a>

#### Proc

Procedimiento, admite 'Nash' y 'UH'

<a id="pydrodelta.pydrology.LinearNet.dt"></a>

#### dt

Longitud del paso de cómputo

<a id="pydrodelta.pydrology.LinearNet.__init__"></a>

#### \_\_init\_\_

```python
def __init__(pars: Union[List[Tuple[float, float]], List[float], np.ndarray],
             Boundaries: Union[List[float], np.ndarray],
             Proc: str = 'Nash',
             dt: float = 1)
```

pars : List[Tuple[float,float],float,np.ndarray]
    Lista de tuplas o de longitud 2 con los valores del tiempo de residencia (k) y número de reservorios (n), en caso que Proc='Nash', o array con ordenadas de cada Hidrograma Unitario, en caso que  Proc='UH', para cada nodo de entrada
Boundaries : Union[List[float],np.ndarray]
    Lista de longitud j o array con los hidrogramas de los nodos de entrada, ordenados como j-vectores columna 
dt : float
    Resolución del hidrograma de entrada, por defecto se establece en la unidad
Proc: str
    Procedimiento para transferencia: 'Nash' (cascada de Nash, debe proveerse k y n) o 'UH' (Hidrogramas Unitarios, array con j-vectores fila con valores de ordenadas)

<a id="pydrodelta.pydrology.HOSH4P1L"></a>

## HOSH4P1L Objects

```python
class HOSH4P1L()
```

Modelo Operacional de Transformación de Precipitación en Escorrentía de 4 parámetros (estimables). Hidrología Operativa Síntesis de Hidrograma. Método NRCS, perfil de suelo con 2 reservorios de retención (sin efecto de base). Rutina de propagación por 'UH' arbitario (e.g. generado por triangularDistributon) o por función de transsferencia gamma.

<a id="pydrodelta.pydrology.HOSH4P1L.maxSurfaceStorage"></a>

#### maxSurfaceStorage

Almacenamiento Máximo Superficial (reservorio de retención)

<a id="pydrodelta.pydrology.HOSH4P1L.maxSoilStorage"></a>

#### maxSoilStorage

Almacenamiento máximo en el Suelo (reservorio de producción)

<a id="pydrodelta.pydrology.HOSH4P1L.Proc"></a>

#### Proc

Procedimiento de propagación ('Nash' o 'UH')

<a id="pydrodelta.pydrology.HOSH4P1L.Precipitation"></a>

#### Precipitation

Precipitación (serie temporal)

<a id="pydrodelta.pydrology.HOSH4P1L.SurfaceStorage"></a>

#### SurfaceStorage

Almacenamiento en reservorio de retención (serie temporal)

<a id="pydrodelta.pydrology.HOSH4P1L.SoilStorage"></a>

#### SoilStorage

Almacenamiento en resservorio de producción (sserie temporal)

<a id="pydrodelta.pydrology.HOSH4P1L.Runoff"></a>

#### Runoff

Transferencia horizontal: escorrentía total (serie temporal)

<a id="pydrodelta.pydrology.HOSH4P1L.Infiltration"></a>

#### Infiltration

Recarga de reservorio de producción (serie temporal)

<a id="pydrodelta.pydrology.HOSH4P1L.CumPrecip"></a>

#### CumPrecip

Precipitación acumulada durante el evento (serie temporal)

<a id="pydrodelta.pydrology.HOSH4P1L.NetRainfall"></a>

#### NetRainfall

Precipitación neta (serie temporal)

<a id="pydrodelta.pydrology.HOSH4P1L.EVR1"></a>

#### EVR1

Evapotranspiración real reservorio de abstracción

<a id="pydrodelta.pydrology.HOSH4P1L.EVR2"></a>

#### EVR2

Evapotranspiración real reservorio de producción

<a id="pydrodelta.pydrology.HOSH4P1L.Q"></a>

#### Q

Flujo encauzado (serie temporal)

<a id="pydrodelta.pydrology.HOSH4P1L.__init__"></a>

#### \_\_init\_\_

```python
def __init__(pars: Union[List[Tuple[float, float]], List[float], np.ndarray],
             Boundaries: Union[List[float], np.ndarray] = [[0], [0]],
             InitialConditions: Union[List[Tuple[float, float]],
                                      List[float]] = [0, 0],
             Proc: str = 'Nash')
```

pars : List[Tuple[float,float],float,np.ndarray]
    Lista con los valores de maxSurFaceStorage (reservorio de abstracción), maxSoilStorage (reservorio de producción) y parámetros tiempo de residencia (k) y n reservorios (caso Proc='Nash') o con lista,tupla o array con ordenadas de Hidrograma Unitario (caso Proc='UH') 
Boundaries : Union[List[float],np.ndarray]
    Lista o array2d compuesto por vectores (columna) de precipitación y evapotranspiración potencial (condiciones de borde) 
InitialConditions : Union[List[Tuple[float,float]],List[float]]
    Lista o array1d con valores de almacenamiento inicial en reservorio de abstracción y en reservorio de producción
Proc: str
    Procedimiento para transferencia: 'Nash' (cascada de Nash, debe proveerse k y n) o 'UH' (Hidrogramas Unitarios, array con j-vectores fila con valores de ordenadas)

<a id="pydrodelta.pydrology.HOSH4P2L"></a>

## HOSH4P2L Objects

```python
class HOSH4P2L()
```

Modelo Operacional de Transformación de Precipitación en Escorrentía de 4/6 parámetros (estimables), con 2 capas de suelo. Hidrología Operativa Síntesis de Hidrograma. Método NRCS, perfil de suelo con 2 reservorios de retención (zona superior) y un reservorio linear (zona inferior). Rutea utilizando una función respuesta de pulso unitario arbitraria o mediante na cascada de Nash (se debe especificar tiempo de residencia y número de reservorios)

<a id="pydrodelta.pydrology.HOSH4P2L.maxSurfaceStorage"></a>

#### maxSurfaceStorage

Almacenamiento Máximo Superficial (reservorio de retención)

<a id="pydrodelta.pydrology.HOSH4P2L.maxSoilStorage"></a>

#### maxSoilStorage

Almacenamiento máximo en el Suelo (reservorio de producción)

<a id="pydrodelta.pydrology.HOSH4P2L.Proc"></a>

#### Proc

Procedimiento de propagación ('Nash' o 'UH')

<a id="pydrodelta.pydrology.HOSH4P2L.Precipitation"></a>

#### Precipitation

Precipitación (serie temporal)

<a id="pydrodelta.pydrology.HOSH4P2L.SurfaceStorage"></a>

#### SurfaceStorage

Almacenamiento en reservorio de retención (serie temporal)

<a id="pydrodelta.pydrology.HOSH4P2L.SoilStorage"></a>

#### SoilStorage

Almacenamiento en resservorio de producción (sserie temporal)

<a id="pydrodelta.pydrology.HOSH4P2L.Runoff"></a>

#### Runoff

Transferencia horizontal: escorrentía total (serie temporal)

<a id="pydrodelta.pydrology.HOSH4P2L.Infiltration"></a>

#### Infiltration

Recarga de reservorio de producción (serie temporal)

<a id="pydrodelta.pydrology.HOSH4P2L.CumPrecip"></a>

#### CumPrecip

Precipitación acumulada durante el evento (serie temporal)

<a id="pydrodelta.pydrology.HOSH4P2L.NetRainfall"></a>

#### NetRainfall

Precipitación neta (serie temporal)

<a id="pydrodelta.pydrology.HOSH4P2L.EVR1"></a>

#### EVR1

Evapotranspiración real reservorio de abstracción

<a id="pydrodelta.pydrology.HOSH4P2L.EVR2"></a>

#### EVR2

Evapotranspiración real reservorio de producción

<a id="pydrodelta.pydrology.HOSH4P2L.Q"></a>

#### Q

Flujo encauzado (serie temporal)

<a id="pydrodelta.pydrology.HOSH4P2L.__init__"></a>

#### \_\_init\_\_

```python
def __init__(pars: Union[List[Tuple[float, float]], List[float], np.ndarray],
             Boundaries: Union[List[float], np.ndarray] = [[0], [0]],
             InitialConditions: Union[List[Tuple[float, float]],
                                      List[float]] = [0, 0],
             Proc: str = 'Nash')
```

pars : List[Tuple[float,float],float,np.ndarray]
    Lista con los valores de maxSurFaceStorage (reservorio de abstracción), maxSoilStorage (reservorio de producción), coeficiente de prorateo (flujo directo/flujo demorado, phi), coeficiente de recesión (autovalor, kb) y parámetros tiempo de residencia (k) y n reservorios (caso Proc='Nash') o con lista,tupla o array con ordenadas de Hidrograma Unitario (caso Proc='UH') 
Boundaries : Union[List[float],np.ndarray]
    Lista o array2d compuesto por vectores (columna) de precipitación y evapotranspiración potencial (condiciones de borde) 
InitialConditions : Union[List[Tuple[float,float]],List[float]]
    Lista o array1d con valores de almacenamiento inicial en reservorio de abstracción y en reservorio de producción
Proc: str
    Procedimiento para transferencia: 'Nash' (cascada de Nash, debe proveerse k y n) o 'UH' (Hidrogramas Unitarios, array con j-vectores fila con valores de ordenadas)

<a id="pydrodelta.pydrology.GR4J"></a>

## GR4J Objects

```python
class GR4J()
```

Modelo Operacional de Transformación de Precipitación en Escorrentía de Ingeniería Rural de 4 parámetros (CEMAGREF). A diferencia de la versión original, la convolución se realiza mediante producto de matrices. Parámetros: Máximo almacenamiento en reservorio de producción, tiempo al pico (hidrograma unitario),máximo almacenamiento en reservorio de propagación, coeficiente de intercambio.

<a id="pydrodelta.pydrology.GR4J.Precipitation"></a>

#### Precipitation

Precipitación (serie temporal)

<a id="pydrodelta.pydrology.GR4J.EVP"></a>

#### EVP

Evapotranspiración (serie temporal)

<a id="pydrodelta.pydrology.GR4J.Runoff"></a>

#### Runoff

Escorentía reservorio de producción (serie temporal)

<a id="pydrodelta.pydrology.GR4J.Q"></a>

#### Q

Flujo encauzado (serie temporal)

<a id="pydrodelta.pydrology.GR4J.__init__"></a>

#### \_\_init\_\_

```python
def __init__(pars: Union[List[float], tuple],
             Boundaries: Union[List[float], np.ndarray] = [[0], [0]],
             InitialConditions: Union[List[Tuple[float, float]],
                                      List[float]] = [0, 0],
             Proc='CEMAGREF SH')
```

pars : Union[List[float],tuple]
    Lista o tupla con los valores de Almacenamiento Máximo en Reservorio de Producción, Tiempo al pico , Almacenamiento Máximo en Reservorio de Tránsito y coeficiente de intercambio o fugas 
Boundaries : Union[List[float],np.ndarray]
    Lista o array2d compuesto por vectores (columna) de precipitación y evapotranspiración potencial (condiciones de borde) 
InitialConditions : Union[List[Tuple[float,float]],List[float]]
    Lista o array1d con valores de almacenamiento inicial en reservorio de producción y en reservorio de tránsito

