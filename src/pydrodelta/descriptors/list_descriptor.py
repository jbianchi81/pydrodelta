class ListDescriptor:
    """List descriptor with default None"""
    def __set_name__(self, owner, name):
        self._name = name

    def __get__(self, instance, owner):
        return instance.__dict__[self._name]

    def __set__(self, instance, value):
        try:
            instance.__dict__[self._name] = value if isinstance(value,list) else list(value) if value is not None else None
        except TypeError as e:
            raise TypeError("couldn't coerce type %s to a list: %s" % (type(value), e))
        except ValueError:
            raise ValueError(f'"{self._name}" must be a list') from None
