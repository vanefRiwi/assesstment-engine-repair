"""Business errors. The presentation layer maps each one to an HTTP status."""


class DomainError(Exception):
    """Base class for expected business errors."""


class NotFoundError(DomainError):
    pass


class ConflictError(DomainError):
    """Uniqueness or state conflict (HTTP 409)."""


class BusinessRuleError(DomainError):
    """The request is well formed but breaks a business rule (HTTP 400)."""


class InvalidTransitionError(BusinessRuleError):
    pass
