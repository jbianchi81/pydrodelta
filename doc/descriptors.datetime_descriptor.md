# Table of Contents

* [pydrodelta.descriptors.datetime\_descriptor](#pydrodelta.descriptors.datetime_descriptor)
  * [DatetimeDescriptor](#pydrodelta.descriptors.datetime_descriptor.DatetimeDescriptor)

<a id="pydrodelta.descriptors.datetime_descriptor"></a>

# pydrodelta.descriptors.datetime\_descriptor

<a id="pydrodelta.descriptors.datetime_descriptor.DatetimeDescriptor"></a>

## DatetimeDescriptor Objects

```python
class DatetimeDescriptor()
```

Datetime descriptor

Reads: for absolute date: ISO-8601 datetime string or datetime.datetime. For relative date: dict (duration key-values) or float (decimal number of days). Defaults to None

Returns: None or datetime.datetime

