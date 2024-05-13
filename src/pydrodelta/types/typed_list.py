import collections

class TypedList(collections.abc.MutableSequence):

    def __init__(self, oktype, *args, unique_id_property : str = None, **fixed_kwargs):
        self.oktype = oktype
        self.list = list()
        self._unique_id_property = unique_id_property
        self._fixed_kwargs = fixed_kwargs
        self.extend(list(args))

    def check(self, v):
        if not isinstance(v, self.oktype):
            raise TypeError("%s must be of type %s" % (str(v),str(self.oktype)))

    def check_else_init(self,v):
        value = None
        if isinstance(v, self.oktype):
            value = v
        else:
            try:
                if isinstance(v,dict):
                    value = self.oktype(**v,**self._fixed_kwargs)
                elif isinstance(v,(list,tuple)):
                    value = self.oktype(*v,**self._fixed_kwargs)
                else:
                    value = self.oktype(v,**self._fixed_kwargs)
            except TypeError as e:
                raise TypeError("Invalid item for mutable sequence. Unable to coerce to type %s" % str(self.oktype),e)
        if self._unique_id_property is not None and getattr(value, self._unique_id_property) in [getattr(o,self._unique_id_property) for o in self.list]:
            raise ValueError("Unique id property %s = %s already present in list" % (self._unique_id_property, getattr(value, self._unique_id_property)))
        return value


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