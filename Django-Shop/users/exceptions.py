class AddressConstraintError(Exception):
    """Base exception for address domain errors."""


class CannotDeleteOnlyAddress(AddressConstraintError):
    """Raised when attempting to delete the user's only address."""

    pass
