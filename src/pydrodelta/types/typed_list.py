import collections

class TypedList(collections.abc.MutableSequence):

    def __init__(self, oktype, *args):
        self.oktype = oktype
        self.list = list()
        self.extend(list(args))

    def check(self, v):
        if not isinstance(v, self.oktype):
            raise TypeError("%s must be of type %s" % (str(v),str(self.oktype)))

    def check_else_init(self,v):
        if isinstance(v, self.oktype):
            return v
        else:
            try:
                if isinstance(v,dict):
                    return self.oktype(**v)
                elif isinstance(v,(list,tuple)):
                    return self.oktype(*v)
                else:
                    return self.oktype(v)
            except TypeError as e:
                raise TypeError("Invalid item for mutable sequence. Unable to coerce to type %s" % str(self.oktype),e)

    def __len__(self): return len(self.list)

    def __getitem__(self, i): return self.list[i]

    def __delitem__(self, i): del self.list[i]

    def __setitem__(self, i, v):
        v = self.check_else_init(v)
        self.list[i] = v

    def insert(self, i, v):
        v = self.check_else_init(v)
        self.list.insert(i, v)

    def __str__(self):
        return str(self.list)

    def __repr__(self):
        return self.list.__repr__()