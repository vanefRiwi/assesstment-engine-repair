from datetime import datetime
from typing import Annotated, Literal
from uuid import UUID

from pydantic import AwareDatetime, BaseModel, ConfigDict, StringConstraints

from business_service.domain.value_objects.statuses import ApprovalStatus, RepairStatus
from business_service.presentation.api.schemas.common import StrictModel

LongText = Annotated[str, StringConstraints(strip_whitespace=True, min_length=1, max_length=5000)]
Technician = Annotated[str, StringConstraints(strip_whitespace=True, min_length=2, max_length=120)]


class RepairOrderCreate(StrictModel):
    engine_id: UUID
    client_id: UUID | None = None
    received_at: AwareDatetime
    reported_problem: LongText
    technical_diagnosis: LongText | None = None
    repair_description: LongText | None = None
    technician_name: Technician | None = None
    estimated_delivery_at: AwareDatetime | None = None
    observations: LongText | None = None


class StatusChange(StrictModel):
    status: RepairStatus
    observations: LongText | None = None
    technical_diagnosis: LongText | None = None
    repair_description: LongText | None = None
    technician_name: Technician | None = None
    estimated_delivery_at: AwareDatetime | None = None


class ApprovalDecision(StrictModel):
    decision: Literal["APPROVED", "REJECTED"]
    notes: LongText | None = None


class RepairOrderResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: UUID
    order_number: str
    engine_id: UUID
    client_id: UUID
    received_at: datetime
    reported_problem: str
    technical_diagnosis: str | None
    repair_description: str | None
    technician_name: str | None
    estimated_delivery_at: datetime | None
    actual_delivery_at: datetime | None
    status: RepairStatus
    approval_status: ApprovalStatus
    approved_at: datetime | None
    approval_notes: str | None
    observations: str | None
    created_at: datetime
    updated_at: datetime


class StatusHistoryResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: UUID
    status: RepairStatus
    changed_by: UUID | None
    changed_at: datetime
    observations: str | None


class StatusSummaryResponse(BaseModel):
    total: int
    by_status: dict[RepairStatus, int]
