from pydrodelta.procedure import Procedure
from pydrodelta.procedures.abstract import AbstractProcedureFunction
from unittest import TestCase
from pydrodelta.types.enhanced_typed_list import EnhancedTypedList
from pydrodelta.procedure_boundary import ProcedureBoundary
class Test_Procedure(TestCase):
    
    def test_create(self):
        procedure = Procedure(
            1,
            {
                "type": "AbstractProcedureFunction"
            }
        )
        self.assertIsInstance(procedure, Procedure)
    

