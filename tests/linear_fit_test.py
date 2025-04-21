from pydrodelta.plan import Plan
# from pydrodelta.procedure_function import ProcedureFunction
from pydrodelta.procedures.linear_fit import LinearFitProcedureFunction
from unittest import TestCase
from pandas import DataFrame
from pydrodelta.util import createDatetimeSequence, tryParseAndLocalizeDate
import numpy as np
class Test_LinearFit(TestCase):

    def test_run(self):
        plan = Plan.load("sample_data/plans/dummy_linear_fit_2_boundaries.yml")
        plan.execute(upload=False)

    def test_drop_warmup(self):
        lfit = LinearFitProcedureFunction(
            type="LinearFit",
            boundaries= [
                {
                    "name": "input",
                    "node_variable": [1,40]
                }
            ],
            outputs = [
                {
                    "name": "output",
                    "node_variable": [1,39]
                }
            ],
            parameters = {},
            extra_pars = {
                "warmup_steps": 10,
                "drop_warmup": True
            }
        )
        self.assertRaises(ValueError, lfit.run) # missing input
        self.assertRaises(ValueError, lfit.run, input=[]) # missing output_obs
        self.assertRaises(ValueError, lfit.run, input=[ # missing output_obs
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
        output, results = lfit.run(input=[
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
