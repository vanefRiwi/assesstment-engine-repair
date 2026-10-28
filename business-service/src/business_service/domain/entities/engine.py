from dataclasses import dataclass, field
from datetime import datetime
from uuid import UUID, uuid4

from business_service.domain.time import utc_now


@dataclass
class Engine:
    serial_number: str
    manufacturer: str
    model: str
    engine_type: str
    client_id: UUID
    capacity: str | None = None
    is_active: bool = True
    id: UUID = field(default_factory=uuid4)
    registered_at: datetime = field(default_factory=utc_now)
    created_at: datetime = field(default_factory=utc_now)
    updated_at: datetime = field(default_factory=utc_now)

    def __post_init__(self) -> None:
        self.serial_number = self.serial_number.strip().upper()
