from __future__ import annotations

from html import escape
from typing import Any, Dict

import pandas as pd


def _normalize_label(value: object) -> str:
    return " ".join(str(value or "").strip().lower().split())


_REPORT_GROUPS = {
    "tiền và tương đương tiền",
    "các khoản phải thu",
    "hàng tồn kho, ròng",
    "tài sản lưu động khác",
    "tài sản cố định",
    "bất động sản đầu tư",
    "tài sản dở dang dài hạn",
    "các khoản phải trả",
    "nợ ngắn hạn",
    "nợ dài hạn",
    "vốn chủ sở hữu",
    "chi phí tài chính",
    "thu nhập khác",
    "lưu chuyển tiền từ hoạt động kinh doanh",
    "lưu chuyển tiền từ hoạt động đầu tư",
    "lưu chuyển tiền từ hoạt động tài chính",
}

_REPORT_DETAILS = {
    "tiền",
    "các khoản tương đương tiền",
    "phải thu khách hàng",
    "trả trước người bán",
    "phải thu nội bộ",
    "phải thu khác",
    "dự phòng nợ khó đòi",
    "hàng tồn kho",
    "dự phòng giảm giá hàng tồn kho",
    "chi phí trả trước ngắn hạn",
    "thuế gtgt được khấu trừ",
    "phải thu thuế khác",
    "chi phí lãi vay",
    "dự phòng giảm giá",
}


def _format_item_label(value: object) -> str:
    label = str(value or "").strip()
    normalized = _normalize_label(label)
    if not label:
        return label
    if label.upper() == label and any(character.isalpha() for character in label):
        level = 0
    elif normalized in _REPORT_DETAILS:
        level = 2
    elif normalized in _REPORT_GROUPS:
        level = 1
    else:
        level = 1
    if level == 0:
        return label
    if level == 1:
        return f"|-- {label}"
    return f"    `-- {label}"


def _item_level(value: object) -> int:
    label = str(value or "").strip()
    normalized = _normalize_label(label)
    if label.upper() == label and any(character.isalpha() for character in label):
        return 0
    if normalized in _REPORT_DETAILS:
        return 2
    return 1


def _format_accounting_value(value: object) -> str:
    if pd.isna(value):
        return ""
    numeric_value = float(value)
    if numeric_value == 0:
        return "-"
    if numeric_value < 0:
        return f"({abs(numeric_value):,.0f})"
    return f"{numeric_value:,.0f}"


def _coerce_dataframe(value: Any) -> pd.DataFrame:
    if value is None:
        return pd.DataFrame()
    if isinstance(value, pd.DataFrame):
        return value
    if isinstance(value, dict):
        try:
            return pd.DataFrame(value)
        except Exception:
            return pd.DataFrame([value])
    if isinstance(value, list):
        return pd.DataFrame(value)
    try:
        return pd.DataFrame(value)
    except Exception:
        return pd.DataFrame()


def format_report_for_display(df: pd.DataFrame) -> pd.DataFrame:
    """Format financial statement values for readable Streamlit tables."""
    if df is None or df.empty:
        return pd.DataFrame() if df is None else df.copy()

    display_df = df.copy()
    for column in display_df.columns:
        if column == "item" or not pd.api.types.is_numeric_dtype(display_df[column]):
            continue
        display_df[column] = display_df[column].map(_format_accounting_value)
    if "item" in display_df.columns:
        display_df["item"] = display_df["item"].map(_format_item_label)
    return display_df


def report_to_html(df: pd.DataFrame) -> str:
    """Render a financial report with real indentation for nested items."""
    display_df = format_report_for_display(df)
    if display_df.empty:
        return "<p>Không có dữ liệu.</p>"

    headers = "".join(f"<th>{escape(str(column))}</th>" for column in display_df.columns)
    rows = []
    for _, row in display_df.iterrows():
        cells = []
        for column in display_df.columns:
            value = "" if pd.isna(row[column]) else str(row[column])
            if column == "item":
                level = _item_level(value.replace("|-- ", "").replace("    `-- ", ""))
                style = f"padding-left: {12 + level * 32}px; font-weight: {'600' if level == 0 else '400'};"
                cells.append(f'<td style="{style}">{escape(value.lstrip())}</td>')
            else:
                cells.append(f"<td>{escape(value)}</td>")
        rows.append("<tr>" + "".join(cells) + "</tr>")

    return (
        '<div style="overflow-x:auto"><table class="financial-report">'
        f"<thead><tr>{headers}</tr></thead><tbody>{''.join(rows)}</tbody>"
        "</table></div>"
    )


def fetch_vnstock_reports(ticker: str) -> Dict[str, pd.DataFrame]:
    """Fetch annual financial statements through the current Vnstock API."""
    try:
        from vnstock.api.financial import Finance
    except Exception:
        return {}

    try:
        finance = Finance(
            source="VCI",
            symbol=ticker.upper(),
            period="year",
            get_all=False,
            show_log=False,
        )
        reports = {
            "income_statement": finance.income_statement(),
            "balance_sheet": finance.balance_sheet(),
            "cash_flow": finance.cash_flow(),
        }
    except Exception:
        return {}

    output: Dict[str, pd.DataFrame] = {}
    for name, value in reports.items():
        df = _coerce_dataframe(value)
        if df.empty:
            continue
        if "item" not in df.columns:
            first_column = df.columns[0]
            df = df.rename(columns={first_column: "item"})
        df = df.drop(columns=["item_en", "item_id"], errors="ignore")
        output[name] = df

    return output
