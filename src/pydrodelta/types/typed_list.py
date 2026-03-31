from collections.abc import MutableSequence
from typing import Optional, Tuple, Union

class TypedList(MutableSequence):

    def __init__(self, oktype, *args, unique_id_property : Optional[Union[str,Tuple[str]]] = None, **fixed_kwargs):
        self.oktype = oktype
        self.list = list()
        self._unique_id_property = unique_id_property
        self._fixed_kwargs = fixed_kwargs
        self.extend(list(args))

    def check(self, v):
        if not isinstance(v, self.oktype):
            raise TypeError("%s must be of type %s" % (str(v),str(self.oktype)))

    def getUniqueId(self, value) -> tuple:
        keys = self._unique_id_property if type(self._unique_id_property) == tuple else tuple([self._unique_id_property])
        unique_id = []
        for key in keys:
            val = getattr(value, key)
            if val is None:
                raise ValueError("Unique key %s from element of type %s is None" % (key, self.oktype))
            unique_id.append(val)
        return tuple(unique_id)

    def assertUnique(self, value):
        unique_id = self.getUniqueId(value)
        for o in self.list:
            o_unique_id = self.getUniqueId(o)
            if o_unique_id == unique_id:
                raise ValueError("Unique id %s = %s already present in list" % (str(self._unique_id_property), str(o_unique_id)))
        # if type(self._unique_id_property) == str:
        #     if getattr(value, self._unique_id_property) in [getattr(o,self._unique_id_property) for o in self.list]:
        #         raise ValueError("Unique id property %s = %s already present in list" % (self._unique_id_property, getattr(value, self._unique_id_property)))
        # elif type(self._unique_id_property) == list:

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
        if self._unique_id_property is not None:
            self.assertUnique(value)
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