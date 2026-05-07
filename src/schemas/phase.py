"""
src/schemas/phase.py
Pydantic models — định nghĩa contract cho tất cả API response.
"""

from pydantic import BaseModel
from typing import Any, Dict, List, Optional


class PhaseMetadata(BaseModel):
    id: int
    slug: str
    title: str
    subtitle: str
    crisp_dm_phase: str
    color: str          # CSS hex — dùng để tô màu tab + node trên sơ đồ
    description: str
    charts: List[str]   # Tên file ảnh trong /static/images/phaseN/


class KpiCard(BaseModel):
    label: str
    value: Any
    unit: Optional[str] = None
    note: Optional[str] = None


class PhaseSummaryResponse(BaseModel):
    phase_id: int
    kpis: Dict[str, Any]


class AllPhasesResponse(BaseModel):
    phases: List[PhaseMetadata]