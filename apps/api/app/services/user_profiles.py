from typing import Any

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.core.auth import AuthenticatedUser
from app.models import UserProfile

DEFAULT_ROLE = "researcher"


def get_or_create_user_profile(db: Session, current_user: AuthenticatedUser) -> UserProfile:
    profile = db.scalar(select(UserProfile).where(UserProfile.auth_user_id == current_user.auth_user_id))
    if profile is not None:
        return profile

    profile = UserProfile(
        auth_user_id=current_user.auth_user_id,
        email=current_user.email or "",
        full_name=_extract_full_name(current_user.claims),
        role=DEFAULT_ROLE,
    )
    db.add(profile)
    db.commit()
    db.refresh(profile)
    return profile


def _extract_full_name(claims: dict[str, Any] | None) -> str | None:
    if not claims:
        return None

    user_metadata = claims.get("user_metadata")
    if isinstance(user_metadata, dict):
        full_name = user_metadata.get("full_name") or user_metadata.get("name")
        if isinstance(full_name, str) and full_name.strip():
            return full_name.strip()

    full_name = claims.get("name")
    if isinstance(full_name, str) and full_name.strip():
        return full_name.strip()

    return None
