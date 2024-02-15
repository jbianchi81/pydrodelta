from datetime import timedelta
from pydrodelta.util import interval2timedelta

class DurationDescriptor:
    """Duration descriptor
    Parses dict of unit: value pairs (i.e., {"hours":1,"minutes":30})

    Return type: datetime.timedelta. 
    
    Default: timedelta(hours=0)"""
    def __set_name__(self, owner, name):
        self._name = name

    def __get__(self, instance, owner):
        return instance.__dict__[self._name]

    def __set__(self, instance, value):
        try:
            instance.__dict__[self._name] = interval2timedelta(value) if value is not None else timedelta(hours=0)
        except ValueError:
            raise ValueError(f'"{self._name}" must be a duration') from None