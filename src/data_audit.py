from __future__ import annotations

from typing import Dict, List

import pandas as pd


def audit_financial_reports(reports: Dict[str, pd.DataFrame]) -> pd.DataFrame:
    issues: List[dict] = []

    for report_name, df in reports.items():
        if df is None or df.empty:
            issues.append({
                "report": report_name,
                "severity": "high",
                "issue": "No data returned",
                "detail": f"Bảng {report_name} rỗng hoặc không tải được.",
            })
            continue

        if "item" not in df.columns:
            issues.append({
                "report": report_name,
                "severity": "high",
                "issue": "Missing item column",
                "detail": "Không tìm thấy cột chỉ tiêu chính để chuẩn hóa dữ liệu.",
            })
            continue

        if df.duplicated(subset=["item"]).any():
            dupes = df.loc[df.duplicated(subset=["item"], keep=False), "item"].dropna().unique().tolist()
            issues.append({
                "report": report_name,
                "severity": "medium",
                "issue": "Duplicate item rows",
                "detail": f"Các dòng lặp: {dupes[:5]}",
            })

        numeric_cols = [col for col in df.columns if col != "item" and col != "error"]
        for col in numeric_cols:
            cleaned = pd.to_numeric(df[col], errors="coerce")
            if cleaned.isna().all():
                issues.append({
                    "report": report_name,
                    "severity": "low",
                    "issue": "Unusable year column",
                    "detail": f"Cột {col} không chứa dữ liệu số hợp lệ.",
                })

    return pd.DataFrame(issues)


def build_audit_summary(reports: Dict[str, pd.DataFrame]) -> dict:
    audit_df = audit_financial_reports(reports)
    return {
        "issue_count": int(len(audit_df)),
        "issues": audit_df,
        "status": "ok" if audit_df.empty else "warning",
    }
