from __future__ import annotations

from users.repository import UserRepository

# Auth domain delegates credential lookups to UserRepository.
# Auth-specific logic (JWT generation, password hashing) lives in
# core/security.py and auth/service.py (not yet implemented).

__all__ = ["UserRepository"]
