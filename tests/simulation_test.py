from pydrodelta.simulation import run_plan
from unittest import TestCase
from click.testing import CliRunner

class Test_Simulation(TestCase):

    def test_run_plan_input_api(self):
        runner = CliRunner()
        result = runner.invoke(
            run_plan,
            [
                "sample_data/plans/dummy_polynomial.yml",
                "--input-api",
                "my_token@https://alerta.ina.gob.ar/test"
            ]
        )
        self.assertEqual(result.exit_code, 0)

    def test_run_plan(self):
        runner = CliRunner()
        result = runner.invoke(
            run_plan,
            [
                "sample_data/plans/dummy_polynomial.yml"
            ]
        )
        self.assertEqual(result.exit_code, 0)