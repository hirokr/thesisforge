from fastapi import APIRouter

from app.api.v1.routes import action_tasks, analysis_runs, demo, documents, me, projects, reports, supervisor_feedback

api_router = APIRouter()
api_router.include_router(me.router)
api_router.include_router(demo.router)
api_router.include_router(projects.router)
api_router.include_router(documents.router)
api_router.include_router(analysis_runs.router)
api_router.include_router(reports.router)
api_router.include_router(action_tasks.router)
api_router.include_router(supervisor_feedback.router)
