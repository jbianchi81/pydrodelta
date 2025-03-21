import json
import yaml
import click
from a5client import Crud
import os
import sys
config_file = open("%s/.pydrodelta.yml" % os.environ["HOME"]) # "src/pydrodelta/config/config.json")
config = yaml.load(config_file,yaml.CLoader)
config_file.close()
import logging

crud = Crud(
    url = config["input_api"]["url"], 
    token =config["input_api"]["token"])

def sort_key(p):
    return p["orden"]

def get_cal_pars(cal_id=None, output=None, node_id=None, input = None, model = "sac"):
    if type(node_id) == int:
        node_id = [node_id]
    if cal_id is not None:    
        calibrado = crud.readCalibrado(cal_id)
    else:
        calibrado = json.load(open(input,"r"))
    if model.lower() == "sac":
        plan = parse_sac(calibrado,node_id)
    elif model.lower() == "junction":
        plan = parse_junction(calibrado,node_id)
    elif model.lower() == "mkgm":
        plan = parse_mkgm(calibrado,node_id)
    else:
        raise Exception("Model argument not valid")
    if output is not None:
        yaml.dump(plan,open(output,"w"))
    else:
        yaml.dump(plan,sys.stdout)

def parse_sac(calibrado,node_id):
    node_id = int(node_id[0])
    calibrado["parametros"].sort(key=sort_key)
    valores = [p["valor"] for p in calibrado["parametros"]]
    calibrado["forzantes"].sort(key=sort_key)

    boundary_names = ["pma","etp","q_obs","smc_obs"]

    parameters = {
        "x1_0": valores[0],
        "x2_0": valores[1],
        "m1": valores[2],
        "c1": valores[3],
        "c2": valores[4],
        "c3": valores[5],
        "mu": valores[6],
        "alfa": valores[7],
        "m2": valores[8],
        "m3": valores[9]
    }

    nodes = [
        {
            "id": node_id,
            "name": "node 1",
            "node_type": "basin",
            "basin_pars": {
                "area_id": node_id
            },
            "time_interval": {
                "days": 1
            },
            "variables": [
                {
                    "id": 1,
                    "name": "PMAD",
                    "series": [
                        {
                            "tipo": "areal",
                            "series_id": calibrado["forzantes"][1]["series_id"]
                        },
                        {
                            "tipo": "areal",
                            "series_id": calibrado["forzantes"][5]["series_id"]
                        },                
                        {
                            "tipo": "areal",
                            "series_id": calibrado["forzantes"][3]["series_id"]
                        }
                    ]
                },
                { 
                    "id": 15,
                    "name": "ETPD",
                    "series": [
                        {
                            "tipo": "areal",
                            "series_id": calibrado["forzantes"][2]["series_id"]
                        }
                    ]
                },
                {
                    "id": 20,
                    "name": "SMC",
                    "series": [
                        {
                            "tipo": "areal",
                            "series_id": calibrado["forzantes"][4]["series_id"]
                        }
                    ],
                    "series_sim": [
                        {
                            "tipo": "areal",
                            "series_id": calibrado["forzantes"][4]["series_id"]
                        }
                    ]
                },
                {
                    "id": 40,
                    "name": "QMD",
                    "series": [
                        {
                            "tipo": "puntual",
                            "series_id": calibrado["forzantes"][0]["series_id"]
                        }
                    ],
                    "series_sim": [
                        {
                            "tipo": "puntual",
                            "series_id": calibrado["forzantes"][0]["series_id"]
                        }
                    ]
                }
            ]
        }
    ]

    # for i, f in enumerate(calibrado["forzantes"]):
    #     nodes.append({
    #         "name": boundary_names[i], # f["serie"]["estacion"]["nombre"] if "nombre" in f["serie"]["estacion"] else None,
    #         "variables": [
    #             {
    #                 "id": f["serie"]["var"]["id"],
    #                 "series": [
    #                     {
    #                         "tipo": f["serie"]["tipo"],
    #                         "series_id": f["serie"]["id"] 
    #                     }
    #                 ]
    #             }
    #         ]
    #     })

    plan = {
        "id": calibrado["id"],
        "name": calibrado["nombre"],
        "topology": {
            "nodes": nodes
        },
        "procedures": [
            {
                "id": calibrado["nombre"],
                "function": {
                    "type": "SacramentoSimplified",
                    "parameters": parameters,
                    "boundaries": [
                        {
                            "name": "pma",
                            "node_variable": [node_id,1]
                        },
                        {
                            "name": "etp",
                            "node_variable": [node_id,15]
                        },
                        {
                            "name": "q_obs",
                            "node_variable": [node_id,40]
                        },
                        {
                            "name": "smc_obs",
                            "node_variable": [node_id,20]
                        }
                    ],
                    "outputs": [
                        {
                            "name": "q_sim",
                            "node_variable": [node_id,40]
                        },
                        {
                            "name": "smc_sim",
                            "node_variable": [node_id,20]
                        }
                    ],
                    "initial_states": [e["valor"] for e in calibrado["estados"]],
                    "extra_pars": calibrado["extra_pars"] if "extra_pars" in calibrado else {"area":0, "ae":0, "wp": 0, "rho": 0, "fill_nulls": False}
                }
            }   
        ]
    }

    # plan["topology"]["nodes"][0]["series_sim"] = [
    #     {
    #         "series_table": calibrado[0]["outputs"][0]["series_table"],
    #         "series_id": calibrado[0]["outputs"][0]["series_id"]
    #     }
    # ]

    return plan

