"""
Scraper Agent Module
Simulates collecting market data, disclosures, and real-time feeds from financial portals.
"""

import time
from typing import Iterator, Dict, Any
from agents.base_agent import BaseAgent


class ScraperAgent(BaseAgent):
    name = "Financial Scraper Agent"
    description = "Thu thập tin tức, dữ liệu giao dịch & báo cáo tài chính từ Vnstock và nguồn công bố chính thức"
    version = "1.2.0"
    category = "Data Extraction"
    author = "DataOps Team"
    default_input = "VNM, HPG, FPT"

    def run(self, input_text: str) -> Iterator[Dict[str, Any]]:
        self._stop_requested = False
        tickers = [t.strip().upper() for t in input_text.split(",") if t.strip()]
        if not tickers:
            tickers = ["VNM"]

        yield self.emit("log", f"🚀 [bold cyan]Starting Scraper Agent[/bold cyan] for tickers: {', '.join(tickers)}")
        yield self.emit("step", "Connecting to financial gateway APIs...")
        time.sleep(0.4)

        if self.is_stopped():
            yield self.emit("warning", "Scraper cancelled by user request.")
            return

        for idx, ticker in enumerate(tickers, start=1):
            if self.is_stopped():
                yield self.emit("warning", f"Scraper halted before completing {ticker}.")
                return

            yield self.emit("step", f"[{idx}/{len(tickers)}] Querying Vnstock Data Feeds for [bold yellow]{ticker}[/bold yellow]...")
            time.sleep(0.5)

            yield self.emit("log", f"  • Fetching live order-book and intraday ticks for {ticker}...")
            time.sleep(0.3)

            yield self.emit("log", f"  • Downloading audited Q2/2026 Financial Statements (Balance Sheet, Cash Flow)...")
            time.sleep(0.4)

            yield self.emit("log", f"  • Scraping latest 15 regulatory filings & corporate announcements...")
            time.sleep(0.3)

            yield self.emit("log", f"  ✅ Extracted 1,420 records for {ticker}. Checksum verified.")
            time.sleep(0.2)

        yield self.emit("step", "Aggregating and normalizing market datasets...")
        time.sleep(0.4)

        summary_result = {
            "tickers_processed": tickers,
            "total_records": len(tickers) * 1420,
            "status": "SUCCESS",
            "storage_path": "data/scraped_cache.parquet",
            "execution_mode": "Mock Live Stream",
        }

        yield self.emit("result", f"🎉 Scraper finished successfully! Saved to {summary_result['storage_path']}", summary_result)

