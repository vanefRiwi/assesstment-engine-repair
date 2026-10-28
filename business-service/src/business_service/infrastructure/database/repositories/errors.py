from collections.abc import Iterator
from contextlib import contextmanager

from sqlalchemy.exc import IntegrityError

from business_service.domain.exceptions import ConflictError

CONSTRAINT_MESSAGES = {
    "uq_clients_document": "A client with this document already exists.",
    "uq_engines_serial_number": "An engine with this serial number already exists.",
    "uq_repair_orders_order_number": "The order number is already in use.",
    "fk_repair_orders_engine_client": "The client must be the current owner of the engine.",
}


@contextmanager
def translate_integrity_error() -> Iterator[None]:
    """Turns database constraint violations (e.g. concurrent duplicates) into domain conflicts."""
    try:
        yield
    except IntegrityError as error:
        constraint = getattr(getattr(error.orig, "diag", None), "constraint_name", None)
        raise ConflictError(
            CONSTRAINT_MESSAGES.get(constraint or "", "The data conflicts with existing records.")
        ) from error
