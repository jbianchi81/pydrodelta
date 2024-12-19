from pydrodelta.plan import Plan
from unittest import TestCase
import os
from pandas import DataFrame
import string
import random
from pydrodelta.config import config

class PersistenceTest(TestCase):
    def test_store_restore(self):
        bucket_name = "".join(random.choices(string.ascii_lowercase + string.digits, k= 16))
        plan_0 = Plan.load("%s/sample_data/plans/linear_channel_dummy.yml" % config["PYDRODELTA_DIR"], s3_config = {
            "url": "play.min.io",
            "access_key": "Q3AM3UQ867SPQQA43P2F",
            "secret_key": "zuf+tfteSlswRu7BJ86wekitnifILbZam1KYY3TG",
            "bucket_name": bucket_name
            })
        plan_0.topology.batchProcessInput()
        nodes_data = {}
        for n in plan_0.topology.nodes:
            nodes_data[n.id] = {}
            for var_id, v in n.variables.items():
                nodes_data[n.id][var_id] = {
                    "data": v.data,
                    "series": {},
                    "series_prono": {},
                    "series_sim": {},
                    "series_output": {}
                }
                if v.series is not None:
                    for s in v.series:
                        if s.data is not None:
                            nodes_data[n.id][var_id]["series"][s.series_id] = s.data
                if v.series_prono is not None:
                    for s in v.series_prono:
                        if s.data is not None:
                            nodes_data[n.id][var_id]["series_prono"][s.series_id] = s.data
                if v.series_sim is not None:
                    for s in v.series_sim:
                        if s.data is not None:
                            nodes_data[n.id][var_id]["series_sim"][s.series_id] = s.data
                if v.series_output is not None:
                    for s in v.series_output:
                        if s.data is not None:
                            nodes_data[n.id][var_id]["series_output"][s.series_id] = s.data
        plan_0.topology.storeSeriesData()
        plan_0.topology.restoreSeriesData()

        for n in plan_0.topology.nodes:
            for var_id, v in n.variables.items():
                if nodes_data[n.id][var_id]["data"] is not None:
                    self.assertTrue(nodes_data[n.id][var_id]["data"].equals(v.data))
                if v.series is not None:
                    for s in v.series:
                        if s.data is not None:
                            self.assertTrue(nodes_data[n.id][var_id]["series"][s.series_id].equals(s.data))
                if v.series_prono is not None:
                    for s in v.series_prono:
                        if s.data is not None:
                            self.assertTrue(nodes_data[n.id][var_id]["series_prono"][s.series_id].equals(s.data))
                if v.series_sim is not None:
                    for s in v.series_sim:
                        if s.data is not None:
                            self.assertTrue(nodes_data[n.id][var_id]["series_sim"][s.series_id].equals(s.data))
                if v.series_output is not None:
                    for s in v.series_output:
                        if s.data is not None:
                            self.assertTrue(nodes_data[n.id][var_id]["series_output"][s.series_id].equals(s.data))
        plan_1 = Plan.load("%s/sample_data/plans/linear_channel_dummy.yml" % config["PYDRODELTA_DIR"], s3_config = {
            "url": "play.min.io",
            "access_key": "Q3AM3UQ867SPQQA43P2F",
            "secret_key": "zuf+tfteSlswRu7BJ86wekitnifILbZam1KYY3TG",
            "bucket_name": bucket_name
            })
        plan_1.topology.restoreSeriesData()

        for n in plan_1.topology.nodes:
            for var_id, v in n.variables.items():
                if nodes_data[n.id][var_id]["data"] is not None:
                    self.assertTrue(nodes_data[n.id][var_id]["data"].equals(v.data))
                if v.series is not None:
                    for s in v.series:
                        if s.data is not None:
                            self.assertTrue(nodes_data[n.id][var_id]["series"][s.series_id].equals(s.data))
                if v.series_prono is not None:
                    for s in v.series_prono:
                        if s.data is not None:
                            self.assertTrue(nodes_data[n.id][var_id]["series_prono"][s.series_id].equals(s.data))
                if v.series_sim is not None:
                    for s in v.series_sim:
                        if s.data is not None:
                            self.assertTrue(nodes_data[n.id][var_id]["series_sim"][s.series_id].equals(s.data))
                if v.series_output is not None:
                    for s in v.series_output:
                        if s.data is not None:
                            self.assertTrue(nodes_data[n.id][var_id]["series_output"][s.series_id].equals(s.data))
        