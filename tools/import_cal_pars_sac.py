import json
import yaml
file = open("tmp/cal_132.json","r")
calibrado = json.load(file)
def sort_key(p):
    return p["orden"]

calibrado[0]["parametros"].sort(key=sort_key)
valores = [p["valor"] for p in calibrado[0]["parametros"]]
calibrado[0]["forzantes"].sort(key=sort_key)

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

nodes = []
for f in calibrado[0]["forzantes"]:
    nodes.append({
        "name": f["serie"]["estacion"]["nombre"] if "nombre" in f["serie"]["estacion"] else None,
        "variables": [
            {
                "id": f["serie"]["var"]["id"],
                "series": [
                    {
                        "tipo": f["serie"]["tipo"],
                        "series_id": f["serie"]["id"] 
                    }
                ]
            }
        ]
    })

plan = {
    "id": calibrado[0]["id"],
    "name": calibrado[0]["nombre"],
    "topology": {
        "nodes": nodes
    },
    "procedures": [
        {
            "function": {
                "type": "SacramentoSimplified",
                "parameters": parameters,
                "boundaries": [
                    {
                        "name": "pma",
                        "node_variable": [1,1]
                    },
                    {
                        "name": "etp",
                        "node_variable": [1,4]
                    },
                    {
                        "name": "q_obs",
                        "node_variable": [2,40]
                    },
                    {
                        "name": "smc_obs",
                        "node_variable": [1,20]
                    }
                ],
                "initial_states": [e["valor"] for e in calibrado[0]["estados_iniciales"]],
                "extra_pars": calibrado[0]["extra_pars"]
            }
        }   
    ]
}

plan["topology"]["nodes"][0]["series_sim"] = [
    {
        "series_table": calibrado[0]["outputs"][0]["series_table"],
        "series_id": calibrado[0]["outputs"][0]["series_id"]
    }
]

yaml.dump(plan,open("tmp/cal_132.yml","w"))