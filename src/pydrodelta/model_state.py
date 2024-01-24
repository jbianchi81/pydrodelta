class ModelState:
    def __init__(self, name:str=None, constraints:tuple=tuple(),default=None):
        if name is None:
            raise ValueError("Missing name")
        if len(constraints) < 2:
            raise ValueError("constraints must be a 2-length list or tuple")
        self.name = name
        self.min = float(constraints[0])
        self.max = float(constraints[1])
        self.default = float(default)
    
