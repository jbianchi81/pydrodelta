from pydrodelta.procedures.sacramento_simplified_fixed_pars import SacramentoSimplifiedFixedParsProcedure
from pydrodelta.util import createDatetimeSequence
from pandas import DataFrame
from unittest import TestCase
from pytz import timezone

class Test_SacramentoSimplifiedFixedParsProcedure(TestCase):

    def test_direct(self):

        input = DataFrame({
            "pma": [5,0,0,0,0,0,0,0],
            "etp": [1,1,1,1,1,1,1,1],
            "q_obs": [0.2,0.4,1.5,1.2,0.4,0.2,0.1,0],
            "smc_obs": [0.2,0.4,1.5,1.2,0.4,0.2,0.1,0]
        })

        procedure = SacramentoSimplifiedFixedParsProcedure(
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
            fixed_parameters = {
                "x1_0": 10,
                "x2_0": 10,
                "m1": 1,
                "c1": 0,
                "c2": 0.0001
            },
            initial_states = [0, 0, 0, 0],
            extra_pars = {
                "ae": 1,
                "area": 86400000.0,
                "rho": 0.5,
                "wp": 0.03,
                "fill_nulls": False,
                "no_check1": False,
                "no_check2": False,
                "mock_run": False,
                "compute_mass_balance": True
            },
            boundaries = input,
            outputs = [ [0.2,0.4,1.5,1.2,0.4,0.2,0.1,0], [0.2,0.4,1.5,1.2,0.4,0.2,0.1,0] ],
            timestart = (2026,1,1),
            time_interval = "1D"
        )

        procedure.run()
        assert procedure.data is not None
        assert len(procedure.data.q_sim.dropna()) == len(input)

        # test calibrate

        procedure.calibration = {
            "calibrate": True,
            "objective_function": "nse",
            "calibration_period": ((2026,1,1), (2026,1,6)),
            "max_iter": 20,
            "no_improve_thr": 0.001,
            "method": "downhill-simplex"
        }

        procedure.calibrate()
        calibration =  procedure.calibration
        assert calibration is not None
        assert calibration.result is not None
        assert len(calibration.result["parameters"]) == 5
        assert procedure.parameters["x1_0"] == 10
        assert procedure.parameters["x2_0"] == 10
        assert procedure.parameters["m1"] == 1
        assert procedure.parameters["c1"] == 0
        assert procedure.parameters["c2"] == 0.0001


