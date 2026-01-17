# common-widgets

Lightweight utilities for lazy properties and ordering-aware enums.

## LazyProperty

Descriptor that computes a value on first access, caches it on the instance, and can optionally record the property name.

**Features**
- Lazy evaluation; replaces the descriptor with the computed value.
- Optional tracking of computed properties via `mark=True` in `__lazy_properties__`.
- No extra dependencies; works with regular instance attributes.

**Example**
```python
from common_widgets.lazy import LazyProperty

class Foo:
    def __init__(self):
        self.data = 1

    @LazyProperty
    def boo(self):
        return self.data + 1

foo = Foo()
print(foo.boo)  # 2 (computed once, then cached)
print(foo.boo)  # 2 (returned from cache)
```

Tracking the lazy fields:
```python
class Bar:
    def __init__(self):
        self.data = 1

    @LazyProperty(mark=True)
    def boo(self):
        return self.data + 1

bar = Bar()
_ = bar.boo
print(bar.__lazy_properties__)  # ['boo']
```

## UnLazyProperty

Descriptor that invalidates previously cached lazy properties when set to `True`.

**Features**
- Clears cached values created by `LazyProperty` when toggled to `True`.
- Removes the `__lazy_properties__` tracker so values recompute on next access.
- Can be used as a simple flag; setting `False` leaves caches intact.

**Example**
```python
from common_widgets.lazy import LazyProperty, UnLazyProperty

class Foo:
    changed = UnLazyProperty(False)

    def __init__(self):
        self.data = 1

    @LazyProperty(mark=True)
    def boo(self):
        return self.data + 1

foo = Foo()
print(foo.boo)   # 2, cached
foo.data = 2
foo.changed = True  # invalidate cached lazy properties
print(foo.boo)   # 3, recomputed
```

## StageEnum

Ordering-aware `Enum` with optional transition flows for validating allowed state changes.

**Features**
- Explicit ordering via `_order_` or `Meta.ordering` enabling comparisons (`<`, `>`, etc.).
- Transition validation via `Meta.flows` and helpers `precedes`/`follows`.
- Convenience accessors: `index_`, `pre_enum_member`, `next_enum_member`, `pre_enum_members`, `next_enum_members`.

**Example**

```python
from common_widgets.stage_enum import StageEnum


class Status(StageEnum):
    _order_ = ("PENDING", "RUNNING", "DONE")

    class Meta:
        flows = {
            "PENDING": ["RUNNING"],
            "RUNNING": ["DONE"],
        }

    PENDING = "pending"
    RUNNING = "running"
    DONE = "done"


print(Status.PENDING < Status.DONE)  # True, ordered comparison
print(Status.RUNNING.precedes(Status.DONE))  # True, allowed transition
print(Status.DONE.follows(Status.RUNNING))  # True
print(Status.RUNNING.pre_enum_member)  # Status.PENDING
print(Status.PENDING.next_enum_members)  # [Status.RUNNING, Status.DONE]
```
