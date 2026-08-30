"""Password hashing (bcrypt) and JWT issuing/validation for ``rcs.sysadmin``.

Deliberately dependency-light: it only needs ``bcrypt`` and ``PyJWT``, both of
which are already present in the runtime environment.
"""
from __future__ import annotations
import datetime as dt

import bcrypt
import jwt
from jwt import PyJWTError

from rcs.config import get_settings


class CredentialsError(Exception):
    """Raised when a username/password pair or a token cannot be accepted."""


# ---------------------------------------------------------------------------
# Passwords
# ---------------------------------------------------------------------------

def verify_password(plain_password: str, hashed_password: str) -> bool:
    """Constant-time check of ``plain_password`` against a bcrypt hash."""
    if not plain_password or not hashed_password:
        return False
    try:
        return bcrypt.checkpw(
            plain_password.encode("utf-8"),
            hashed_password.encode("utf-8"),
        )
    except (ValueError, TypeError):
        # Not a valid bcrypt hash (e.g. legacy plaintext row).
        return False


def get_password_hash(password: str) -> str:
    """Hash ``password`` with a freshly generated bcrypt salt."""
    return bcrypt.hashpw(password.encode("utf-8"), bcrypt.gensalt()).decode("utf-8")


# ---------------------------------------------------------------------------
# JSON Web Tokens
# ---------------------------------------------------------------------------

def create_access_token(subject: int | str, expires_delta: dt.timedelta | None = None) -> str:
    """Issue a signed JWT whose ``sub`` claim identifies the user.

    ``sub`` is stringified because the JWT spec requires it and because the
    audit middleware decodes the token without database access.
    """
    settings = get_settings()
    expire = dt.datetime.now(dt.timezone.utc) + (
        expires_delta
        or dt.timedelta(minutes=settings.access_token_expire_minutes)
    )
    payload = {"sub": str(subject), "exp": expire, "iat": dt.datetime.now(dt.timezone.utc)}
    return jwt.encode(payload, settings.secret_key, algorithm=settings.algorithm)


def decode_access_token(token: str) -> int | None:
    """Return the user id encoded in ``token`` or ``None`` when it is invalid.

    Raises nothing on malformed/expired tokens — callers treat ``None`` as
    "unauthenticated" so that the audit middleware never breaks a request just
    because a client sent a stale token.
    """
    settings = get_settings()
    try:
        payload = jwt.decode(
            token,
            settings.secret_key,
            algorithms=[settings.algorithm],
        )
    except PyJWTError:
        return None
    raw = payload.get("sub")
    if raw is None:
        return None
    try:
        return int(raw)
    except (TypeError, ValueError):
        return None
