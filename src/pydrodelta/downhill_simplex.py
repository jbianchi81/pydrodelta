#!/usr/bin/env python
# coding: UTF-8
from __future__ import division
from typing import Optional, List, Tuple, Callable, Iterable, Union
import logging
from pathlib import Path

'''
    Pure Python/Numpy implementation of the downhill simplex algorithm.
    Reference: https://en.wikipedia.org/wiki/Nelder%E2%80%93Mead_method
'''

import numpy as np

Point = np.typing.NDArray[np.float64]

PointScoreTuple = Tuple[Point,np.float64]

def generate_simplex(x0 : np.typing.NDArray[np.float64], step : float=0.1):
    """
    Create a simplex based at x0
    """
    yield x0.copy()
    for i,_ in enumerate(x0):
        x = x0.copy()
        x[i] += step
        yield x

def make_simplex(x0 : np.typing.NDArray[np.float64], step : float=0.1):
    return np.array(list(generate_simplex(x0, step)))

def centroid(points : np.typing.NDArray[np.float64]) -> np.typing.NDArray[np.float64]:
    """
    Compute the centroid of a list points given as an array.
    points : array of points (2d numpy array)
    returns : point (1d numpy array)
    """
    return np.mean(points, axis=0)

class DownhillSimplex(object):

    refl = 1.
    ext = 1.
    cont = 0.5
    red = 0.5

    # max_stagnations: break after max_stagnations iterations with an improvement lower than no_improve_thr
    no_improve_thr=10e-6
    max_stagnations=10

    max_iter=1000

    _limits : Optional[List[Tuple[float,float]]]

    @property
    def limits(self) -> Optional[List[Tuple[float,float]]]:
        return self._limits
    @limits.setter
    def limits(self,limits : Optional[List[Tuple[float,float]]]):
        if limits is None:
            self._limits = None
            return
        self._limits = []
        for i, r in enumerate(limits):
            if len(r) < 2:
                raise Exception("Range for parameter index %i must be of length 2: (min, max)" % i)
            self._limits.append((float(r[0]), float(r[1])))

    current_points : Optional[List[PointScoreTuple]]

    initial_points : Optional[List[PointScoreTuple]]

    @property
    def current_points_list(self) -> Optional[List[List[float]]]:
        pts : List[List[float]] = []
        if self.current_points is None:
            return None
        for p in self.current_points:
            pts.append([*p[0].tolist(), p[1]])
        return pts

    @property
    def initial_points_list(self) -> Optional[List[List[float]]]:
        pts : List[List[float]] = []
        if self.initial_points is None:
            return None
        for p in self.initial_points:
            pts.append([*p[0].tolist(), p[1]])
        return pts

    iters : int

    save_simplex : Optional[Union[Path,str]]

    minmax : Optional[List[Tuple[float,float]]]

    def __init__(
            self, 
            f : Callable[[np.typing.NDArray[np.float64]],Union[float,np.float64]], 
            points : np.typing.NDArray[np.float64],
            no_improve_thr:Optional[float]=None, 
            max_stagnations:Optional[int]=None, 
            max_iter:Optional[int]=None, 
            limit:bool=False, 
            limits:Optional[List[Tuple[float,float]]]=None, 
            maximize:bool=False,
            save_simplex:Optional[Union[Path,str]] = None,
            minmax:Optional[List[Tuple[float,float]]]=None):
        '''
            f: (function): function to optimize, must return a scalar score 
                and operate over a numpy array of the same dimensions as x_start
            points: (numpy array): initial position
            no_improve_thr (float): break after max_stagnations iterations with an improvement lower than no_improv_thr
            max_stagnations (int): break after max_stagnations iterations with an improvement lower than no_improv_thr
            max_iter: maximum iterations
            limit: if True, uses limits to limit parameter values on expansion and reflection
            limits: if limit=True, use this ordered list of tuples (min, max) to limit parameter values
            maximize: maximize objective function (instead of the default which is to minimize it)
            save_simplex: save simplex at this file path as comma separated values. Each row is a point. Last column is score.
        '''
        self.f = f
        self.points = points
        if no_improve_thr is not None:
            self.no_improve_thr = no_improve_thr
        if max_stagnations is not None:
            self.max_stagnations = max_stagnations
        if max_iter is not None:
            self.max_iter = max_iter
        self.iters = 0
        self.limit = limit
        self.limits = limits
        self.maximize = maximize
        self.current_points = None
        self.initial_points = None
        self.save_simplex = save_simplex
        self.minmax = minmax

    def step(self, res : List[PointScoreTuple]) -> List[PointScoreTuple]:
        # centroid of the lowest face
        pts = np.array([tup[0] for tup in res[:-1]])
        x0 = centroid(pts)

        new_res = self.reflection(res, x0, self.refl)
        if new_res is not None:
            exp_res = self.expansion(new_res, x0, self.ext)
            if exp_res is not None:
                new_res = exp_res
        else:
            new_res = self.contraction(res, x0, self.cont)
            if new_res is None:
                new_res = self.reduction(res, self.red)
        return new_res
    
    def run(self) -> PointScoreTuple:
        # initialize
        self.stagnations = 0
        self.current_points = self.sort(self.make_score(self.points), reverse=self.maximize)
        self.initial_points = self.current_points
        self.prev_best = self.f(self.current_points[0][0])

        # simplex iter
        iters = 0
        for iters in range(self.max_iter):
            self.iters = iters
            self.current_points = self.sort(self.current_points, reverse=self.maximize)
            best = self.current_points[0][1]
            logging.debug("Downhill simplex iter: %i, best score: %f" % (iters, best))
            if self.save_simplex:
                self.saveCurrentPoints(self.save_simplex)

            # break after max_stagnations iterations with no improvement
            if self.maximize:
                if best > self.prev_best + self.no_improve_thr:
                    logging.debug(f"Downhill simplex improved by {best - self.prev_best} at iteration {iters}")
                    self.stagnations = 0
                    self.prev_best = best
                else:
                    self.stagnations += 1
                    logging.debug(f"Downhill simplex not improved at iteration {iters}. Stagnations: {self.stagnations}")
            else:
                if best < self.prev_best - self.no_improve_thr:
                    logging.debug(f"Downhill simplex improved by {self.prev_best - best} at iteration {iters}")
                    self.stagnations = 0
                    self.prev_best = best
                else:
                    self.stagnations += 1
                    logging.debug(f"Downhill simplex not improved at iteration {iters}. Stagnations: {self.stagnations}")
        
            if self.stagnations >= self.max_stagnations:
                logging.debug("Downhill simplex breaking after reaching max_stagnations=%i " % self.stagnations)
                return self.current_points[0]

            # Downhill-Simplex algorithm
            new_res = self.step(self.current_points)

            self.current_points = new_res
        else:
            logging.warning("Downhill simplex No convergence after {} iterations".format(iters))
            return self.current_points[0]



    def sort(self, res : List[PointScoreTuple], reverse : bool=False) -> List[PointScoreTuple]:
        """
        Order the points according to their value.
        """
        return sorted(res, key = lambda x: x[1], reverse=reverse)

    def reflection(self, res : List[PointScoreTuple], x0 : Point, refl : float):
        """
        Reflection-extension step.
        refl: refl = 1 is a standard reflection
        """
        # reflected point and score
        xr = x0 + refl*(x0 - res[-1][0])
        xr = self.limitVertex(xr)
        rscore = np.float64(self.f(xr))

        new_res = res[:]

        progress = rscore > new_res[-2][1] if self.maximize else rscore < new_res[-2][1]
        logging.debug(f"Downhill simplex reflection. score: {"%f" % rscore}, progress: {progress}")
        if progress: # if this is a progress, we keep it
            new_res[-1] = (xr, rscore)
            return new_res
        return None

    def expansion(self, res : List[PointScoreTuple], x0 : Point, ext : float) -> Optional[List[PointScoreTuple]]:
        """
        ext: the amount of the expansion; ext=0 means no expansion
        """
        xr, rscore = res[-1]
        # if it is the new best point, we try to expand
        if (rscore > res[0][1] if self.maximize else rscore < res[0][1]):
            xe = xr + ext*(xr - x0)
            xe = self.limitVertex(xe)
            escore = np.float64(self.f(xe))
            if (escore > rscore if self.maximize else escore < rscore):
                logging.debug(f"Downhill simplex expansion score: {"%f" % escore}, progress: True")
                new_res = res[:]
                new_res[-1] = (xe, escore)
                return new_res
            logging.debug(f"Downhill simplex expansion score: {"%f" % escore}, progress: False")
            return None
        return None

    def contraction(self, res : List[PointScoreTuple], x0 : Point, cont : float) -> Optional[List[PointScoreTuple]]:
        """
        cont: contraction parameter: should be between zero and one
        """
        xc = x0 + cont*(res[-1][0] - x0)
        cscore = np.float64(self.f(xc))

        new_res = res[:]

        progress = cscore > new_res[-1][1] if self.maximize else cscore < new_res[-1][1]
        logging.debug(f"Downhill simplex contraction, score: {"%f" % cscore}, progress: {progress}")
        if progress:
            new_res[-1] = (xc, cscore)
            return new_res
        return None

    def reduction(self, res : List[PointScoreTuple], red : float) -> List[PointScoreTuple]:
        """
        red: reduction parameter: should be between zero and one
        """
        logging.debug("Downhill simplex reduction")
        pts = np.array([pts for (pts,_) in res])
        dirs = pts - pts[0]
        reduced_points = pts[0] + red*dirs
        new_res = self.make_score(reduced_points)
        return new_res

    def make_score(self, points : Iterable[Point]) -> List[PointScoreTuple]:
        res = []
        i = 0
        for pt in points:
            score = np.float64(self.f(pt))
            logging.debug(f"Donwhill simplex make_score point: {i}, score: {"%f" % score}")
            res.append((pt, score))
            i = i + 1
        return res

    def limitVertex(
            self,
            vertex : Iterable[float]
        ) -> np.typing.NDArray[np.float64]: # List[float]:
        """Limit parameters with self.limits only if self.limit=True

        Args:
            vertex (List[float]): parameter list

        Returns:
            List[float]: limited parameter list
        """
        limits : List[Tuple[float, float]]
        if self.limit:
            if self.limits is None:
                raise Exception("Can't run limit: limits not set")
            limits = self.limits
        elif self.minmax is not None:
            limits = self.minmax
        else:
            return np.array(vertex)
        limited : List[float] = []
        for i, p in enumerate(vertex):
            if len(limits) < i + 1:
                raise Exception("Missing limits for parameter index %i" % i)
            # logging.debug("i: %i, min: %f, p: %f, max: %f" % (i,self.limits[i][0], p, self.limits[i][1]))
            limited.append(limits[i][0] if p < limits[i][0] else p if p < limits[i][1] else limits[i][1])
        return np.array(limited)
    
    def saveCurrentPoints(self, output : Union[str,Path]) -> None:
        points = self.current_points_list
        if points is None:
            raise RuntimeError("vertex not set")
        with open(output,"w") as f:
            f.write("\n".join([",".join([f"{x:12.5e}" for x in p]) for p in points]))