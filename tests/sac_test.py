from pydrodelta.plan import Plan
from unittest import TestCase
import yaml
import os

class Test_SacramentoSimplified(TestCase):

    def test_calibration_save_result(self):
        config = yaml.load(open("%s/sample_data/plans/dummy_sac.yml" % os.environ["PYDRODELTA_DIR"]),yaml.CLoader)
        plan = Plan(**config)
        plan.execute(upload=False)
        
        self.assertTrue(isinstance(plan.procedures[0].calibration.calibration_result[0],list))
        self.assertEqual(
            len(plan.procedures[0].calibration.calibration_result[0]),
            len(plan.procedures[0].function._parameters)
        )
        for i, value in enumerate(plan.procedures[0].calibration.calibration_result[0]):
            self.assertTrue(isinstance(value,float))
            self.assertTrue(value >= plan.procedures[0].function._parameters[i].min)
            self.assertTrue(value <= plan.procedures[0].function._parameters[i].max)
        plan.procedures[0].calibration.saveResult(
            "results/dummy_sac_cal_result.yml",
            format = "yaml"
        )

        self.assertTrue("scores" in plan.procedures[0].calibration.result)
        self.assertTrue(isinstance(plan.procedures[0].calibration.result["scores"], list))
        self.assertEqual(
            len(plan.procedures[0].calibration.result["scores"]),
            1
        )
        for key in ["n","rmse","r","nse", "n_val", "rmse_val", "r_val", "nse_val"]:
            self.assertTrue(key in plan.procedures[0].calibration.result["scores"][0])
            if key in ["n", "n_val"]:
                self.assertTrue(isinstance(plan.procedures[0].calibration.result["scores"][0][key], int))
            else:
                self.assertTrue(isinstance(plan.procedures[0].calibration.result["scores"][0][key], float))

        saved_result = yaml.load(open("%s/results/dummy_sac_cal_result.yml" % os.environ["PYDRODELTA_DIR"]),yaml.CLoader)
        self.assertTrue("parameters" in saved_result)
        self.assertTrue(isinstance(saved_result["parameters"],list))
        self.assertEqual(
            len(saved_result["parameters"]),
            len(plan.procedures[0].function._parameters)
        )
        for i, value in enumerate(saved_result["parameters"]):
            self.assertTrue(isinstance(value,float))        
            self.assertTrue(value >= plan.procedures[0].function._parameters[i].min)
            self.assertTrue(value <= plan.procedures[0].function._parameters[i].max)

        self.assertTrue("scores" in saved_result)
        self.assertTrue(isinstance(saved_result["scores"], list))
        self.assertEqual(
            len(saved_result["scores"]),
            1
        )
        

