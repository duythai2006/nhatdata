"""
Project Registry Module
Defines metadata and operational parameters for local services and micro-projects.
"""

from dataclasses import dataclass, field
from typing import List, Optional
import time


@dataclass
class LocalProject:
    id: str
    name: str
    category: str
    entry_point: str
    command: str
    status: str = "STOPPED"  # "STOPPED", "RUNNING", "FAILED"
    pid: Optional[int] = None
    started_at: Optional[float] = None
    logs: List[str] = field(default_factory=list)

    @property
    def uptime(self) -> str:
        if self.status != "RUNNING" or not self.started_at:
            return "--:--:--"
        elapsed = int(time.time() - self.started_at)
        hours, rem = divmod(elapsed, 3600)
        mins, secs = divmod(rem, 60)
        return f"{hours:02d}:{mins:02d}:{secs:02d}"


def get_default_projects() -> List[LocalProject]:
    return [
        LocalProject(
            id="proj_copilot_engine",
            name="Investment Copilot Engine",
            category="Data Pipeline",
            entry_point="src/vnstock_provider.py",
            command="python -c \"from src.vnstock_provider import fetch_vnstock_reports\"",
            status="RUNNING",
            pid=28941,
            started_at=time.time() - 3600 * 2.5,  # running for 2.5 hours
            logs=[
                "[14:20:01] Engine initialized with DuckDB persistence.",
                "[14:20:05] Vnstock data provider connected.",
                "[16:45:10] Heartbeat OK: Ingested 12,400 ticks across HOSE & HNX.",
            ],
        ),
        LocalProject(
            id="proj_streamlit_dashboard",
            name="Financial Research Dashboard",
            category="Web UI / Streamlit",
            entry_point="app/streamlit_app.py",
            command="streamlit run app/streamlit_app.py --server.port 8501",
            status="STOPPED",
            pid=None,
            started_at=None,
            logs=[
                "[INFO] Dashboard service idle. Click 'Start' to launch on port 8501.",
            ],
        ),
        LocalProject(
            id="proj_data_worker",
            name="Realtime Market Ticker Worker",
            category="Background Worker",
            entry_point="src/data_agent.py",
            command="python src/data_agent.py --watch",
            status="RUNNING",
            pid=34102,
            started_at=time.time() - 3600 * 5.2,  # running for 5.2 hours
            logs=[
                "[09:00:00] Market session morning open detected.",
                "[11:30:00] Morning close sync finished (Index: 1,280.45).",
                "[13:00:00] Afternoon session active. Streaming order book depths.",
            ],
        ),
        LocalProject(
            id="proj_macro_analyzer",
            name="Macro & Bond Yield Scanner",
            category="Quant Scheduler",
            entry_point="src/macro_scanner.py",
            command="python src/macro_scanner.py --cron",
            status="STOPPED",
            pid=None,
            started_at=None,
            logs=[
                "[INFO] Macro scanner stopped. Scheduled to run daily at 17:00.",
            ],
        ),
    ]

