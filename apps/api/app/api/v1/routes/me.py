from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.core.auth import AuthenticatedUser, get_current_user
from app.db.session import get_db
from app.schemas.user_profile import UserProfileRead
from app.services.user_profiles import get_or_create_user_profile

router = APIRouter(prefix="/me", tags=["users"])


@router.get("", response_model=UserProfileRead)
def read_current_user_profile(
    current_user: AuthenticatedUser = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> UserProfileRead:
    return get_or_create_user_profile(db, current_user)
