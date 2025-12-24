LAZY_PROPERTIES_FIELD_NAME = "__lazy_properties__"


class LazyProperty:
    """
    Classes with lazy loading properties

    The following example uses decorators to modify properties
    to achieve lazy loading of properties::

        class Foo(object):
            def __init__(self):
                self.data = 1

            @LazyProperty
            def boo(self):
                return self.data + 1

    ** Parameter ``mark``, Mark whether the lazy loading property name
    is placed inside the list in the object as a record.

    If `mark` is `True`, Follow the example above::

        >>> class Foo(object):
        ...    def __init__(self):
        ...        self.data = 1
        ...
        ...    @LazyProperty(mark=True)
        ...    def boo(self):
        ...        return self.data + 1

        >>> foo = Foo()
        >>> print(dir(foo))
        # ['__class__', '__delattr__', '__dict__', '__dir__', '__doc__', '__eq__',
        # '__format__', '__ge__', '__getattribute__', '__gt__', '__hash__', '__init__',
        # '__init_subclass__', '__le__', '__lt__', '__module__', '__ne__', '__new__',
        # '__reduce__', '__reduce_ex__', '__repr__', '__setattr__', '__sizeof__',
        # '__str__', '__subclasshook__', '__weakref__', 'boo', 'data']

        >>> foo.boo
        >>> print(dir(foo))
        # ['__class__', '__delattr__', '__dict__', '__dir__', '__doc__', '__eq__',
        # '__format__', '__ge__', '__getattribute__', '__gt__', '__hash__', '__init__',
        # '__init_subclass__', '__lazy_properties__', '__le__', '__lt__', '__module__',
        # '__ne__', '__new__', '__reduce__', '__reduce_ex__', '__repr__', '__setattr__',
        # '__sizeof__', '__str__', '__subclasshook__', '__weakref__', 'boo', 'data']

        >>> print(foo.__lazy_properties__)
        # ["foo"]

    """

    LAZY_PROPERTIES_FIELD_NAME = LAZY_PROPERTIES_FIELD_NAME or "__lazy_properties__"

    def __init__(self, func=None, mark=False):
        self.func = func
        self.mark = mark

    def __call__(self, func, *args, **kwargs):
        self.func = func
        return self

    def __get__(self, instance, owner):
        value = self.func(instance)
        setattr(instance, self.func.__name__, value)
        if self.mark:
            self.__add_lazy_property(instance, self.func.__name__)
        return value

    def __add_lazy_property(self, instance, name):
        """Send the lazy loading property name in the object for record"""

        lazy_properties = getattr(instance, self.LAZY_PROPERTIES_FIELD_NAME, None)
        if lazy_properties:
            lazy_properties.append(name)
        else:
            lazy_properties = [name]
            setattr(instance, self.LAZY_PROPERTIES_FIELD_NAME, lazy_properties)


class UnLazyProperty:
    """Use with class ``LazyProperty`` to
    unload properties that have been lazy loaded.

    The following example demonstrates a lazy loading property being reloaded::

        >>> class Foo(object):
        ...    changed = UnLazyProperty(False)
        ...
        ...    def __init__(self):
        ...        self.data = 1
        ...
        ...    @LazyProperty(mark=True)
        ...    def boo(self):
        ...        return self.data + 1

        >>> foo = Foo()
        >>> foo.boo # print 2
        >>> print(dir(foo))
        # ['__class__', '__delattr__', '__dict__', '__dir__', '__doc__', '__eq__',
        # '__format__', '__ge__', '__getattribute__', '__gt__', '__hash__', '__init__',
        # '__init_subclass__', '__lazy_properties__', '__le__', '__lt__', '__module__',
        # '__ne__', '__new__', '__reduce__', '__reduce_ex__', '__repr__', '__setattr__',
        # '__sizeof__', '__str__', '__subclasshook__', '__weakref__', 'boo', 'changed',
        # 'data']
        >>> print(foo.__lazy_properties__)
        # ["foo"]
        >>> foo.data = 2
        >>> foo.changed = True
        >>> print(dir(foo))
        # ['__class__', '__delattr__', '__dict__', '__dir__', '__doc__', '__eq__',
        # '__format__', '__ge__', '__getattribute__', '__gt__', '__hash__', '__init__',
        # '__init_subclass__', '__le__', '__lt__', '__module__', '__ne__', '__new__',
        # '__reduce__', '__reduce_ex__', '__repr__', '__setattr__', '__sizeof__',
        # '__str__', '__subclasshook__', '__weakref__', 'boo', 'changed', 'data']
        >>> foo.boo # print 3
        >>> print(dir(foo))
        # ['__class__', '__delattr__', '__dict__', '__dir__', '__doc__', '__eq__',
        # '__format__', '__ge__', '__getattribute__', '__gt__', '__hash__', '__init__',
        # '__init_subclass__', '__lazy_properties__', '__le__', '__lt__', '__module__',
        # '__ne__', '__new__', '__reduce__', '__reduce_ex__', '__repr__', '__setattr__',
        # '__sizeof__', '__str__', '__subclasshook__', '__weakref__', 'boo', 'changed',
        # 'data']


    """

    LAZY_PROPERTIES_FIELD_NAME = LAZY_PROPERTIES_FIELD_NAME or "__lazy_properties__"

    def __init__(self, value):
        self.value = value

    def __set__(self, instance, value):
        if value is True:
            lazy_properties = (
                getattr(instance, self.LAZY_PROPERTIES_FIELD_NAME, []) or []
            )
            if hasattr(instance, self.LAZY_PROPERTIES_FIELD_NAME):
                delattr(instance, self.LAZY_PROPERTIES_FIELD_NAME)
            for lazy_property in lazy_properties:
                delattr(instance, lazy_property)
        self.value = value
