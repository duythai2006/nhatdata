import requests
from bs4 import BeautifulSoup
from pathlib import Path
from urllib.parse import urljoin
import re
import time


class DocumentCollector:

    def __init__(self, ticker):
        self.ticker = ticker.upper()

        self.root = Path("data/raw") / self.ticker
        self.financial = self.root / "financial_statements"
        self.annual = self.root / "annual_reports"
        self.presentation = self.root / "presentations"
        self.other = self.root / "other"

        for folder in [
            self.financial,
            self.annual,
            self.presentation,
            self.other,
        ]:
            folder.mkdir(parents=True, exist_ok=True)

        self.headers = {
            "User-Agent": (
                "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
                "AppleWebKit/537.36 Chrome/131 Safari/537.36"
            )
        }

    def search_bing(self, query):

        url = "https://www.google.com/search"

        params = {
            "q": query,
            "num": 10
        }

        try:
            r = requests.get(
                url,
                params=params,
                headers=self.headers,
                timeout=15
            )

            soup = BeautifulSoup(r.text, "html.parser")

            results = []

            for a in soup.select("a"):
                href = a.get("href", "")

                if href.startswith("http") and "google.com" not in href:
                    results.append(href)

            return list(dict.fromkeys(results))

        except Exception as e:
            print("Search error:", e)
            return []

    def search_documents(self):

        queries = [
            f"{self.ticker} báo cáo tài chính 2025 pdf",
            f"{self.ticker} báo cáo thường niên 2025 pdf",
            f"{self.ticker} báo cáo tài chính 2024 pdf",
            f"{self.ticker} annual report pdf",
            f"{self.ticker} investor presentation pdf",
        ]

        all_results = []

        for query in queries:

            print(f"\nSearching: {query}")

            results = self.search_bing(query)

            for url in results:

                if url not in all_results:
                    all_results.append(url)

        return all_results

    def classify(self, url):

        url_lower = url.lower()

        if ".pdf" not in url_lower:
            return self.other

        if any(
            word in url_lower
            for word in [
                "annual",
                "thuong-nien",
                "thuongnien",
                "annualreport"
            ]
        ):
            return self.annual

        if any(
            word in url_lower
            for word in [
                "financial",
                "taichinh",
                "bctc",
                "bao-cao-tai-chinh"
            ]
        ):
            return self.financial

        if any(
            word in url_lower
            for word in [
                "presentation",
                "investor",
                "ir"
            ]
        ):
            return self.presentation

        return self.other

    def download_pdf(self, url, folder):

        try:

            filename = url.split("/")[-1]

            filename = re.sub(
                r"[^a-zA-Z0-9._-]",
                "_",
                filename
            )

            if not filename.lower().endswith(".pdf"):
                filename += ".pdf"

            path = folder / filename

            if path.exists():
                return path

            print("Downloading:", url)

            r = requests.get(
                url,
                headers=self.headers,
                timeout=30
            )

            content_type = r.headers.get(
                "content-type",
                ""
            ).lower()

            if (
                "pdf" not in content_type
                and not url.lower().endswith(".pdf")
            ):
                return None

            if len(r.content) < 10000:
                return None

            path.write_bytes(r.content)

            print("Saved:", path)

            return path

        except Exception as e:

            print("Download failed:", e)

            return None

    def run(self):

        print("=" * 60)
        print(f"DATA COLLECTION — {self.ticker}")
        print("=" * 60)

        urls = self.search_documents()

        print(f"\nFound {len(urls)} candidate URLs.")

        downloaded = []

        for url in urls:

            folder = self.classify(url)

            path = self.download_pdf(
                url,
                folder
            )

            if path:
                downloaded.append({
                    "url": url,
                    "path": str(path)
                })

            time.sleep(1)

        print("\n" + "=" * 60)
        print("COLLECTION COMPLETE")
        print("=" * 60)

        print(f"Downloaded: {len(downloaded)} files")

        for item in downloaded:
            print(item["path"])

        return downloaded


if __name__ == "__main__":

    ticker = input("Ticker: ").strip()

    if not ticker:
        raise ValueError("Ticker is required")

    agent = DocumentCollector(ticker)

    agent.run()
