import sys
from io import BytesIO
from pathlib import Path

ROOT_DIR = Path(__file__).resolve().parents[1]
if str(ROOT_DIR) not in sys.path:
    sys.path.insert(0, str(ROOT_DIR))

import streamlit as st
import pandas as pd

from src.data_audit import build_audit_summary
from src.financial_pipeline import build_company_snapshot
from src.vnstock_provider import report_to_html
from src.valuation import build_thesis_outline

st.set_page_config(
    page_title="Investment Research Copilot",
    layout="wide",
)

st.title("Investment Research Copilot")
st.caption("Ticker → financial data → audit → thesis → valuation")

ticker = st.text_input("Mã cổ phiếu", placeholder="Ví dụ: PVS")


def dataframe_to_excel(df):
    output = BytesIO()
    with pd.ExcelWriter(output, engine="xlsxwriter") as writer:
        df.to_excel(writer, index=False, sheet_name="Financial data")
    return output.getvalue()

if st.button("Bắt đầu Research"):
    if not ticker:
        st.warning("Nhập mã cổ phiếu trước.")
    else:
        ticker = ticker.strip().upper()
        with st.spinner(f"Đang thu thập và chuẩn hóa dữ liệu cho {ticker}..."):
            snapshot = build_company_snapshot(ticker)
            audit = build_audit_summary(snapshot["reports"])
            thesis = build_thesis_outline()

        st.success(f"Xong: {ticker}")

        col1, col2, col3 = st.columns(3)
        col1.metric("Reports", len(snapshot["reports"]))
        col2.metric("Metrics", len(snapshot["summary"]))
        col3.metric("Audit", audit["issue_count"])

        st.subheader("1) Financial Data")
        if snapshot["summary"].empty:
            st.info("Không có metric nào được trích xuất từ dữ liệu nguồn.")
        else:
            st.dataframe(snapshot["summary"], use_container_width=True)
            st.download_button(
                "Tải metrics CSV",
                snapshot["summary"].to_csv(index=False).encode("utf-8-sig"),
                file_name=f"{ticker}_metrics.csv",
                mime="text/csv",
            )

        st.subheader("2) Data Audit")
        if audit["issues"].empty:
            st.success("Không có issue nào phát hiện được trong dữ liệu đã parse.")
        else:
            st.dataframe(audit["issues"], use_container_width=True)
            st.download_button(
                "Tải audit CSV",
                audit["issues"].to_csv(index=False).encode("utf-8-sig"),
                file_name=f"{ticker}_audit.csv",
                mime="text/csv",
            )

        st.subheader("3) Thesis Framework")
        st.write(thesis["thesis"])

        st.markdown("### Bull case")
        for item in thesis["bull_case"]:
            st.write("- " + item)

        st.markdown("### Bear case")
        for item in thesis["bear_case"]:
            st.write("- " + item)

        st.markdown("### Assumptions")
        for item in thesis["assumptions"]:
            st.write("- " + item)

        st.subheader("4) Sources and raw reports")
        for report_name, df in snapshot["reports"].items():
            if df is not None and not df.empty:
                st.markdown(f"**{report_name}**")
                st.markdown(report_to_html(df), unsafe_allow_html=True)
                download_col1, download_col2 = st.columns(2)
                download_col1.download_button(
                    "Tải CSV",
                    df.to_csv(index=False).encode("utf-8-sig"),
                    file_name=f"{ticker}_{report_name}.csv",
                    mime="text/csv",
                    key=f"{report_name}_csv",
                )
                download_col2.download_button(
                    "Tải Excel",
                    dataframe_to_excel(df),
                    file_name=f"{ticker}_{report_name}.xlsx",
                    mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
                    key=f"{report_name}_xlsx",
                )
