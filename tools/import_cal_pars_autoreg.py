import json
import yaml
file = open("tmp/cal_500.json","r")
calibrado = json.load(file)
def sort_key(p):
    return p["orden"]

calibrado[0]["parametros"].sort(key=sort_key)
valores = [p["valor"] for p in calibrado[0]["parametros"]]


boundary_names = ["input_1","input_2","input_3"]
m = int(valores[0])
n = int(valores[1])
N = 3 # int(valores[2])
# (len(calibrado["parametros"]) - 3)
coefficients = list()
index = 3
for i in range(n):
    step = {
        "intercept": valores[index],
        "step": i
    }
    index = index + 1
    step["boundaries"] = list()
    for j in range(N):
        step["boundaries"].append({
            "name": boundary_names[j],
            "values": valores[index:index+m]
        })
        index = index + m
    coefficients.append(step)
   

yaml.dump(coefficients,open("tmp/500_coefficients.yml","w"))