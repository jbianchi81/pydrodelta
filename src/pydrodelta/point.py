from typing import List

class Point:
    coordinates : List[float]

    @property
    def x(self):
        return self.coordinates[0]

    @property
    def y(self):
        return self.coordinates[1]

    def __init__(
            self,
            coordinates : List[float]
    ):    
        self.coordinates = coordinates
        if len(self.coordinates) < 2:
            raise ValueError("Bad coordinates: length must be >= 2")

    def __repr__(
            self
    ):
        return (
            f"Point(\n"
            f"  x={self.x},\n"
            f"  y={self.y},\n"
            f")"
        )
