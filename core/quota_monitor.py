"""
Quota & API Rate Limit Monitor Module
Provides structured tracking of accounts, model limits (Gemini, Claude, GPT),
real-time percentage calculations, and countdown timers for quota refreshes.
"""

from dataclasses import dataclass, field
from datetime import datetime, timedelta
from typing import List, Dict, Any


@dataclass
class ModelQuota:
    id: str
    name: str
    provider: str  # "Google Gemini", "Anthropic", "OpenAI"
    remaining_percent: float
    used_tpm: int
    max_tpm: int
    used_rpm: int
    max_rpm: int
    seconds_until_refresh: int
    tier: str = "Pay-as-you-go"

    @property
    def formatted_refresh_time(self) -> str:
        if self.seconds_until_refresh <= 0:
            return "Resetting..."
        td = timedelta(seconds=self.seconds_until_refresh)
        hours, remainder = divmod(int(td.total_seconds()), 3600)
        minutes, seconds = divmod(remainder, 60)
        return f"{hours:02d}h {minutes:02d}m {seconds:02d}s"

    @property
    def status_label(self) -> str:
        if self.remaining_percent > 50:
            return "HEALTHY"
        elif self.remaining_percent > 20:
            return "WARNING"
        return "CRITICAL"


@dataclass
class AccountQuota:
    account_id: str
    account_name: str
    organization: str
    tier: str
    models: List[ModelQuota] = field(default_factory=list)


class QuotaMonitor:
    def __init__(self):
        self.accounts = self._load_initial_mock_data()

    def _load_initial_mock_data(self) -> List[AccountQuota]:
        return [
            AccountQuota(
                account_id="acc_gemini_prod",
                account_name="Production Google Cloud AI Platform",
                organization="FinTech Enterprise Alpha",
                tier="Tier-3 Enterprise",
                models=[
                    ModelQuota(
                        id="gemini-1_5-pro",
                        name="Gemini 1.5 Pro (Workspace Pro)",
                        provider="Google Gemini",
                        remaining_percent=86.5,
                        used_tpm=270000,
                        max_tpm=2000000,
                        used_rpm=48,
                        max_rpm=360,
                        seconds_until_refresh=8245,  # ~2h 17m
                        tier="Enterprise",
                    ),
                    ModelQuota(
                        id="gemini-2_0-flash",
                        name="Gemini 2.0 Flash (Fast Agent)",
                        provider="Google Gemini",
                        remaining_percent=94.0,
                        used_tpm=240000,
                        max_tpm=4000000,
                        used_rpm=60,
                        max_rpm=1000,
                        seconds_until_refresh=2540,  # ~42m
                        tier="Enterprise",
                    ),
                    ModelQuota(
                        id="gemini-1_5-flash",
                        name="Gemini 1.5 Flash (Batch Pipeline)",
                        provider="Google Gemini",
                        remaining_percent=78.2,
                        used_tpm=872000,
                        max_tpm=4000000,
                        used_rpm=218,
                        max_rpm=1000,
                        seconds_until_refresh=11115,  # ~3h 5m
                        tier="Enterprise",
                    ),
                ],
            ),
            AccountQuota(
                account_id="acc_frontier_llm",
                account_name="Frontier Multi-Provider Gateway",
                organization="Investment Research Ops",
                tier="Production Scale",
                models=[
                    ModelQuota(
                        id="claude-3_5-sonnet",
                        name="Claude 3.5 Sonnet (v2)",
                        provider="Anthropic",
                        remaining_percent=68.4,
                        used_tpm=126400,
                        max_tpm=400000,
                        used_rpm=32,
                        max_rpm=100,
                        seconds_until_refresh=4725,  # ~1h 18m
                        tier="Tier-4 Scale",
                    ),
                    ModelQuota(
                        id="gpt-4o",
                        name="GPT-4o (Reasoning & Vision)",
                        provider="OpenAI",
                        remaining_percent=81.0,
                        used_tpm=95000,
                        max_tpm=500000,
                        used_rpm=95,
                        max_rpm=500,
                        seconds_until_refresh=9015,  # ~2h 30m
                        tier="Tier-4 Scale",
                    ),
                    ModelQuota(
                        id="claude-3_5-haiku",
                        name="Claude 3.5 Haiku (Fast Classifier)",
                        provider="Anthropic",
                        remaining_percent=92.5,
                        used_tpm=37500,
                        max_tpm=500000,
                        used_rpm=15,
                        max_rpm=200,
                        seconds_until_refresh=17400,  # ~4h 50m
                        tier="Tier-4 Scale",
                    ),
                ],
            ),
            AccountQuota(
                account_id="acc_secondary_dev",
                account_name="Developer Sandbox & Backups",
                organization="Dev Environment",
                tier="Pay-As-You-Go",
                models=[
                    ModelQuota(
                        id="gemini-1_5-flash-dev",
                        name="Gemini 1.5 Flash (Dev Sandbox)",
                        provider="Google Gemini",
                        remaining_percent=96.0,
                        used_tpm=40000,
                        max_tpm=1000000,
                        used_rpm=1,
                        max_rpm=15,
                        seconds_until_refresh=909,  # ~15m
                        tier="Free/PayGo",
                    ),
                    ModelQuota(
                        id="deepseek-v3",
                        name="DeepSeek-V3 (Open Inference)",
                        provider="DeepSeek",
                        remaining_percent=74.5,
                        used_tpm=255000,
                        max_tpm=1000000,
                        used_rpm=26,
                        max_rpm=100,
                        seconds_until_refresh=18620,  # ~5h 10m
                        tier="API Standard",
                    ),
                ],
            ),
        ]

    def tick_second(self):
        """Tick down all refresh countdowns by 1 second."""
        for acc in self.accounts:
            for model in acc.models:
                if model.seconds_until_refresh > 1:
                    model.seconds_until_refresh -= 1
                else:
                    # Reset cycle
                    model.seconds_until_refresh = 3600 * 4
                    model.remaining_percent = min(100.0, model.remaining_percent + 20.0)

    def refresh_data(self):
        """Re-sync or reset monitor metrics."""
        self.accounts = self._load_initial_mock_data()

    def get_summary_stats(self) -> Dict[str, Any]:
        total_models = sum(len(a.models) for a in self.accounts)
        avg_remaining = (
            sum(m.remaining_percent for a in self.accounts for m in a.models)
            / max(total_models, 1)
        )
        return {
            "total_accounts": len(self.accounts),
            "total_models": total_models,
            "avg_remaining": avg_remaining,
            "updated_at": datetime.now().strftime("%H:%M:%S"),
        }
