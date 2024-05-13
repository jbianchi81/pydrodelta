# Table of Contents

* [pydrodelta.types.enhanced\_typed\_list](#pydrodelta.types.enhanced_typed_list)
  * [EnhancedTypedList](#pydrodelta.types.enhanced_typed_list.EnhancedTypedList)
    * [\_\_init\_\_](#pydrodelta.types.enhanced_typed_list.EnhancedTypedList.__init__)

<a id="pydrodelta.types.enhanced_typed_list"></a>

# pydrodelta.types.enhanced\_typed\_list

<a id="pydrodelta.types.enhanced_typed_list.EnhancedTypedList"></a>

## EnhancedTypedList Objects

```python
class EnhancedTypedList(collections.abc.MutableSequence)
```

A list of the specified type. On setting/appending/extending, tries to coerce the items to the given type by calling its constructor, optionally adding fixed_kwargs. If unique_id_property is set, it checks for duplicates using that property of the items. If valid_items_list is set together with the latter, it checks that the identifiers are present within the given list of dict, and any additional properties in the matched dict are set in the item.

<a id="pydrodelta.types.enhanced_typed_list.EnhancedTypedList.__init__"></a>

#### \_\_init\_\_

```python
def __init__(oktype,
             *args,
             unique_id_property: str = None,
             valid_items_list: List[dict] = None,
             allow_additional_ids: bool = False,
             allow_missing: bool = True,
             **fixed_kwargs)
```

EnhancedTypedList class constructor

**Arguments**:

- `oktype` _type_ - try to coerce *args into this type
- `*args` - list of elements. If not provided, it will set an empty list.
- `unique_id_property` _str, optional_ - If set, it checks for duplicates using that property of the items. Defaults to None.
- `valid_items_list` _List[dict], optional_ - If set together with the unique_id_property, it checks that the identifiers are present within the given list of dict, and any additional properties in the matched dict are set in the item. Defaults to None.
- `allow_additional_ids` _bool_ - If set to True, allows identifiers not included in valid_items_list. Defaults to False
  allow_missing (bool). If false, assert if every item's in valid_items_list is present in the list. Defaults to True
- `**fixed_kwargs` - passed to the type constructor of every item of the list

