from uuid import UUID

from pydantic import BaseModel, ConfigDict


class UserProfileRead(BaseModel):
    id: UUID
    auth_user_id: str
    email: str
    full_name: str | None
    role: str
    institution: str | None

    model_config = ConfigDict(from_attributes=True)
