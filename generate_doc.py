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
    "util",
    "node_serie",
    "node_serie_prono",
    "validation",
    "derived_node_serie",
    "calibration",
    "interpolated_origin",
    "derived_origin",
    "procedure_boundary",
    "procedure_function",
    "procedure_function_results",
    "procedures.difference",
    "procedures.expression",
    "procedures.gr4j",
    "procedures.grp",
    "procedures.hosh4p1l",
    "procedures.hosh4p1lnash",
    "procedures.hosh4p1luh",
    "procedures.junction",
    "procedures.linear_channel",
    "procedures.linear_combination_2b",
    "procedures.linear_combination_3b",
    "procedures.linear_combination_4b",
    "procedures.linear_combination",
    "procedures.muskingumchannel",
    "procedures.polynomial",
    "procedures.pq",
    "procedures.sac_enkf",
    "procedures.sacramento_simplified",
    "procedures.uh_linear_channel",
    "model_parameter",
    "model_state",
    "node_serie_prono_metadata"
]

for filename in selected_files:
    path = "pydrodelta.%s" % filename
    output = open("doc/%s.md" % filename,"w")
    subprocess.run(["pydoc-markdown", "-I","src","-m",path,"--render-toc"],stdout = output)
    output.close()
