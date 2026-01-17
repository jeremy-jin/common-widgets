"""Ordering-aware Enum with optional transition flows.

Members gain comparison based on a declared ordering and helpers to validate
allowed transitions between states via `follows` and `precedes`.
"""

from enum import Enum, EnumMeta


__all__ = ["StageEnum"]


class MetaOptions(object):  # pragma: no cover
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
        if _ordering is not None:
            for _o in _ordering:
                ordering.append(self._get_enum_member(_o))
        else:
            ordering = _order_ or []

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


class StageEnumMetaclass(EnumMeta):  # pragma: no cover
    @classmethod
    def __prepare__(metacls, cls, bases, **kwargs):
        enum_dict = super().__prepare__(cls, bases, **kwargs)
        enum_dict._ignore = ["Meta"]
        return enum_dict

    def __new__(mcs, name, bases, attrs):
        attr_meta = attrs.get("Meta", None)
        new_class = super(StageEnumMetaclass, mcs).__new__(mcs, name, bases, attrs)
        new_class.meta = MetaOptions(new_class, attr_meta) if attr_meta else None

        return new_class


class StageEnum(Enum, metaclass=StageEnumMetaclass):  # pragma: no cover
    """Enum with explicit ordering and transition helpers.

    Define ordering via `_order_` or `Meta.ordering` and allowed transitions
    via `Meta.flows` mapping members (names or values) to lists of next members.
    """

    @classmethod
    def _member__(cls, value):
        return cls(value) if not isinstance(value, StageEnum) else value

    def follows(self, other):
        """
        Returns ``True`` if this member can be transitioned from ``other`` member
        """

        other = self._member__(other)
        allowed_next = self.meta.flows.get(other) or []
        return self in allowed_next

    def precedes(self, other):
        """
        Returns ``True`` if this member can be transitioned to ``other`` member
        """

        other = self._member__(other)
        allowed_next = self.meta.flows.get(self) or []
        return other in allowed_next

    @property
    def index_(self):
        return self.meta.ordering.index(self)

    @classmethod
    def is_comparable(cls, member):
        try:
            member = cls._member__(member)
            if member in cls.meta.ordering:
                return True
        except ValueError:
            return False

        return False

    def __le__(self, other):
        other = self._member__(other)
        return self.index_ <= other.index_

    def __lt__(self, other):
        other = self._member__(other)
        return self.index_ < other.index_

    def __ge__(self, other):
        other = self._member__(other)
        return self.index_ >= other.index_

    def __gt__(self, other):
        other = self._member__(other)
        return self.index_ > other.index_

    def __sub__(self, other):
        other = self._member__(other)
        if self.index_ <= other.index_:
            return self.meta.ordering[self.index_ + 1 : other.index_]
        else:
            return self.meta.ordering[
                -len(self.meta.ordering)
                + other.index_
                + 1 : -len(self.meta.ordering)
                + self.index_
            ]

    @property
    def pre_enum_member(self):
        index = self.index_ - 1
        if index < 0:
            raise IndexError("No previous")
        return self.meta.ordering[index]

    @property
    def next_enum_member(self):
        index = self.index_ + 1
        return self.meta.ordering[index]

    @property
    def pre_enum_members(self):
        return self.meta.ordering[: self.index_]

    @property
    def next_enum_members(self):
        return self.meta.ordering[self.index_ + 1 :]
