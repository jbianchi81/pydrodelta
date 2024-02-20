import subprocess

selected_files = [
    "derived_node_variable",
    "procedures.generic_linear_channel",
    "procedures.linear_channel",
    "node_variable",
    "node",
    "observed_node_variable",
    "plan",
    "procedure",
    "result_statistics",
    "topology",
    "procedures.uh_linear_channel",
    "util",
    "node_serie",
    "node_serie_prono",
    "validation",
    "derived_node_serie",
    "calibration",
    "interpolated_origin",
    "derived_origin"
]

for filename in selected_files:
    path = "pydrodelta.%s" % filename
    output = open("doc/%s.md" % filename,"w")
    subprocess.run(["pydoc-markdown", "-I","src","-m",path,"--render-toc"],stdout = output)
    output.close()
