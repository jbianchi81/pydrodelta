import collections
from typing import List

class EnhancedTypedList(collections.abc.MutableSequence):
    """
    A list of the specified type. On setting/appending/extending, tries to coerce the items to the given type by calling its constructor, optionally adding fixed_kwargs. If unique_id_property is set, it checks for duplicates using that property of the items. If valid_items_list is set together with the latter, it checks that the identifiers are present within the given list of dict, and any additional properties in the matched dict are set in the item.
    """
    def __init__(self, oktype, *args, unique_id_property : str = None, valid_items_list : List[dict] = None, allow_additional_ids : bool = False, allow_missing : bool = True, **fixed_kwargs):
        """EnhancedTypedList class constructor

        Args:
            oktype (type): try to coerce *args into this type
            *args: list of elements. If not provided, it will set an empty list.
            unique_id_property (str, optional): If set, it checks for duplicates using that property of the items. Defaults to None.
            valid_items_list (List[dict], optional): If set together with the unique_id_property, it checks that the identifiers are present within the given list of dict, and any additional properties in the matched dict are set in the item. Defaults to None.
            allow_additional_ids (bool): If set to True, allows identifiers not included in valid_items_list. Defaults to False
            allow_missing (bool). If false, assert if every item's in valid_items_list is present in the list. Defaults to True
            **fixed_kwargs: passed to the type constructor of every item of the list
        """
        self.oktype = oktype
        self.list = list()
        self._unique_id_property = unique_id_property
        self._valid_items_list = valid_items_list
        self._allow_additional_ids = allow_additional_ids
        self._allow_missing = allow_missing
        self._fixed_kwargs = fixed_kwargs
        self.extend(list(args))
        if unique_id_property and valid_items_list and not allow_missing:
            self.assert_missing_ids()
    
    def assert_missing_ids(self):
        for v in self._valid_items_list:
            if v[self._unique_id_property] not in [getattr(x, self._unique_id_property) for x in self.list]:
                raise ValueError("Missing required element with id='%s' in list" % v[self._unique_id_property])

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
        if self._unique_id_property is not None:
            if getattr(value, self._unique_id_property) in [getattr(o,self._unique_id_property) for o in self.list]:
                raise ValueError("Unique id property %s = %s already present in list" % (self._unique_id_property, getattr(value, self._unique_id_property)))
            if self._valid_items_list is not None:
                if getattr(value, self._unique_id_property) not in [item[self._unique_id_property] for item in self._valid_items_list]:
                    if not self._allow_additional_ids:
                        raise ValueError("typed list item identifier %s not valid - not found in _valid_items_list" % getattr(value, self._unique_id_property))
                else:
                    item = [i for i in self._valid_items_list if i[self._unique_id_property] == getattr(value, self._unique_id_property)][0]
                    for key, val in item.items():
                        if key == self._unique_id_property:
                            continue
                        setattr(value, key, val)               
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
    
    def getById(self, id):
        if self._unique_id_property is None:
            raise TypeError("Can't retrieve element by id: unique_id_property not set")
        if id not in [getattr(i, self._unique_id_property) for i in self.list]:
            raise ValueError("Element with identifier = %s not found" % str(id))
        return [i for i in self.list if getattr(i,self._unique_id_property) == id][0]

    def getIndex(self, id):
        if self._unique_id_property is None:
            raise TypeError("Can't retrieve element by id: unique_id_property not set")
        if id not in [getattr(i, self._unique_id_property) for i in self.list]:
            raise ValueError("Element with identifier = %s not found" % str(id))
        return [i for i, v in enumerate(self.list) if getattr(self.list[i],self._unique_id_property) == id][0]
    
    def replace(self,index : int, item):
        popped = self.list.pop(index)
        self.insert(index, item)
        if not self._allow_missing:
            self.assert_missing_ids()
        return popped