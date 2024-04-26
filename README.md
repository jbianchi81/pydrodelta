## pydrodelta

módulo generación de análisis de series temporales

- se definen las clases NodeSerie, Node y Topology
- se define un esquema json (jsonschema) para validar la configuración de la topología (data/schemas/topology.json)
- se instancia un objeto de la clase Topology usando el archivo json de configuración y:
- lee series de entrada de a5 topology.loadData()
- regulariza las series topology.regularize()
- rellena nulos topology.fillNulls()
- guarda observaciones en archivo csv o json topology.saveData()
- guarda observaciones en a5 topology.uploadData() 

módulo simulación

- se definen las clases Plan, Procedure y clases para cada procedimiento específico
- se define un esquema json (jsonschema) para validar la configuración del plan (data/schemas/plan.json) 
- se instancia un objeto de la clase Plan usando el archivo de configuración, y:
- ejecuta el análisis de la topología del plan (generación de condiciones de borde, plan.topology.batchProcessInput())
- ejecuta secuencialmente los procedimientos (procedure.run() por cada procedure en plan.procedures)

### Description

La aplicación lee un archivo de entrada .json que define con qué armar las series, de acuerdo al esquema definido acá: https://github.com/jbianchi81/pydrodelta/blob/main/schemas/topology.json . Por ejemplo, para el modelo Hidrodelta el archivo de entrada es así: https://github.com/jbianchi81/pydrodelta/blob/main/pydrodelta_config/288_bordes_curados.json . Básicamente, el esquema define una topología que contiene 1..n nodos, cada uno de los cuales 1..n series. También se pueden definir nodos derivados allí donde no hay observaciones, copiando o interpolando otros nodos. Luego de descargar de la base de datos, curar y regularizar las series, los datos faltantes de la primera serie se completan con los de las subsiguientes, para dar una serie resultante por nodo. Luego se calculan los nodos derivados y finalmente se exportan las series a .csv, .json y/o se cargan a la base de datos.

### installation

    git clone https://github.com/jbianchi81/pydrodelta.git pydrodelta
    cd pydrodelta
    python3 -m venv myenv
    source myenv/bin/activate
    python3 -m pip install -r requirements.txt
    python3 -m pip install .
    export PYDRODELTA_DIR=$PWD
    cp config/config_empty.yml config/config.yml
    nano config/config.yml # <- insert api connection parameters

### test installation

    myenv/bin/python3
    >>> from pydrodelta.a5 import Crud
    >>> crud = Crud({"url":"https://alerta.ina.gob.ar/test","token":"my_token"})
    >>> series = crud.readSeries()

### tested with

- **OS**
    - Ubuntu 18.04.6 LTS
    - Ubuntu 22.04.3 LTS
- **python**: 
    - 3.8.15
    - 3.10.12 

### use examples

#### a5 api series to/from dataframe

    import pydrodelta.a5 as a5
    # instancia cliente de la api
    crud = a5.Crud({"url":"https://alerta.ina.gob.ar/a5","token":"my_token"})
    # lee serie de api a5
    serie = crud.readSerie(26497,"2022-05-25T03:00:00Z","2022-06-01T03:00:00Z")
    # convierte observaciones a dataframe 
    obs_df = a5.observacionesListToDataFrame(serie["observaciones"]) 
    # convierte de dataframe a lista de dict
    obs_list = a5.observacionesDataFrameToList(obs_df,series_id=serie["id"])
    # valida observaciones
    for x in obs_list:
        a5.validate(x,"Observacion")
    # sube observaciones a la api a5 (requiere credenciales)
    upserted = crud.createObservaciones(obs_df,series_id=serie["id"])

#### python api analysis de series temporales

    import pydrodelta.analysis
    import json

    t_config = json.load(open("pydrodelta_config/288_bordes_curados.json"))
    topology = pydrodelta.analysis.Topology(t_config])
    topology.loadData()
    topology.regularize()
    topology.fillNulls()
    # csv = topology.toCSV()
    topology.saveData("bordes_288.csv",pivot=True)
    topology.saveData("bordes_288.json","json")
    topology.uploadData()

#### python api simulation

    import pydrodelta.simulation
    import json

    plan_config = json.load(open("../data/plans/gualeguay_rt_dummy.json"))
    plan = pydrodelta.simulation.Plan(plan_config)
    plan.execute()

#### CLI

    source bin/activate
    
    export PYDRODELTA_DIR=$PWD

    # dummy run from csv data. Outputs json and pivot csv
    pydrodelta run-plan sample_data/plans/from_csv.yml -e results/from_csv.json -E tmp/from_csv.csv -p

    # Transit between 2 nodes
    pydrodelta run-plan sample_data/plans/linear_channel_dummy.yml -a  results/linear_channel_dummy_analysis.json -e results/linear_channel_dummy_simulation.json -g results/linear_channel_dummy.png

    # P-Q transformation, load data from csv. Print plot of Q observed vs. simulated
    pydrodelta run-plan sample_data/plans/dummy_grp_from_csv_one_node.yml -V 4 results/grp_dummy_q.pdf

    # P-Q transformation, load data from a5 API
    pydrodelta run-plan sample_data/plans/pjau_grp.yml --input-api my_token@https://alerta.ina.gob.ar/a5
  

### TODO list

- [x] Color plan.topology.plotVariable() according to tag (obs,sim)
- [x] SacramentoSimplified procedure function
- [x] procedure function schemas: harmonize initial conditions (init_states vs initial_states, array vs object)
- [x] nelder-mead parameter optimization
- [x] sacramento simplified with ensemble kalman filter
- [x] move statistics from ProcedureFunctions to Procedure
- [x] add hline on forecast date in variable plots
- [x] test uh_linear_channel
- [x] map graph edges from procedure boundaries and outputs
- [x] move basin parameters (from procedurefunction.extra_pars) to topology
- [x] create procedure templates
- [x] create node templates
- [x] move procedures to /procedures
- [ ] reimplement hec ras adapter (win)
- [ ] implement swmm adapter
- [ ] create plan/topology configuration database  
- [ ] resample analysis output to match serie time support and time offset
- [x] split time domain (cal/val) in statistics
- [ ] colored log
- [ ] nodes list / procedures list to dataframe
- [ ] implement linear regression as functionProcedure
- [x] implement exponential fit functionProcedure
- [ ] add error band to linear regression result series
- [ ] cache variables
- [x] test suite
- [ ] add procedure exponential recession
- [ ] add procedure repeat last value
- [ ] add procedure adjust tail parameter (to fit using only the last n steps)

### References

Instituto Nacional del Agua

Laboratorio de Hidrología

Programa de Sistemas de Información y Alerta Hidrológico

Ezeiza - Buenos Aires - Argentina

2024