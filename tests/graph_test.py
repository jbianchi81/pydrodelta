from pydrodelta.plan import Plan
from unittest import TestCase
import yaml
import json
import os
from pandas import DataFrame
from networkx import DiGraph
from pydrodelta.config import config
from pathlib import Path

data_dir = Path(__file__).parent / "data"

class Test_Plan_Graph(TestCase):

    def test_to_graph(self):
        plan = Plan.load(data_dir / "plans/linear_channel_dummy.yml")
        assert plan.topology is not None
        graph = plan.toGraph(nodes=plan.topology.nodes)
        self.assertTrue(isinstance(graph, DiGraph))

    def test_to_graph_after_execute(self):
        plan = Plan.load(data_dir / "plans/linear_channel_dummy.yml")
        plan.execute(upload=False)
        assert plan.topology is not None
        graph = plan.toGraph(nodes=plan.topology.nodes)
        self.assertTrue(isinstance(graph, DiGraph))

    def test_print_graph(self):
        plan = Plan.load(data_dir / "plans/linear_channel_dummy.yml")
        assert plan.topology is not None
        plan.printGraph(nodes=plan.topology.nodes, output_file= data_dir / "results/linear_channel_dummy.png")
        
    def test_export_graph(self):
        plan = Plan.load(data_dir / "plans/linear_channel_dummy.yml")
        assert plan.topology is not None
        plan.exportGraph(nodes=plan.topology.nodes, output_file= data_dir / "results/linear_channel_dummy.json")
        graph = json.load(open(data_dir / "results/linear_channel_dummy.json"))
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

