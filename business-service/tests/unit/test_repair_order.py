from datetime import UTC, datetime
from uuid import uuid4

import pytest

from business_service.domain.entities.repair_order import RepairOrder
from business_service.domain.exceptions import BusinessRuleError, InvalidTransitionError
from business_service.domain.value_objects.statuses import ApprovalStatus, RepairStatus

USER = uuid4()


def new_order() -> RepairOrder:
    return RepairOrder(
        order_number="REP-2026-000001",
        engine_id=uuid4(),
        client_id=uuid4(),
        received_at=datetime(2026, 10, 27, tzinfo=UTC),
        reported_problem="Does not start",
    )


def advance(order: RepairOrder, *statuses: RepairStatus) -> None:
    for status in statuses:
        order.change_status(status, USER)


def test_new_order_starts_received_with_initial_history():
    order = new_order()
    entry = order.initial_history(USER)
    assert order.status == RepairStatus.RECEIVED
    assert entry.status == RepairStatus.RECEIVED
    assert entry.changed_by == USER


def test_rejects_skipping_steps():
    with pytest.raises(InvalidTransitionError):
        new_order().change_status(RepairStatus.DELIVERED, USER)


def test_entering_awaiting_approval_sets_pending():
    order = new_order()
    advance(order, RepairStatus.IN_DIAGNOSIS, RepairStatus.AWAITING_APPROVAL)
    assert order.approval_status == ApprovalStatus.PENDING


def test_repair_cannot_start_without_approval():
    order = new_order()
    advance(order, RepairStatus.IN_DIAGNOSIS, RepairStatus.AWAITING_APPROVAL)
    with pytest.raises(InvalidTransitionError):
        order.change_status(RepairStatus.IN_REPAIR, USER)

    order.record_approval(ApprovalStatus.REJECTED, "Too expensive")
    with pytest.raises(InvalidTransitionError):
        order.change_status(RepairStatus.IN_REPAIR, USER)
    assert order.approved_at is None


def test_full_lifecycle_sets_approval_and_delivery_dates():
    order = new_order()
    advance(order, RepairStatus.IN_DIAGNOSIS, RepairStatus.AWAITING_APPROVAL)
    order.record_approval(ApprovalStatus.APPROVED, "Client agreed")
    assert order.approved_at is not None

    advance(
        order,
        RepairStatus.IN_REPAIR,
        RepairStatus.IN_TESTING,
        RepairStatus.IN_REPAIR,  # failed test goes back to repair
        RepairStatus.IN_TESTING,
        RepairStatus.COMPLETED,
        RepairStatus.DELIVERED,
    )
    assert order.status == RepairStatus.DELIVERED
    assert order.actual_delivery_at is not None


def test_rejected_proposal_can_be_rediagnosed_and_needs_a_new_decision():
    order = new_order()
    advance(order, RepairStatus.IN_DIAGNOSIS, RepairStatus.AWAITING_APPROVAL)
    order.record_approval(ApprovalStatus.REJECTED, None)
    advance(order, RepairStatus.IN_DIAGNOSIS, RepairStatus.AWAITING_APPROVAL)
    assert order.approval_status == ApprovalStatus.PENDING


def test_approval_only_while_awaiting_approval():
    with pytest.raises(BusinessRuleError):
        new_order().record_approval(ApprovalStatus.APPROVED, None)


def test_delivered_is_final():
    order = new_order()
    advance(order, RepairStatus.IN_DIAGNOSIS, RepairStatus.AWAITING_APPROVAL)
    order.record_approval(ApprovalStatus.APPROVED, None)
    advance(order, RepairStatus.IN_REPAIR, RepairStatus.IN_TESTING, RepairStatus.COMPLETED, RepairStatus.DELIVERED)
    for status in RepairStatus:
        with pytest.raises(InvalidTransitionError):
            order.change_status(status, USER)
