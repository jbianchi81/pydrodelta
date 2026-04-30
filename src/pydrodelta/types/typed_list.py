try:
    from collections.abc import MutableSequence  # runtime base
except ImportError:
    from typing import MutableSequence  # fallback (older Python)
from typing import Optional, Tuple, Union, Generic, TypeVar, Callable, overload, Iterable, Any

T = TypeVar("T")

class TypedList(MutableSequence, Generic[T]):

    def __init__(self, oktype, *args, unique_id_property : Optional[Union[str,Tuple[str, ...]]] = None, **fixed_kwargs):
        self.oktype = oktype
        self.list = list()
        self._unique_id_property = unique_id_property
        self._fixed_kwargs = fixed_kwargs
        self.extend(list(args))

    def check(self, v):
        if not isinstance(v, self.oktype):
            raise TypeError("%s must be of type %s" % (str(v),str(self.oktype)))

    def getUniqueId(self, value) -> tuple:
        if self._unique_id_property is None:
            return ()

        if isinstance(self._unique_id_property, str):
            keys = (self._unique_id_property,)
        else:
            keys = self._unique_id_property
        
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


    def __len__(self) -> int: return len(self.list)

    @overload
    def __getitem__(self, i: int) -> T: ...
    @overload
    def __getitem__(self, i: slice) -> "TypedList[T]": ...
    def __getitem__(self, i: Union[int, slice]) -> Union["TypedList[T]",T]:
        if isinstance(i, slice):
            return TypedList(
                self.oktype,
                *self.list[i],
                unique_id_property=self._unique_id_property,
                **self._fixed_kwargs
            )
        else:
            return self.list[i]

    def __delitem__(self, i : Union[int,slice]) -> None: del self.list[i]

    @overload
    def __setitem__(self, i : int, v: T) ->  None: ...
    @overload
    def __setitem__(self, i : slice, v: Iterable[T]) ->  None: ...
    def __setitem__(self, i : Union[slice,int], v: Union[T,Iterable[T],Any]) ->  None:
        if isinstance(i, slice):
            assert isinstance(v, Iterable)
            self.list[i] = [self.check_else_init(x) for x in v]
        else:
            self.list[i] = self.check_else_init(v)

    def insert(self, index : int, value : T) -> None:
        value = self.check_else_init(value)
        self.list.insert(index, value)

    def __str__(self):
        return str(self.list)

    def __repr__(self):
        return self.list.__repr__()
    
    def filter(self, fn: Callable[[T], bool]) -> "TypedList[T]":
        return TypedList(
            self.oktype,
            *[x for x in self if fn(x)],
            unique_id_property=self._unique_id_property,
            **self._fixed_kwargs
        )