def parse_junction(calibrado,node_id):

    calibrado["forzantes"].sort(key=sort_key)

    index = 0

    node_names = ["output", "input_1", "input_2", "input_3", "input_4", "input_5", "input_6", "input_7", "input_8", "input_9"]

    output_node = {
        "id": int(node_id[index]),
        "name": "output node",
        "node_type": "station",
        "time_interval": {
            "days": 1
        },
        "variables": [
            {
                "id": 40,
                "name": "QMD",
                "series": [
                    {
                        "tipo": "puntual",
                        "series_id": calibrado["forzantes"][0]["series_id"]
                    }
                ],
                "series_sim": [
                    {
                        "tipo": "puntual",
                        "series_id": calibrado["forzantes"][0]["series_id"]
                    }
                ]
            }
        ]
    }
    index = index + 1

    input_nodes = {}
    boundaries = []

    for i in range(1, len(calibrado["forzantes"])):
        f = calibrado["forzantes"][i]
        if 1 < f["orden"] < 11:
            if  index >= len(node_id):
                raise Exception("missing node_id for index %i" % index) 
            input_nodes[node_names[index]] = {
                "id": int(node_id[index]),
                "name": node_names[index],
                "node_type": "station",
                "time_interval": {
                    "days": 1
                },
                "variables": [
                    {
                        "id": 40,
                        "name": "QMD",
                        "series": [
                            {
                                "tipo": "puntual",
                                "series_id": f["series_id"]
                            }
                        ]
                    }
                ]
            }
            boundaries.append({
                "name": node_names[index],
                "node_variable": [int(node_id[index]),40]
            })
            index = index + 1
        elif f["orden"] < 20:
            index_ = f["orden"] - 10
            if node_names[index_] not in input_nodes:
                raise Exception("Missing forzante %s " % node_names[index_])
            input_nodes[node_names[index_]]["variables"][0]["series"].append({
                "tipo": "puntual",
                "series_id": f["series_id"]
            })
        else:
            index_ = f["orden"] - 19
            if node_names[index_] not in input_nodes:
                raise Exception("Missing forzante %s " % node_names[index_])
            input_nodes[node_names[index_]]["variables"][0]["series"].append({
                "tipo": "puntual",
                "series_id": f["series_id"]
            })

    nodes = [
        output_node
    ]
    for name in node_names:
        if name in input_nodes:
            nodes.append(input_nodes[name])

    plan = {
        "id": calibrado["id"],
        "name": calibrado["nombre"],
        "topology": {
            "nodes": nodes
        },
        "procedures": [
            {
                "id": calibrado["nombre"],
                "function": {
                    "type": "Junction",
                    "boundaries": boundaries,
                    "outputs": [
                        {
                            "name": "output",
                            "node_variable": [int(node_id[0]),40]
                        }
                    ]
                }
            }   
        ]
    }

    # plan["topology"]["nodes"][0]["series_sim"] = [
    #     {
    #         "series_table": calibrado[0]["outputs"][0]["series_table"],
    #         "series_id": calibrado[0]["outputs"][0]["series_id"]
    #     }
    # ]

    return plan

