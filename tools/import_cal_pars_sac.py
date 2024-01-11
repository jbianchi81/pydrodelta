import json
import yaml
import click

def run(input,output,node_id):
    file = open(input,"r")
    calibrado = json.load(file)
    def sort_key(p):
        return p["orden"]

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
                "function": {
                    "id": calibrado["nombre"],
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
                    "initial_states": [e["valor"] for e in calibrado["estados_iniciales"]],
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

    yaml.dump(plan,open(output,"w"))

@click.command()
@click.argument('input', type=str)
@click.argument('output', type=str)
@click.argument('node_id', type=int)
def importCalParsSac(input,output,node_id=1):
    run(input = input,output = output, node_id = node_id)

if __name__ == '__main__':
    importCalParsSac()
