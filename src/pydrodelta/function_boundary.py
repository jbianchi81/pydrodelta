class FunctionBoundary():
    """
    A boundary condition definition for a procedure function class
    """
    def __init__(self,params):
        self.name = params["name"]
        self.optional = bool(params["optional"]) if "optional" in params else False
        self.warmup_only = bool(params["warmup_only"]) if "warmup_only" in params else False
        self.compute_statistics = bool(params["compute_statistics"]) if "compute_statistics" in params else True
    def __dict__(self):
        return {
            "name": self.name,
            "optional": self.optional,
            "warmup_only": self.warmup_only,
            "compute_statistics": self.compute_statistics
        }