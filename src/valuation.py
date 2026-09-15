from __future__ import annotations

from typing import Dict

import pandas as pd


def build_valuation_snapshot(reports: Dict[str, pd.DataFrame]) -> pd.DataFrame:
    rows = []

    for report_name, df in reports.items():
        if df is None or df.empty or "item" not in df.columns:
            continue

        normalized = df.copy()
        normalized["item"] = normalized["item"].astype(str).str.lower()
        value_cols = [col for col in normalized.columns if col != "item" and col != "error"]

        for item_name, aliases in {
            "revenue": ["doanh thu", "revenue"],
            "net_profit": ["lợi nhuận sau thuế", "net income"],
            "total_assets": ["tổng tài sản", "total assets"],
            "equity": ["vốn chủ sở hữu", "equity"],
            "liabilities": ["nợ phải trả", "liabilities"],
            "operating_cash_flow": ["dòng tiền từ hoạt động kinh doanh", "cash flow from operations"],
        }.items():
            hit = normalized[normalized["item"].str.contains("|".join(aliases), na=False)]
            if hit.empty:
                continue
            last_values = {}
            for col in value_cols:
                try:
                    last_values[col] = pd.to_numeric(hit.iloc[0][col], errors="coerce")
                except Exception:
                    continue
            last_year = max((v for v in last_values.values() if pd.notna(v)), default=float("nan"))
            rows.append({
                "report": report_name,
                "metric": item_name,
                "latest_value": last_year if pd.notna(last_year) else None,
                "years_covered": len(last_values),
            })

    return pd.DataFrame(rows)


def build_thesis_outline() -> dict:
    return {
        "thesis": "Khung thesis đầu tư cần kiểm chứng: ngành có catalyst, doanh thu và lợi nhuận đang cải thiện, dòng tiền mạnh, valuation còn hợp lý so với peer.",
        "bull_case": [
            "Doanh thu tăng nhờ velocity của sản phẩm hoặc thị trường.",
            "Lợi nhuận mở rộng nhờ hiệu quả hoạt động và tận dụng quy mô.",
            "Dòng tiền tự do cải thiện và nâng tỷ suất sinh lời.",
        ],
        "bear_case": [
            "Doanh thu có thể không theo kịp kỳ vọng do suy yếu ngành hoặc mất đơn hàng.",
            "Lợi nhuận bị nén nếu chi phí biến động mạnh.",
            "Valuation có thể bị đánh giá quá cao khi peer suy yếu.",
        ],
        "assumptions": [
            "Giả định cần user xác nhận: tốc độ tăng trưởng, chi phí vốn, mức discount rate, mô hình tăng trưởng dài hạn.",
        ],
    }
