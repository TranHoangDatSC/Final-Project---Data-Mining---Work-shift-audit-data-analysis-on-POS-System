"""
src/api/data_summary.py
GET /api/summary/{phase_id} → KPI numbers cho phase cụ thể
GET /api/summary            → KPI tổng hợp tất cả phases
"""

from fastapi import APIRouter, HTTPException
from src.schemas.phase import PhaseSummaryResponse
from src.services.summary_builder import PHASE_BUILDERS

router = APIRouter()


@router.get("/summary/{phase_id}", response_model=PhaseSummaryResponse)
async def get_phase_summary(phase_id: str):
    """Trả về KPI cards cho một phase."""
    if phase_id not in PHASE_BUILDERS:
        raise HTTPException(status_code=404, detail=f"Phase {phase_id} not found")
    kpis = PHASE_BUILDERS[phase_id]()
    return PhaseSummaryResponse(phase_id=int(phase_id), kpis=kpis)


@router.get("/summary")
async def get_all_summaries():
    """Trả về KPI của tất cả 4 phase cùng lúc — dùng để preload."""
    return {
        phase_id: builder()
        for phase_id, builder in PHASE_BUILDERS.items()
    }