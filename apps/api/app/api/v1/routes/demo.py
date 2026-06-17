from fastapi import APIRouter, Depends, status
from sqlalchemy.orm import Session

from app.core.auth import AuthenticatedUser, get_current_user
from app.db.session import get_db
from app.schemas.demo import DemoProjectRead
from app.services.demo import load_demo_project

router = APIRouter(prefix="/demo", tags=["demo"])


@router.post("/project", response_model=DemoProjectRead, status_code=status.HTTP_201_CREATED)
def load_demo_project_route(
    current_user: AuthenticatedUser = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> DemoProjectRead:
    return load_demo_project(db, current_user)
