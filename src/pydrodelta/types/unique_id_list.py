from typing import Generic, TypeVar, Union, Iterable, List, Protocol
from ..custom_errors import DuplicateKeyError

class HasId(Protocol):
    id: Union[int, str]

T = TypeVar("T", bound=HasId)

class UniqueIdList(List[T], Generic[T]):

    @classmethod
    def checkDuplicatesInInput(cls, items):
        unique_ids = list(set([item.id for item in items]))
        if len(unique_ids) < len(items):
            raise DuplicateKeyError(f"Duplicate ids found in list")
        
    def checkDuplicateId(self, id):
        if any(x.id == id for x in self):
            raise DuplicateKeyError(f"Duplicate id: {id}")

    def __init__(self, iterable: Iterable[T] = ()) -> None:
        super().__init__()

        for item in iterable:
            self.append(item)

    def append(self, item):
        self.checkDuplicateId(item.id)
        super().append(item)

    def extend(self, items):
        self.checkDuplicatesInInput(items)
        for item in items:
            self.checkDuplicateId(item.id)
        super().extend(items)

    def __setitem__(self, index, value):
        if isinstance(index, slice):
            self.checkDuplicatesInInput(value)
            for item in value:
                self.checkDuplicateId(item.id)
        else:
            self.checkDuplicateId(value.id)

        super().__setitem__(index, value)