from __future__ import annotations

from typing import Dict, Iterable, List

import pandas as pd

from src.vnstock_provider import fetch_vnstock_reports


def _normalize_item_name(value: object) -> str:
    text = str(value or "").strip().lower()
    replacements = {
        "&nbsp;": " ",
        "\xa0": " ",
        "–": "-",
        "—": "-",
    }
    for old, new in replacements.items():
        text = text.replace(old, new)
    return " ".join(text.split())


def _extract_metric_rows(df: pd.DataFrame, aliases: Iterable[str]) -> pd.DataFrame:
    if df is None or df.empty:
        return pd.DataFrame()

    if "item" not in df.columns:
        return pd.DataFrame()

    work = df.copy()
    work["_item_norm"] = work["item"].apply(_normalize_item_name)
    rows = []
    for alias in aliases:
        alias_norm = _normalize_item_name(alias)
        found = work[work["_item_norm"].str.contains(alias_norm, na=False)]
        if not found.empty:
            rows.append(found.iloc[0])
    if not rows:
        return pd.DataFrame()
    return pd.DataFrame(rows).drop(columns=["_item_norm"], errors="ignore")


def collect_financial_reports(ticker: str) -> Dict[str, pd.DataFrame]:
    """Collect financial statements from Vnstock only."""
    return fetch_vnstock_reports(ticker)


def build_metric_summary(reports: Dict[str, pd.DataFrame]) -> pd.DataFrame:
    metric_aliases = {
        "revenue": ["doanh thu", "doanh thu thuần", "total revenue", "revenue"],
        "net_profit": ["lợi nhuận sau thuế", "lợi nhuận ròng", "net income"],
        "ebitda": ["ebitda", "lợi nhuận trước thuế", "earnings before interest taxes depreciation amortization"],
        "operating_cash_flow": ["dòng tiền từ hoạt động kinh doanh", "cash flow from operations", "tien tu hdkd"],
        "free_cash_flow": ["dòng tiền tự do", "free cash flow", "fcf"],
        "total_assets": ["tổng tài sản", "total assets", "tai san"],
        "total_liabilities": ["tổng nợ phải trả", "total liabilities", "nợ phải trả"],
        "equity": ["vốn chủ sở hữu", "equity", "total equity"],
        "capex": ["capex", "đầu tư tài sản cố định", "mua sắm tài sản cố định", "investments"],
    }

    rows: List[dict] = []

    for metric_name, aliases in metric_aliases.items():
        for report_name, df in reports.items():
            if df is None or df.empty or "item" not in df.columns:
                continue
            match = _extract_metric_rows(df, aliases)
            if match.empty:
                continue
            value_row = match.iloc[0]
            numeric_values = {}
            for key, value in value_row.items():
                if key == "item":
                    continue
                if key == "error":
                    continue
                numeric_values[str(key)] = value

            if not numeric_values:
                continue

            latest_year = max(numeric_values.keys(), key=lambda x: str(x))
            latest_value = numeric_values[latest_year]
            rows.append({
                "metric": metric_name,
                "report": report_name,
                "latest_year": str(latest_year),
                "latest_value": latest_value,
                "source_table": report_name,
            })
            break

    summary_df = pd.DataFrame(rows, columns=[
        "metric",
        "report",
        "latest_year",
        "latest_value",
        "source_table",
    ])

    if summary_df.empty or "metric" not in summary_df.columns:
        return summary_df

    try:
        return summary_df.sort_values(["metric"], kind="stable").reset_index(drop=True)
    except KeyError:
        return summary_df


def build_company_snapshot(ticker: str) -> dict:
    reports = collect_financial_reports(ticker)
    summary = build_metric_summary(reports)
    return {
        "ticker": ticker.upper(),
        "reports": reports,
        "summary": summary,
    }
