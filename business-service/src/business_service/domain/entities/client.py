from dataclasses import dataclass, field
from datetime import datetime
from uuid import UUID, uuid4

from business_service.domain.time import utc_now


@dataclass
class Client:
    name: str
    document_type: str
    document_number: str
    email: str | None = None
    phone: str | None = None
    is_active: bool = True
    id: UUID = field(default_factory=uuid4)
    created_at: datetime = field(default_factory=utc_now)
    updated_at: datetime = field(default_factory=utc_now)

    def __post_init__(self) -> None:
        # Normalize identifiers so "cc 123" and "CC123 " count as the same document.
        self.name = self.name.strip()
        self.document_type = self.document_type.strip().upper()
        self.document_number = self.document_number.strip().replace(" ", "").upper()
        if self.email is not None:
            self.email = self.email.strip().lower()
