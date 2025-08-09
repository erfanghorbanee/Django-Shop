class AddressConstraintError(Exception):
    """Base exception for address domain errors."""


class CannotDeleteOnlyAddress(AddressConstraintError):
    """Raised when attempting to delete the user's only address."""

    default_message = "You cannot delete your only address."

    def __init__(self, message: str | None = None):
        super().__init__(message or self.default_message)


class CannotDemoteOnlyPrimary(AddressConstraintError):
    """Raised when attempting to unset the only primary address."""

    default_message = "You must have at least one primary address."

    def __init__(self, message: str | None = None):
        super().__init__(message or self.default_message)
