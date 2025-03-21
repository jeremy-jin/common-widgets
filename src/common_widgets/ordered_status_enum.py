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

from enum import Enum


class OrderedStatusEnum(Enum):
    @property
    def flow(self):  # pragma: no cover
        return self.set_flow()

    def set_flow(self):
        return {}

    def follows(self, other):
        """
        Returns ``True`` if this status can be transitioned from ``other``
        status

        """
        allowed_next = self.flow.get(other) or []
        return self in allowed_next

    def precedes(self, other):
        """
        Returns ``True`` if this status can be transitioned to ``other``
        status

        """
        allowed_next = self.flow.get(self) or []
        return other in allowed_next

    @property
    def cus_ordered(self):
        return self.set_ordered()

    def set_ordered(self):
        return []

    @property
    def ordered_statuses(self):
        if self.cus_ordered:
            return self.cus_ordered
        else:
            return list(self.__class__.__members__.values())

    @property
    def index_(self):
        return self.ordered_statuses.index(self)

    @property
    def statuses_len(self):
        return len(self.ordered_statuses)

    def __le__(self, other):
        return self.index_ <= other.index_

    def __lt__(self, other):
        return self.index_ < other.index_

    def __ge__(self, other):
        return self.index_ >= other.index_

    def __gt__(self, other):
        return self.index_ > other.index_

    def __sub__(self, other):
        if self.index_ <= other.index_:
            return self.ordered_statuses[self.index_ + 1 : other.index_]
        else:
            return self.ordered_statuses[
                -self.statuses_len + other.index_ + 1 : -self.statuses_len + self.index_
            ]

    @property
    def pre_status(self):
        index = self.index_ - 1
        if index < 0:
            raise IndexError("No previous")
        return self.ordered_statuses[index]

    @property
    def next_status(self):
        index = self.index_ + 1
        return self.ordered_statuses[index]

    @property
    def pre_statuses(self):
        return self.ordered_statuses[: self.index_]

    @property
    def next_statuses(self):
        return self.ordered_statuses[self.index_ + 1:]