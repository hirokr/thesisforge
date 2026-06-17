from fastapi import APIRouter

from app.api.v1.routes import analysis_runs, documents, me, projects, reports

api_router = APIRouter()
api_router.include_router(me.router)
api_router.include_router(projects.router)
api_router.include_router(documents.router)
api_router.include_router(analysis_runs.router)
api_router.include_router(reports.router)
