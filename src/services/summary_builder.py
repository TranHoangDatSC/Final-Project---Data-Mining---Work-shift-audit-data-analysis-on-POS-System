"""
src/services/summary_builder.py
Tổng hợp KPI numbers cho từng phase để render trên frontend.
Tất cả logic business nằm ở đây, không trong API layer.
"""

from __future__ import annotations
from typing import Dict, Any, Optional
import pandas as pd

from src.services.data_loader import DataLoader


def _safe(df: Optional[pd.DataFrame], col: str, agg: str, fallback=0):
    """Helper: tránh crash khi CSV chưa load hoặc cột không tồn tại."""
    if df is None or col not in df.columns:
        return fallback
    series = df[col].dropna()
    if series.empty:
        return fallback
    return getattr(series, agg)()


def build_phase1_kpis() -> Dict[str, Any]:
    """Phase 1 — Descriptive: tổng quan dữ liệu."""
    df = DataLoader.main_log()
    audit = DataLoader.audit_merged()
    return {
        "total_shifts": int(len(df)) if df is not None else 0,
        "valid_shifts": int(len(audit)) if audit is not None else 0,
        "avg_revenue": round(float(_safe(audit, "total_revenue", "mean")), 0),
        "max_cash_diff": round(float(_safe(audit, "Cash_Diff", "max")), 0),
    }


def build_phase2_kpis() -> Dict[str, Any]:
    """Phase 2 — Diagnostic: K-Means clustering results."""
    df = DataLoader.clustered()
    kpis: Dict[str, Any] = {
        "num_clusters": 0,
        "cluster_sizes": {},
        "silhouette_note": "k=4 selected via Elbow + Silhouette",
    }
    if df is not None and "cluster" in df.columns:
        counts = df["cluster"].value_counts().sort_index()
        kpis["num_clusters"] = int(counts.shape[0])
        kpis["cluster_sizes"] = {
            f"C{int(k)}": int(v) for k, v in counts.items()
        }
    return kpis


def build_phase3_kpis() -> Dict[str, Any]:
    """Phase 3 — Customer Pattern: text mining + anomaly detection."""
    df = DataLoader.customer_pattern()
    return {
        "total_notes": int(len(df)) if df is not None else 0,
        "anomaly_note": "IQR-based outlier detection on order quantity",
        "top_categories": ["Chờ lâu", "Thiếu đồ", "Nhân viên"],
    }


def build_phase4_kpis() -> Dict[str, Any]:
    """Phase 4 — Prescriptive: Rule Engine output."""
    return {
        "rules_defined": 3,
        "rule_names": ["R1: Thu Ngân Thất Thoát", "R2: Lỗi Cân Đối", "R3: Dư Két Bất Thường"],
        "priority_order": "R1 → R2 → R3 (độc lập)",
    }


PHASE_BUILDERS = {
    "1": build_phase1_kpis,
    "2": build_phase2_kpis,
    "3": build_phase3_kpis,
    "4": build_phase4_kpis,
}