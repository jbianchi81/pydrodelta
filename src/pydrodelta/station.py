from typing import Optional
from .types.point_dict import PointDict
from .point import Point
from textwrap import indent

class Station:
    id : int
    geom : Optional[Point]
    nombre : Optional[str]
    tabla : Optional[str]
    def __init__(
        self,
        id : int,
        geom : Optional[PointDict]=None,
        nombre : Optional[str]=None,
        tabla : Optional[str]=None
    ):
        self.id = id
        if geom is not None:
            if "coordinates" not in geom:
                raise ValueError("Missing coordinates in geom")
            self.geom = Point(geom["coordinates"])
        else:
            self.geom = None
        self.nombre = nombre
        self.tabla = tabla

    def __repr__(
            self
    ):
        geom_repr = indent(repr(self.geom), "    ")
        return (
            f"Station(\n"
            f"  id={self.id},\n"
            f"  geom=\n"
            f"{geom_repr},\n"
            f"  nombre={self.nombre},\n"
            f"  tabla={self.tabla}\n"
            f")"
        )
        
