from pydrodelta.plan import Plan
from pydrodelta.config import config
from unittest import TestCase
import yaml
import json
from pandas import DataFrame
from networkx import DiGraph

class Test_Plan_Graph(TestCase):

    def test_to_graph(self):
        plan_config = yaml.load(open("%s/sample_data/plans/linear_channel_dummy.yml" % config["PYDRODELTA_DIR"]),yaml.CLoader)
        plan = Plan(**plan_config)
        graph = plan.toGraph(nodes=plan.topology.nodes)
        self.assertTrue(isinstance(graph, DiGraph))

    def test_to_graph_after_execute(self):
        plan_config = yaml.load(open("%s/sample_data/plans/linear_channel_dummy.yml" % config["PYDRODELTA_DIR"]),yaml.CLoader)
        plan = Plan(**plan_config)
        plan.execute(upload=False)
        graph = plan.toGraph(nodes=plan.topology.nodes)
        self.assertTrue(isinstance(graph, DiGraph))

    def test_print_graph(self):
        plan_config = yaml.load(open("%s/sample_data/plans/linear_channel_dummy.yml" % config["PYDRODELTA_DIR"]),yaml.CLoader)
        plan = Plan(**plan_config)
        plan.printGraph(nodes=plan.topology.nodes, output_file="results/linear_channel_dummy.png")
        
    def test_export_graph(self):
        plan_config = yaml.load(open("%s/sample_data/plans/linear_channel_dummy.yml" % config["PYDRODELTA_DIR"]),yaml.CLoader)
        plan = Plan(**plan_config)
        plan.exportGraph(nodes=plan.topology.nodes, output_file="%s/results/linear_channel_dummy.json" % config["PYDRODELTA_DIR"])
        graph = json.load(open("%s/results/linear_channel_dummy.json" % config["PYDRODELTA_DIR"]))
        for key in ['directed', 'multigraph', 'graph', 'nodes', 'links']:
            self.assertTrue(key in graph)
        self.assertEqual(
            len([ n for n in  graph["nodes"] if n["object"]["node_type"] == "station"] ),
            2
        )
        self.assertEqual(
            len([ n for n in  graph["nodes"] if n["object"]["node_type"] == "procedure"] ), 
            1
        )
        self.assertEqual(
            len(graph["links"]),
            2
        )

