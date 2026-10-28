"""Repair lifecycle and approval states, and the allowed transitions between them."""

from enum import StrEnum


class RepairStatus(StrEnum):
    RECEIVED = "RECEIVED"
    IN_DIAGNOSIS = "IN_DIAGNOSIS"
    AWAITING_APPROVAL = "AWAITING_APPROVAL"
    IN_REPAIR = "IN_REPAIR"
    IN_TESTING = "IN_TESTING"
    COMPLETED = "COMPLETED"
    DELIVERED = "DELIVERED"


class ApprovalStatus(StrEnum):
    NOT_REQUIRED = "NOT_REQUIRED"
    PENDING = "PENDING"
    APPROVED = "APPROVED"
    REJECTED = "REJECTED"


ALLOWED_TRANSITIONS: dict[RepairStatus, frozenset[RepairStatus]] = {
    RepairStatus.RECEIVED: frozenset({RepairStatus.IN_DIAGNOSIS}),
    RepairStatus.IN_DIAGNOSIS: frozenset({RepairStatus.AWAITING_APPROVAL}),
    # Back to diagnosis lets the workshop revise the proposal after a rejection.
    RepairStatus.AWAITING_APPROVAL: frozenset({RepairStatus.IN_REPAIR, RepairStatus.IN_DIAGNOSIS}),
    RepairStatus.IN_REPAIR: frozenset({RepairStatus.IN_TESTING}),
    RepairStatus.IN_TESTING: frozenset({RepairStatus.COMPLETED, RepairStatus.IN_REPAIR}),
    RepairStatus.COMPLETED: frozenset({RepairStatus.DELIVERED}),
    RepairStatus.DELIVERED: frozenset(),
}
