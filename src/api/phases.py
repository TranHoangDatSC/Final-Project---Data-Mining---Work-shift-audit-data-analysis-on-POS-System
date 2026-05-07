"""
src/api/phases.py
GET /api/phases       → danh sách tất cả 4 phase với metadata
GET /api/phase/{id}   → metadata của 1 phase cụ thể
"""

from fastapi import APIRouter, HTTPException
from src.schemas.phase import PhaseMetadata, AllPhasesResponse

router = APIRouter()

# ── Static metadata — không cần DB, không thay đổi ──────────────────────────
PHASES: list[PhaseMetadata] = [
    PhaseMetadata(
        id=1,
        slug="descriptive",
        title="Vòng 1: Descriptive",
        subtitle="Hiểu dữ liệu & Chuẩn bị",
        crisp_dm_phase="Business Understanding → Data Understanding → Data Preparation",
        color="#4361ee",
        description=(
            "Khám phá và làm sạch dữ liệu từ MainLog và DetailsTransaction. "
            "Tổng hợp thống kê mô tả, phân phối doanh thu, phát hiện outlier ban đầu "
            "và xây dựng pipeline merge dữ liệu audit."
        ),
        charts=[
            "boxplot.png",
            "correlation-heatmap.png",
            "histogram-kde.png",
            "histogram-timeseries.png",
            "scatter-plot.png",
        ],
    ),
    PhaseMetadata(
        id=2,
        slug="diagnostic",
        title="Vòng 2: Diagnostic",
        subtitle="Mô hình hóa & Phân cụm",
        crisp_dm_phase="Modeling → Evaluation",
        color="#f4845f",
        description=(
            "Áp dụng K-Means Clustering (k=4) trên 5 features đặc trưng của ca làm việc. "
            "Dùng RobustScaler để xử lý outlier, PCA 2D để visualize cluster, "
            "Elbow + Silhouette để chọn k tối ưu."
        ),
        charts=[
            "elbow-curve.png",
            "silhouette-analysis.png",
            "PCA2D-scatter-feature.png",
            "heatmap-centroids.png",
            "radar-chart.png",
            "cluster-distribution-overtime.png",
            "moring-afternoon-shift.png",
            "scatter-ratio.png",
            "boxplot-3.png",
        ],
    ),
    PhaseMetadata(
        id=3,
        slug="customer-pattern",
        title="Vòng 3: Customer Pattern",
        subtitle="Khai thác hành vi khách hàng",
        crisp_dm_phase="Data Preparation → Modeling (nhánh độc lập)",
        color="#7b5ea7",
        description=(
            "Text mining trên 101 ghi chú khách hàng từ DetailsTransaction. "
            "Phân loại phản hồi theo chủ đề, phát hiện bất thường trong số lượng order "
            "bằng IQR, timeline anomaly detection."
        ),
        charts=[
            "histogram-customer-behaviour.png",
            "boxplot-orders-distribution.png",
            "anomalies-timeline.png",
        ],
    ),
    PhaseMetadata(
        id=4,
        slug="prescriptive",
        title="Vòng 4: Prescriptive",
        subtitle="Rule Engine & Khuyến nghị",
        crisp_dm_phase="Evaluation → Deployment",
        color="#2ec4b6",
        description=(
            "Xây dựng Rule Engine 3 tầng dựa trên kết quả clustering. "
            "R1: Phát hiện thất thoát thu ngân, R2: Lỗi cân đối sổ sách, "
            "R3: Dư két bất thường. Mỗi rule gắn với khuyến nghị hành động cụ thể."
        ),
        charts=["general-rule-engine.png"],
    ),
]

PHASE_MAP = {p.id: p for p in PHASES}


@router.get("/phases", response_model=AllPhasesResponse)
async def get_all_phases():
    """Trả về metadata của tất cả 4 phase."""
    return AllPhasesResponse(phases=PHASES)


@router.get("/phase/{phase_id}", response_model=PhaseMetadata)
async def get_phase(phase_id: int):
    """Trả về metadata của phase theo ID (1–4)."""
    if phase_id not in PHASE_MAP:
        raise HTTPException(status_code=404, detail=f"Phase {phase_id} not found")
    return PHASE_MAP[phase_id]