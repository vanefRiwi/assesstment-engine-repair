from dataclasses import dataclass, field
from datetime import datetime
from uuid import UUID, uuid4

from business_service.domain.exceptions import BusinessRuleError, InvalidTransitionError
from business_service.domain.time import utc_now
from business_service.domain.value_objects.statuses import (
    ALLOWED_TRANSITIONS,
    ApprovalStatus,
    RepairStatus,
)


@dataclass
class StatusHistoryEntry:
    repair_order_id: UUID
    status: RepairStatus
    changed_by: UUID | None = None
    observations: str | None = None
    id: UUID = field(default_factory=uuid4)
    changed_at: datetime = field(default_factory=utc_now)


@dataclass
class RepairOrder:
    """Aggregate root for a repair. All lifecycle rules live here, not in routes or SQL."""

    order_number: str
    engine_id: UUID
    client_id: UUID
    received_at: datetime
    reported_problem: str
    technical_diagnosis: str | None = None
    repair_description: str | None = None
    technician_name: str | None = None
    estimated_delivery_at: datetime | None = None
    actual_delivery_at: datetime | None = None
    status: RepairStatus = RepairStatus.RECEIVED
    approval_status: ApprovalStatus = ApprovalStatus.NOT_REQUIRED
    approved_at: datetime | None = None
    approval_notes: str | None = None
    observations: str | None = None
    id: UUID = field(default_factory=uuid4)
    created_at: datetime = field(default_factory=utc_now)
    updated_at: datetime = field(default_factory=utc_now)

    def initial_history(self, changed_by: UUID | None) -> StatusHistoryEntry:
        return StatusHistoryEntry(
            repair_order_id=self.id,
            status=self.status,
            changed_by=changed_by,
            observations=self.observations,
            changed_at=self.created_at,
        )

    def change_status(
        self, new_status: RepairStatus, changed_by: UUID | None, observations: str | None = None
    ) -> StatusHistoryEntry:
        if new_status not in ALLOWED_TRANSITIONS[self.status]:
            raise InvalidTransitionError(f"Cannot change status from {self.status} to {new_status}.")

        if (
            self.status == RepairStatus.AWAITING_APPROVAL
            and new_status == RepairStatus.IN_REPAIR
            and self.approval_status != ApprovalStatus.APPROVED
        ):
            raise InvalidTransitionError("The client must approve the repair before it can start.")

        now = utc_now()
        if new_status == RepairStatus.AWAITING_APPROVAL:
            # Each proposal needs a fresh decision.
            self.approval_status = ApprovalStatus.PENDING
            self.approved_at = None
        if new_status == RepairStatus.DELIVERED:
            self.actual_delivery_at = now

        self.status = new_status
        self.updated_at = now
        return StatusHistoryEntry(
            repair_order_id=self.id,
            status=new_status,
            changed_by=changed_by,
            observations=observations,
            changed_at=now,
        )

    def record_approval(self, decision: ApprovalStatus, notes: str | None) -> None:
        if decision not in (ApprovalStatus.APPROVED, ApprovalStatus.REJECTED):
            raise BusinessRuleError("The approval decision must be APPROVED or REJECTED.")
        if self.status != RepairStatus.AWAITING_APPROVAL:
            raise BusinessRuleError("Approval can only be recorded while the order is awaiting approval.")

        now = utc_now()
        self.approval_status = decision
        self.approved_at = now if decision == ApprovalStatus.APPROVED else None
        self.approval_notes = notes
        self.updated_at = now

    def update_technical_details(
        self,
        technical_diagnosis: str | None = None,
        repair_description: str | None = None,
        technician_name: str | None = None,
        estimated_delivery_at: datetime | None = None,
    ) -> None:
        """Fill in work details as the repair progresses; omitted values are left unchanged."""
        if technical_diagnosis is not None:
            self.technical_diagnosis = technical_diagnosis
        if repair_description is not None:
            self.repair_description = repair_description
        if technician_name is not None:
            self.technician_name = technician_name
        if estimated_delivery_at is not None:
            self.estimated_delivery_at = estimated_delivery_at
        self.updated_at = utc_now()
