from pydrodelta.plan import Plan
# from pydrodelta.procedure_function import ProcedureFunction
from pydrodelta.procedures.linear_fit import LinearFitProcedure
from unittest import TestCase
from pandas import DataFrame
from pydrodelta.util import createDatetimeSequence, tryParseAndLocalizeDate
import numpy as np
from numpy import nan
from pathlib import Path

data_dir = Path(__file__).parent / "data"

class Test_LinearFit(TestCase):

    def test_run(self):
        plan = Plan.load(data_dir / "plans/dummy_linear_fit_2_boundaries.yml")
        plan.execute(upload=False)

    def test_drop_warmup(self):
        lfit = LinearFitProcedure(
            boundaries= [
                {
                    "name": "input_1",
                    "node_variable": (1,40)
                }
            ],
            outputs = [
                {
                    "name": "output",
                    "node_variable": (1,39)
                }
            ],
            extra_pars = {
                "warmup_steps": 10,
                "drop_warmup": True
            }
        )
        self.assertRaises(Exception, lfit.exec) # missing input
        self.assertRaises(Exception, lfit.exec, input=[]) # missing output_obs
        self.assertRaises(Exception, lfit.exec, input=[ # missing output_obs
            DataFrame(
                data = {
                    "valor": np.random.rand(32)
                },
                index = createDatetimeSequence(
                    timeInterval={"days":1}, 
                    timestart=tryParseAndLocalizeDate((2020,1,1)),
                    timeend=tryParseAndLocalizeDate((2020,2,1))
                )                    
            )
        ])
        output, results = lfit.exec(input=[
            DataFrame(
                data = {
                    "valor": np.random.rand(32)
                },
                index = createDatetimeSequence(
                    timeInterval={"days":1}, 
                    timestart=tryParseAndLocalizeDate((2020,1,1)),
                    timeend=tryParseAndLocalizeDate((2020,2,1))
                )                    
            )
        ],
        output_obs = [
            DataFrame(
                data = {
                    "valor": np.random.rand(32)
                },
                index = createDatetimeSequence(
                    timeInterval={"days":1}, 
                    timestart=tryParseAndLocalizeDate((2020,1,1)),
                    timeend=tryParseAndLocalizeDate((2020,2,1))
                )                    
            )
        ])
        self.assertEqual(len(output),1)
        self.assertEqual(len(output[0].dropna()), 32 - 10)
        self.assertEqual(output[0].dropna().index[0],tryParseAndLocalizeDate((2020,1,11)))

    def test_direct(self):
        procedure = LinearFitProcedure(
            boundaries = [
                [1.2,3.4,4.5,5.6,6.7,7.8,8.9,10.0],
                [2.3,3.4,4.5,5.6,6.7,7.8,8.9,10.0]
            ],
            outputs = [
                [1.0,2.0,3.0,4.0,5.0,nan,nan,nan]
            ]
        )
        procedure.run()
        assert procedure.data is not None
        assert len(procedure.data.output.dropna()) == 8
        self.assertAlmostEqual(procedure.data.output.iloc[7],8.0,2)
        assert procedure.linear_model is not None
        assert procedure.linear_model["method"] == "lfit"
        self.assertAlmostEqual(procedure.linear_model["r2"], 1.0, 2)