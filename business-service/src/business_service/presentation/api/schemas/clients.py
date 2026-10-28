from datetime import datetime
from typing import Annotated
from uuid import UUID

from pydantic import BaseModel, ConfigDict, EmailStr, StringConstraints

from business_service.presentation.api.schemas.common import StrictModel

Name = Annotated[str, StringConstraints(strip_whitespace=True, min_length=2, max_length=150)]
DocumentType = Annotated[str, StringConstraints(strip_whitespace=True, min_length=1, max_length=20)]
DocumentNumber = Annotated[str, StringConstraints(strip_whitespace=True, min_length=3, max_length=40)]
Phone = Annotated[str, StringConstraints(strip_whitespace=True, max_length=30)]


class ClientCreate(StrictModel):
    name: Name
    document_type: DocumentType
    document_number: DocumentNumber
    email: EmailStr | None = None
    phone: Phone | None = None


class ClientUpdate(StrictModel):
    name: Name | None = None
    email: EmailStr | None = None
    phone: Phone | None = None
    is_active: bool | None = None


class ClientResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: UUID
    name: str
    document_type: str
    document_number: str
    email: str | None
    phone: str | None
    is_active: bool
    created_at: datetime
    updated_at: datetime
