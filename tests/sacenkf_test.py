from pydrodelta.procedures.sac_enkf import SacEnkfProcedure
from pydrodelta.util import createDatetimeSequence
from pandas import DataFrame
from unittest import TestCase
from pytz import timezone

class Test_SacEnkfProcedure(TestCase):

    def test_direct(self):

        input = DataFrame({
            "pma": [5,0,0,0,0,0,0,0],
            "etp": [1,1,1,1,1,1,1,1],
            "q_obs": [0.2,0.4,1.5,1.2,0.4,0.2,0.1,0],
            "smc_obs": [0.2,0.4,1.5,1.2,0.4,0.2,0.1,0]
        })

        procedure = SacEnkfProcedure(
            parameters = {
                "x1_0": 10,
                "x2_0": 10,
                "m1": 1,
                "c1": 0,
                "c2": 0.0001,
                "c3": 0.02,
                "mu": 0,
                "alfa": 0.5,
                "m2": 1,
                "m3": 1
            },
            initial_states = [0, 0, 0, 0],
            extra_pars = {
                "area": 86400000.0
            },
            asim_pars = {
                "asim": ["q"],
                "rule": [
                    [-100,100,1]
                ]
            },
            boundaries = input,
            outputs = [ [0.2,0.4,1.5,1.2,0.4,0.2,0.1,0], [0.2,0.4,1.5,1.2,0.4,0.2,0.1,0] ],
            timestart = (2026,1,1),
            time_interval = "1D"
        )

        procedure.run()
        assert procedure.data is not None
        assert len(procedure.data.q_sim.dropna()) == len(input)
        assert min(procedure.data.index).isoformat()[0:10] == "2026-01-01"
        results = procedure.procedure_function_results
        assert results is not None
        assert results.data is not None
        assert isinstance(results.data, DataFrame)
        assert sum([row.KG[3][0] for i, row in results.data.iterrows()]) > 0

        