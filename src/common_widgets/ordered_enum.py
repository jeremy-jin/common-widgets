"""
在 Python 中，enum 的成员是有顺序的。enum 成员的顺序是它们在类定义中出现的顺序。你可以使用 list() 函数将 enum 转换为列表，以查看其成员的顺序。
以下是一个示例：

    >>> from enum import Enum
    ... class Color(Enum):
    ...     RED = 1
    ...     GREEN = 2
    ...     BLUE = 3
    ... # 将枚举转换为列表以查看顺序
    ... print(list(Color))

输出将是：
    [<Color.RED: 1>, <Color.GREEN: 2>, <Color.BLUE: 3>]

在这个示例中，Color.RED 是第一个成员，Color.GREEN 是第二个成员，Color.BLUE 是第三个成员。
这表明 enum 成员的顺序是它们在类定义中出现的顺序。
"""

from enum import Enum, EnumMeta, _EnumDict


class MetaOptions(object):
    def __init__(self, cls, meta, *args, **kwargs):
        self.cls = cls
        self.meta = meta

        self.ordering = self.set_ordering()
        self.flows = self.set_flows()

    def _get_enum_member(self, value):
        try:
            enum_member = self.cls[value.upper()]
        except KeyError:
            enum_member = self.cls(value)

        return enum_member

    def set_ordering(self):
        _order_ = getattr(self.cls, "_order_", None)
        _ordering = getattr(self.meta, "ordering", None)
        ordering = []
        if _order_ is not None:
            ordering = _order_
        else:
            for _o in _ordering:
                ordering.append(self._get_enum_member(_o))
        return ordering

    def set_flows(self):
        _flows = getattr(self.meta, "flows", {})
        flows = {}
        for key, value in _flows.items():
            flow_list = []
            for v in value:
                flow_list.append(self._get_enum_member(v))
            flows[self._get_enum_member(key)] = flow_list
        return flows


class OrderedEnumMetaclass(EnumMeta):
    @classmethod
    def __prepare__(metacls, cls, bases, **kwds):
        # check that previous enum members do not exist
        metacls._check_for_existing_members(cls, bases)
        # create the namespace dict
        enum_dict = _EnumDict()
        enum_dict._ignore = ["Meta"]
        enum_dict._cls_name = cls
        # inherit previous flags and _generate_next_value_ function
        member_type, first_enum = metacls._get_mixins_(cls, bases)
        if first_enum is not None:
            enum_dict['_generate_next_value_'] = getattr(
                first_enum, '_generate_next_value_', None,
            )
        return enum_dict

    def __new__(mcs, name, bases, attrs):
        attr_meta = attrs.get("Meta", None)
        new_class = super(OrderedEnumMetaclass, mcs).__new__(mcs, name, bases, attrs)
        if attr_meta:
            setattr(new_class, "meta", MetaOptions(new_class, attr_meta))

        return new_class


class OrderedEnum(Enum, metaclass=OrderedEnumMetaclass):
    @classmethod
    def _format__(cls, value):
        return cls(value) if not isinstance(value, OrderedEnum) else value

    def follows(self, other):
        """
        Returns ``True`` if this member can be transitioned from ``other`` member
        """

        other = self._format__(other)
        allowed_next = self._meta.flows.get(other) or []
        return self in allowed_next

    def precedes(self, other):
        """
        Returns ``True`` if this member can be transitioned to ``other`` member
        """

        other = self._format__(other)
        allowed_next = self._meta.flows.get(self) or []
        return other in allowed_next

    @property
    def index_(self):
        return self._meta.ordering.index(self)

    @classmethod
    def is_comparable(cls, member):
        try:
            member = cls._format__(member)
            if member in cls.meta.ordering:
                return True
        except ValueError:
            return False

        return False

    def __le__(self, other):
        other = self._format__(other)
        return self.index_ <= other.index_

    def __lt__(self, other):
        other = self._format__(other)
        return self.index_ < other.index_

    def __ge__(self, other):
        other = self._format__(other)
        return self.index_ >= other.index_

    def __gt__(self, other):
        other = self._format__(other)
        return self.index_ > other.index_

    def __sub__(self, other):
        other = self._format__(other)
        if self.index_ <= other.index_:
            return self.meta.ordering[self.index_ + 1 : other.index_]
        else:
            return self.meta.ordering[
                -self.meta.len_ordering + other.index_ + 1 : -self.meta.len_ordering + self.index_
            ]

    @property
    def pre_enum_member(self):
        index = self.index_ - 1
        if index < 0:
            raise IndexError("No previous")
        return self.meta.len_ordering[index]

    @property
    def next_enum_member(self):
        index = self.index_ + 1
        return self.meta.len_ordering[index]

    @property
    def pre_enum_members(self):
        return self.meta.len_ordering[: self.index_]

    @property
    def next_enum_members(self):
        return self.meta.len_ordering[self.index_ + 1:]
