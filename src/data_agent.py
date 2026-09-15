from pathlib import Path
import requests
from bs4 import BeautifulSoup
from urllib.parse import urljoin


class DataAgent:

    def __init__(self, ticker: str):
        self.ticker = ticker.upper()
        self.base_dir = Path("data/raw") / self.ticker
        self.base_dir.mkdir(parents=True, exist_ok=True)

    def search_company_documents(self):
        """
        Tạm thời tìm tài liệu công khai bằng công cụ tìm kiếm.
        Giai đoạn sau sẽ bổ sung nguồn chuyên biệt.
        """

        queries = [
            f"{self.ticker} báo cáo tài chính pdf",
            f"{self.ticker} báo cáo thường niên pdf",
            f"{self.ticker} annual report pdf",
        ]

        print("\n=== DOCUMENT SEARCH ===")

        for query in queries:
            print(f"Searching: {query}")

        print("\nSearch module initialized.")
        print("Next step: connect real search sources.")

    def create_research_folder(self):
        folders = [
            self.base_dir / "financial_statements",
            self.base_dir / "annual_reports",
            self.base_dir / "presentations",
            self.base_dir / "other",
        ]

        for folder in folders:
            folder.mkdir(parents=True, exist_ok=True)

        print(f"\nResearch folder created: {self.base_dir}")


if __name__ == "__main__":
    ticker = input("Ticker: ").strip()

    if not ticker:
        raise ValueError("Ticker is required.")

    agent = DataAgent(ticker)

    agent.create_research_folder()
    agent.search_company_documents()