def parse_mkgm(calibrado,node_id):
    logging.debug("node_id type %s, length: %i" % (str(type(node_id)), len(node_id)))

    if len(node_id) < 2:
        raise Exception("node_id is too short. length 2 required")

    calibrado["forzantes"].sort(key=sort_key)
    calibrado["parametros"].sort(key=sort_key)

    node_names = ["output", "input"]

    output_node = {
        "id": int(node_id[0]),
        "name": "output node",
        "node_type": "station",
        "time_interval": {
            "days": 1
        },
        "variables": [
            {
                "id": 40,
                "name": "QMD",
                "series": [
                    {
                        "tipo": "puntual",
                        "series_id": calibrado["forzantes"][0]["series_id"]
                    }
                ],
                "series_sim": [
                    {
                        "tipo": "puntual",
                        "series_id": calibrado["forzantes"][0]["series_id"]
                    }
                ]
            }
        ]
    }

    input_node = {
        "id": int(node_id[1]),
        "name": "input node",
        "node_type": "station",
        "time_interval": {
            "days": 1
        },
        "variables": [
            {
                "id": 40,
                "name": "QMD",
                "series": [
                    {
                        "tipo": "puntual",
                        "series_id": calibrado["forzantes"][1]["series_id"]
                    }
                ],
                "series_sim": [
                    {
                        "tipo": "puntual",
                        "series_id": calibrado["forzantes"][1]["series_id"]
                    }
                ]
            }
        ]
    }

    if len(calibrado["forzantes"]) > 2:
        input_node["variables"][0]["series_sim"].append({
            "tipo": "puntual",
            "series_id": calibrado["forzantes"][2]["series_id"]
        })
    if len(calibrado["forzantes"]) > 3:
        input_node["variables"][0]["series_sim"].append({
            "tipo": "puntual",
            "series_id": calibrado["forzantes"][3]["series_id"]
        })
    
    boundaries = [
        {
            "name": node_names[1],
            "node_variable": [int(node_id[1]),40]
        }
    ]
    outputs = [
        {
            "name": node_names[0],
            "node_variable": [int(node_id[0]),40]
        }
    ]

    nodes = [
        output_node,
        input_node
    ]

    plan = {
        "id": calibrado["id"],
        "name": calibrado["nombre"],
        "topology": {
            "nodes": nodes
        },
        "procedures": [
            {
                "id": calibrado["nombre"],
                "function": {
                    "type": "MuskingumChannel",
                    "boundaries": boundaries,
                    "outputs": outputs,
                    "K": calibrado["parametros"][0]["valor"],
                    "X": calibrado["parametros"][1]["valor"],
                    "Proc": "Muskingum"
                }
            }   
        ]
    }
    if calibrado["estados_iniciales"] is not None:
        plan["procedures"][0]["function"]["initial_states"] =calibrado["estados_iniciales"]
    
    return plan



@click.command()
@click.argument('model', default="sac", type=click.Choice(['sac', 'junction', 'mkgm'], case_sensitive=False))
@click.option('--cal_id','-c', type=int, default=None)
@click.option('--input','-i', type=str, default=None)
@click.option('--output','-o', type=str, default=None)
@click.option('--node-id','-n', default=range(200), show_default=True, multiple=True)
def getCal(model,cal_id,input,output,node_id):
    """ 
    Converts sacramento configuration parameters into a plan. If --cal_id is set, retrieves calibrado from a5 API. Else, calibrado is read from json file at --input. Result is saved as yaml in --output, or to stdout if not defined. API connection parameters are read from config/config.yml -> input_api

    Available models: 
    - sac (SacramentoSimplified)
    - junction (Junction)
    - mkgm (MuskingumChannel)
    """
    node_id = list(node_id) if type(node_id) == tuple else node_id
    logging.debug("node_id type: %s" % str(type(node_id)))
    if cal_id:
        get_cal_pars(cal_id = cal_id,output = output, node_id = node_id, model = model)
    elif input:
        get_cal_pars(input = input,output = output, node_id = node_id, model = model)
    else:
        raise Exception("Missing --cal_id or --input")

if __name__ == '__main__':
    getCal()
