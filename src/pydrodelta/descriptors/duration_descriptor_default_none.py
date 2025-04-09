from pydrodelta.util import interval2timedelta
from .duration_descriptor import DurationDescriptor
default = None

class DurationDescriptorDefaultNone(DurationDescriptor):
    """Duration descriptor
    Parses dict of unit: value pairs (i.e., {"hours":1,"minutes":30})

    Return type: dateutil.relativedelta.relativedelta. 
    
    Default: None(hours=0)"""
    def __set__(self, instance, value):
        try:
            instance.__dict__[self._name] = interval2timedelta(value) if value is not None else default
        except ValueError:
            raise ValueError(f'"{self._name}" must be a duration') from None