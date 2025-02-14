from unittest import TestCase
from pydrodelta.pydrology import LagAndRoute
# from numpy import array
# from typing import List, Tuple

class Test_lagandroute(TestCase):

    def test_init_missing_k(self):
        self.assertRaises(
            ValueError,
            LagAndRoute,
            [1.1]
        )

    def test_init_2_pars(self):    
        procedure = LagAndRoute(
            pars = [1.1, 2.2]
        )
        self.assertEqual(procedure.lag, 1.1)
        self.assertEqual(procedure.k, 2.2)
        self.assertEqual(procedure.n, 1)
        self.assertEqual(len(procedure.routingSystem.Cascade),2)
        self.assertEqual(len(procedure.routingSystem.Cascade[0]),1)
        self.assertEqual(procedure.routingSystem.Cascade[0][0],0)
        self.assertEqual(len(procedure.routingSystem.Cascade[1]),1)
        self.assertEqual(procedure.routingSystem.Cascade[1][0],0)

    def test_init_1_reservoir(self):    
        procedure = LagAndRoute(
            pars = [1.1, 2.2, 1]
        )
        self.assertEqual(procedure.lag, 1.1)
        self.assertEqual(procedure.k, 2.2)
        self.assertEqual(procedure.n, 1)
        self.assertEqual(len(procedure.routingSystem.Cascade),2)
        self.assertEqual(len(procedure.routingSystem.Cascade[0]),1)
        self.assertEqual(procedure.routingSystem.Cascade[0][0],0)
        self.assertEqual(procedure.routingSystem.Cascade[1][0],0)


    def test_init_3_pars(self):    
        procedure = LagAndRoute(
            pars = [1.1, 2.2, 2]
        )
        self.assertEqual(procedure.lag, 1.1)
        self.assertEqual(procedure.k, 2.2)
        self.assertEqual(procedure.n, 2)
        self.assertEqual(len(procedure.routingSystem.Cascade),2)
        self.assertEqual(len(procedure.routingSystem.Cascade[0]),2)
        self.assertEqual(procedure.routingSystem.Cascade[0][0],0)
        self.assertEqual(procedure.routingSystem.Cascade[0][1],0)
        self.assertEqual(len(procedure.routingSystem.Cascade[1]),2)
        self.assertEqual(procedure.routingSystem.Cascade[1][0],0)
        self.assertEqual(procedure.routingSystem.Cascade[1][1],0)

    def test_init_empty_initial_conditions(self):    
        procedure = LagAndRoute(
            pars = [1.1, 2.2, 2],
            InitialConditions = []
        )
        self.assertEqual(len(procedure.routingSystem.Cascade),2)
        self.assertEqual(len(procedure.routingSystem.Cascade[0]),2)
        self.assertEqual(procedure.routingSystem.Cascade[0][0],0)
        self.assertEqual(procedure.routingSystem.Cascade[0][1],0)
        self.assertEqual(len(procedure.routingSystem.Cascade[1]),2)
        self.assertEqual(procedure.routingSystem.Cascade[1][0],0)
        self.assertEqual(procedure.routingSystem.Cascade[1][1],0)
    
    def test_init_raise_short_initial_conditions(self):    
        self.assertRaises(
            ValueError,
            LagAndRoute,
            pars = [1.1, 2.2, 3],
            InitialConditions = [1.1,2.2]
        )

    def test_init_set_initial_conditions(self):    
        procedure = LagAndRoute(
            pars = [1.1, 2.2, 3],
            InitialConditions = [1.1,2.2,3.3]
        )
        self.assertEqual(len(procedure.routingSystem.Cascade),2)
        self.assertEqual(len(procedure.routingSystem.Cascade[0]),3)
        self.assertEqual(procedure.routingSystem.Cascade[0][0],1.1)
        self.assertEqual(procedure.routingSystem.Cascade[0][1],2.2)
        self.assertEqual(procedure.routingSystem.Cascade[0][2],3.3)
        self.assertEqual(len(procedure.routingSystem.Cascade[1]),3)
        self.assertEqual(procedure.routingSystem.Cascade[1][0],0)
        self.assertEqual(procedure.routingSystem.Cascade[1][1],0)
        self.assertEqual(procedure.routingSystem.Cascade[1][2],0)

    def test_init_set_boundaries(self):    
        procedure = LagAndRoute(
            pars = [1.1, 2.2, 3],
            Boundaries = [
                [1,1,1,1,1],
                [1,1,1,1,1]
            ]
        )
        self.assertEqual(len(procedure.boundaries[0]),5)
        self.assertEqual(len(procedure.boundaries[1]),5)
        self.assertEqual(len(procedure.Inflow),5)
        self.assertEqual(len(procedure.Leakages),5)

    def test_init_fill_leakages(self):    
        procedure = LagAndRoute(
            pars = [1.1, 2.2, 3],
            Boundaries = [
                [1,1,1,1,1],
                [1,1,1]
            ]
        )
        self.assertEqual(len(procedure.Leakages),5)
        self.assertEqual(procedure.Leakages[0],1)
        self.assertEqual(procedure.Leakages[1],1)
        self.assertEqual(procedure.Leakages[2],1)
        self.assertEqual(procedure.Leakages[3],0)
        self.assertEqual(procedure.Leakages[4],0)


    def test_init_fill_inflow(self):    
        procedure = LagAndRoute(
            pars = [1.1, 2.2, 3],
            Boundaries = [
                [1,1,1],
                [1,1,1,1,1]
            ]
        )
        self.assertEqual(len(procedure.Inflow),5)
        self.assertEqual(procedure.Inflow[0],1)
        self.assertEqual(procedure.Inflow[1],1)
        self.assertEqual(procedure.Inflow[2],1)
        self.assertEqual(procedure.Inflow[3],0)
        self.assertEqual(procedure.Inflow[4],0)

    def test_init_null_outflow(self):    
        procedure = LagAndRoute(
            pars = [1.1, 2.2, 3],
            Boundaries = [
                [1,2,3]
            ]
        )
        self.assertEqual(len(procedure.Leakages),3)
        self.assertEqual(procedure.Leakages[0],0)
        self.assertEqual(procedure.Leakages[1],0)
        self.assertEqual(procedure.Leakages[2],0)

    def test_run(self):    
        procedure = LagAndRoute(
            pars = [1.1, 2.2, 3],
            Boundaries = [
                [1] * 1000
            ]
        )
        procedure.executeRun()
        self.assertGreaterEqual(len(procedure.Q),1000)
        self.assertAlmostEqual(procedure.Q[999],1,7)

    def test_no_route_k_0(self):    
        procedure = LagAndRoute(
            pars = [1, 0]
        )
        self.assertIsNone(procedure.routingSystem, "Expected RoutingSystem = None")

    def test_sum(self):    
        procedure = LagAndRoute(
            pars = [1, 1],
            Boundaries = [
                [0,1,0,0,0,0,0,0,0,0,0,0,0,0]
            ]
        )
        procedure.executeRun()
        self.assertAlmostEqual(procedure.Q.sum(),1,4)

    def test_no_lag(self):    
        procedure = LagAndRoute(
            pars = [0, 0.00001],
            Boundaries = [
                [0,1,0,0,0,0,0,0,0,0,0,0,0,0]
            ]
        )
        self.assertEqual(procedure.laggedInflow[1],1)

    def test_lag(self):    
        procedure = LagAndRoute(
            pars = [1, 0],
            Boundaries = [
                [0,1,0,0,0,0,0,0,0,0,0,0,0,0]
            ]
        )
        procedure.executeRun()
        self.assertAlmostEqual(procedure.Q.sum(),1,4)
        self.assertAlmostEqual(procedure.Q[2],1,4)

    def test_lag_and_route(self):    
        procedure = LagAndRoute(
            pars = [1, 0.5],
            Boundaries = [
                [0,1,0,0,0,0,0,0,0,0,0,0,0,0]
            ]
        )
        procedure.executeRun()
        self.assertAlmostEqual(procedure.Q.sum(),1,4)
        self.assertAlmostEqual(procedure.Q[15],0)
