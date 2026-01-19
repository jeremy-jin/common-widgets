from common_widgets.stage_enum import StageEnum
import pytest


class Status(StageEnum):
    PENDING = "pending"
    RUNNING = "running"
    DONE = "done"
    CLOSED = "expired"

    class Meta:
        flows = {
            "PENDING": ["RUNNING"],
            "RUNNING": ["DONE", "expired"],
        }
        ordering = ["PENDING", "RUNNING", "DONE"]


class TestStageEnum:
    def test_follows(self):
        assert Status.RUNNING.follows(Status.PENDING)
        assert not Status.DONE.follows(Status.PENDING)

    def test_precedes(self):
        assert Status.PENDING.precedes(Status.RUNNING)
        assert not Status.PENDING.precedes(Status.DONE)

    def test_comparison(self):
        assert Status.PENDING < Status.RUNNING
        assert Status.DONE > Status.RUNNING
        assert Status.PENDING <= Status.PENDING
        assert Status.DONE >= Status.RUNNING

    def test_subtraction(self):
        assert (Status.DONE - Status.PENDING) == [Status.RUNNING]
        assert (Status.RUNNING - Status.PENDING) == []

    def test_subtraction_forward_branch(self):
        assert (Status.PENDING - Status.RUNNING) == []
        assert (Status.PENDING - Status.DONE) == [Status.RUNNING]

    def test_member_coercion_and_comparable(self):
        assert Status._member__(Status.PENDING) is Status.PENDING
        assert Status._member__("pending") is Status.PENDING
        assert Status.is_comparable("pending")
        assert Status.is_comparable(Status.PENDING)
        assert not Status.is_comparable("missing")
        assert not Status.is_comparable(123)
        assert not Status.is_comparable("expired")

    def test_neighbor_accessors(self):
        assert Status.RUNNING.pre_enum_member is Status.PENDING
        assert Status.RUNNING.next_enum_member is Status.DONE
        assert Status.RUNNING.pre_enum_members == [Status.PENDING]
        assert Status.RUNNING.next_enum_members == [Status.DONE]
        assert Status.PENDING.pre_enum_members == []
        assert Status.DONE.next_enum_members == []
        with pytest.raises(IndexError):
            _ = Status.PENDING.pre_enum_member
        with pytest.raises(IndexError):
            _ = Status.DONE.next_enum_member
