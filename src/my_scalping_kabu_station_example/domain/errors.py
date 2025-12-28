"""Domain-level errors."""

from __future__ import annotations


class DomainError(Exception):
    """Base domain error."""


class InvariantViolation(DomainError):
    """Raised when a domain invariant is violated."""

