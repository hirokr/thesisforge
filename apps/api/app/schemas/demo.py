from pydantic import BaseModel

from app.schemas.project import ProjectRead


class DemoProjectRead(BaseModel):
    project: ProjectRead
    document_count: int
    reference_count: int
