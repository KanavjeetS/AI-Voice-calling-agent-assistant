from fastapi import APIRouter

from models.schemas import DashboardStats
from services.analytics.metrics import get_dashboard_stats

router = APIRouter(prefix="/api/v1/dashboard", tags=["dashboard"])


@router.get("/stats", response_model=DashboardStats)
async def dashboard_stats() -> DashboardStats:
    return await get_dashboard_stats()
