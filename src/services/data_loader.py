"""
src/services/data_loader.py
Đọc tất cả CSV vào memory một lần lúc startup.
Dùng class variable để share across requests mà không cần re-read disk.
"""

import os
from pathlib import Path
import pandas as pd
from typing import Optional

DATA_DIR = Path(__file__).parent.parent.parent / "data"


class DataLoader:
    _main_log: Optional[pd.DataFrame] = None
    _details: Optional[pd.DataFrame] = None
    _audit_merged: Optional[pd.DataFrame] = None
    _clustered: Optional[pd.DataFrame] = None
    _customer_pattern: Optional[pd.DataFrame] = None

    @classmethod
    def load_all(cls) -> None:
        """Gọi một lần trong lifespan startup."""
        try:
            cls._main_log        = pd.read_csv(DATA_DIR / "MainLog.csv")
            cls._details         = pd.read_csv(DATA_DIR / "DetailsTransaction.csv")
            cls._audit_merged    = pd.read_csv(DATA_DIR / "Audit_Merged_Data.csv")
            cls._clustered       = pd.read_csv(DATA_DIR / "Clustered_Shifts.csv")
            cls._customer_pattern = pd.read_csv(DATA_DIR / "Customer_Pattern.csv")
        except FileNotFoundError as e:
            # Graceful degradation: web vẫn hoạt động dù thiếu data
            print(f"[DataLoader] Warning: {e}")

    @classmethod
    def clear(cls) -> None:
        cls._main_log = cls._details = cls._audit_merged = None
        cls._clustered = cls._customer_pattern = None

    # ── Accessors ────────────────────────────────────────────────────────────
    @classmethod
    def main_log(cls) -> Optional[pd.DataFrame]:
        return cls._main_log

    @classmethod
    def audit_merged(cls) -> Optional[pd.DataFrame]:
        return cls._audit_merged

    @classmethod
    def clustered(cls) -> Optional[pd.DataFrame]:
        return cls._clustered

    @classmethod
    def customer_pattern(cls) -> Optional[pd.DataFrame]:
        return cls._customer_pattern