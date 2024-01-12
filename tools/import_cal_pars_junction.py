import json
import yaml
import click

def run(input,output,node_id):
    # file = open(input,"r")
    calibrado = json.load(open(input,"r"))
    def sort_key(p):
        return p["orden"]

    calibrado["forzantes"].sort(key=sort_key)

    index = 0

    node_names = ["output", "input_1", "input_2", "input_3", "input_4", "input_5", "input_6", "input_7", "input_8", "input_9"]

    output_node = {
        "id": node_id[index],
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
                    "type": "SacramentoSimplified",
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

    yaml.dump(plan,open(output,"w"))

@click.command()
@click.argument('input', type=str)
@click.argument('output', type=str)
@click.option('--node-id','-n', multiple=True, default = range(1,10))
def importCalParsJunction(input,output,node_id):
    run(input = input,output = output, node_id = node_id)

if __name__ == '__main__':
    importCalParsJunction()
