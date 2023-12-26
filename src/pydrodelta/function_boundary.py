class FunctionBoundary():
    """
    A boundary condition definition for a procedure function class
    """
    def __init__(self,params):
        self.name = params["name"]
        self.optional = params["optional"] if "optional" in params else False