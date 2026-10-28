from datetime import datetime
from typing import Annotated
from uuid import UUID

from pydantic import BaseModel, ConfigDict, StringConstraints

from business_service.presentation.api.schemas.common import StrictModel

Serial = Annotated[str, StringConstraints(strip_whitespace=True, min_length=3, max_length=100)]
Text100 = Annotated[str, StringConstraints(strip_whitespace=True, min_length=1, max_length=100)]
Text60 = Annotated[str, StringConstraints(strip_whitespace=True, min_length=1, max_length=60)]


class EngineCreate(StrictModel):
    serial_number: Serial
    manufacturer: Text100
    model: Text100
    engine_type: Text60
    capacity: Text60 | None = None
    client_id: UUID


class EngineUpdate(StrictModel):
    manufacturer: Text100 | None = None
    model: Text100 | None = None
    engine_type: Text60 | None = None
    capacity: Text60 | None = None
    client_id: UUID | None = None
    is_active: bool | None = None


class EngineResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: UUID
    serial_number: str
    manufacturer: str
    model: str
    engine_type: str
    capacity: str | None
    client_id: UUID
    registered_at: datetime
    is_active: bool
    created_at: datetime
    updated_at: datetime
