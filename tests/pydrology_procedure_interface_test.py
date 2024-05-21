from unittest import TestCase
from pydrodelta.pydrology_procedure_interface import PydrologyProcedureInterface
from numpy import array
from typing import List, Tuple

class Test_pydrology_procedure_interface(TestCase):

    def test_init_blank(self):
        procedure = PydrologyProcedureInterface()
        self.assertIsNone(procedure.pars)
        self.assertIsNone(procedure.boundaries)
        self.assertIsNone(procedure.initial_conditions)

    def test_init_empty_lists(self):
        procedure = PydrologyProcedureInterface(
            [],
            [],
            []
        )
        self.assertIsInstance(procedure.pars,list)
        self.assertIsInstance(procedure.boundaries,list)
        self.assertIsInstance(procedure.initial_conditions,list)

    def test_init_lists(self):
        procedure = PydrologyProcedureInterface(
            [1.0,2.0,3.0,4.0],
            [[1.0,2.0,3.0,4.0],[5.0,6.0,7.0,8.0]],
            [[1.0,2.0,3.0,4.0],[5.0,6.0,7.0,8.0]]
        )
        self.assertIsInstance(procedure.pars,list)
        self.assertIsInstance(procedure.boundaries,list)
        self.assertIsInstance(procedure.initial_conditions,list)

    def test_raise_not_a_list(self):
        self.assertRaises(
            TypeError,
            PydrologyProcedureInterface,
            1,
            [1.0,2.0,3.0,4.0],
            [1.0,2.0,3.0,4.0]
        )

    def test_parse_array(self):
        procedure = PydrologyProcedureInterface(
            array([1.0,2.0,3.0,4.0]),
            array([[1.0,2.0,3.0,4.0],[5.0,6.0,7.0,8.0]]),
            array([[1.0,2.0,3.0,4.0],[5.0,6.0,7.0,8.0]])
        )
        self.assertIsInstance(procedure.pars,list)
        self.assertEquals(len(procedure.pars), 4)
        self.assertIsInstance(procedure.boundaries,list)
        self.assertEquals(len(procedure.boundaries), 2)
        for i in procedure.boundaries:
            self.assertEquals(len(i), 4)
        self.assertIsInstance(procedure.initial_conditions,list)
        self.assertEquals(len(procedure.initial_conditions), 2)
        for i in procedure.initial_conditions:
            self.assertEquals(len(i), 4)

    def test_parse_tuple(self):
        procedure = PydrologyProcedureInterface(
            (1.0,2.0,3.0,4.0),
            ((1.0,2.0), (3.0, 4.0))
        )
        self.assertIsInstance(procedure.pars,list)
        self.assertEquals(len(procedure.pars), 4)
        self.assertIsInstance(procedure.boundaries,list)
        self.assertEquals(len(procedure.boundaries), 2)
        for i in procedure.boundaries:
            self.assertIsInstance(i, tuple)
            self.assertEquals(len(i), 2)

    def test_inherit(self):
        class MyActualProcedure(PydrologyProcedureInterface):
            
            @property
            def par_one(self) -> float:
                return self.pars[0] 
            
            @property
            def par_two(self) -> float:
                return self.pars[0] 
            
            def __init__(
                self,
                pars : Tuple[float,float],
                Boundaries : List[List[float]] = [[0],[0]],
                InitialConditions : List[float] = [0,0],
                other_property : float = None):
                
                super().__init__(
                    pars,
                    Boundaries, 
                    InitialConditions)
                
                # additional checks
                self.checkItemsType("pars",float,length=2, coerce=True)
                self.checkItemsType("boundaries", list)

                # set additional properties
                self.other_property = other_property

        procedure = MyActualProcedure(
            [1.0,2.0],
            [[1.0,2.0,3.0,4.0],[5.0,6.0,7.0,8.0]],
            [[1.0,2.0,3.0,4.0],[5.0,6.0,7.0,8.0]],
            other_property = 43.67
        )

        self.assertIsInstance(procedure.pars,list)
        self.assertEquals(len(procedure.pars), 2)
        self.assertIsInstance(procedure.boundaries,list)
        self.assertEquals(len(procedure.boundaries), 2)
        self.assertIsInstance(procedure.initial_conditions,list)
        self.assertEquals(len(procedure.initial_conditions), 2)
        self.assertEquals(procedure.other_property, 43.67)

        # pars must be of length 2 
        self.assertRaises(
            ValueError,
            MyActualProcedure,
            [1.0]
        )

        # pars[1] must be a float but a str is given 
        self.assertRaises(
            TypeError,
            MyActualProcedure,
            [1.0, "imastr"]
        )

        # boundaries must be a list of lists but a list of arrays is given, and won't be coerced 
        self.assertRaises(
            TypeError,
            MyActualProcedure,
            [1, 2],
            [array([1,2])]
        )

        # ints should be coerced to float
        procedure = MyActualProcedure(
            [1, 2]
        )
        self.assertIsInstance(procedure.par_one, float)
        self.assertIsInstance(procedure.par_two, float)