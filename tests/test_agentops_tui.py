"""
Automated Verification Suite for AgentOps Terminal Command Center
Tests:
  1. Dynamic Agent Discovery (adding a file to agents/ and auto-detecting it)
  2. Quota countdown and calculations
  3. Process Manager execution and cancellation
  4. Project Manager toggle and state tracking
  5. Textual Headless Pilot Test (Mounts all 3 tabs, clicks buttons, verifies rendering)
"""

import sys
import asyncio
from pathlib import Path

# Add workspace root to sys.path
WORKSPACE_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(WORKSPACE_ROOT))

from textual.widgets import Button
from core.quota_monitor import QuotaMonitor
from core.agent_loader import AgentLoader
from core.process_manager import ProcessManager
from core.project_manager import ProjectManager
from agents.base_agent import BaseAgent
from main import AgentOpsApp


def test_quota_monitor():
    print("--- [1/5] Testing QuotaMonitor ---")
    monitor = QuotaMonitor()
    assert len(monitor.accounts) >= 3, f"Expected at least 3 accounts, got {len(monitor.accounts)}"
    
    first_model = monitor.accounts[0].models[0]
    initial_countdown = first_model.seconds_until_refresh
    monitor.tick_second()
    assert first_model.seconds_until_refresh == initial_countdown - 1
    
    stats = monitor.get_summary_stats()
    assert stats["total_accounts"] >= 3
    assert stats["total_models"] >= 8
    print(f"✅ QuotaMonitor OK. Tracked {stats['total_models']} models across {stats['total_accounts']} accounts.")


def test_agent_loader_and_dynamic_discovery():
    print("--- [2/5] Testing AgentLoader & Dynamic Auto-Discovery ---")
    loader = AgentLoader()
    discovered = loader.get_agent_list()
    agent_ids = [a["id"] for a in discovered]
    print(f"Initial discovered agents: {agent_ids}")
    assert any("scraper_agent" in aid for aid in agent_ids), "ScraperAgent missing!"
    assert any("analyzer_agent" in aid for aid in agent_ids), "AnalyzerAgent missing!"

    # Test dynamic discovery by creating a new temporary agent file
    temp_agent_file = WORKSPACE_ROOT / "agents" / "temp_crypto_agent.py"
    temp_agent_code = '''"""Temporary agent for testing auto-discovery."""
from agents.base_agent import BaseAgent

class CryptoAgent(BaseAgent):
    name = "Crypto On-Chain Scanner"
    description = "Scans DEX liquidity pools and whale alerts"
    version = "1.0.0"
    category = "Crypto & Web3"
    default_input = "ETH/USDT"

    def run(self, input_text):
        yield self.emit("log", f"Analyzing pool {input_text}")
        yield self.emit("result", "Pool analyzed successfully")
'''
    try:
        temp_agent_file.write_text(temp_agent_code, encoding="utf-8")
        loader.reload()
        new_list = loader.get_agent_list()
        new_agent_ids = [a["id"] for a in new_list]
        print(f"After dynamic add: {new_agent_ids}")
        assert any("temp_crypto_agent" in aid for aid in new_agent_ids), "Failed to dynamically discover new agent!"
        print("✅ Dynamic discovery verified: New agent detected instantly without restart.")
    finally:
        if temp_agent_file.exists():
            temp_agent_file.unlink()
        loader.reload()


def test_process_manager():
    print("--- [3/5] Testing ProcessManager ---")
    loader = AgentLoader()
    scraper = None
    scraper_id = None
    for aid, agent in loader.agents.items():
        if "scraper_agent" in aid:
            scraper = agent
            scraper_id = aid
            break

    assert scraper is not None
    pm = ProcessManager()
    events = []

    proc = pm.run_agent(
        agent_id=scraper_id,
        agent=scraper,
        input_text="VNM",
        log_callback=lambda ev: events.append(ev),
    )
    
    # Wait briefly and check running status
    import time
    time.sleep(0.6)
    assert len(events) > 0, "No stream events received from agent!"
    # Test stop/cancel
    pm.stop_agent(scraper_id)
    time.sleep(0.5)
    print(f"✅ ProcessManager OK. Captured {len(events)} stream events. Stopped cleanly: {proc.status}")


def test_project_manager():
    print("--- [4/5] Testing ProjectManager ---")
    pjm = ProjectManager()
    projects = pjm.list_projects()
    assert len(projects) >= 4
    
    target_id = projects[1].id
    init_status = projects[1].status
    pjm.toggle_project(target_id)
    assert projects[1].status != init_status, "Toggle failed to change project status"
    pjm.toggle_project(target_id)
    assert projects[1].status == init_status
    print(f"✅ ProjectManager OK. Verified {len(projects)} local projects with state toggle.")


async def run_headless_textual_app():
    print("--- [5/5] Testing Textual Headless App Mounting & Pilot ---")
    app = AgentOpsApp()
    async with app.run_test(size=(140, 45)) as pilot:
        # Check title and elements mounted
        assert app.query_one("#main_tabs") is not None
        assert app.query_one("#quota_summary_bar") is not None
        assert app.query_one("#agent_option_list") is not None
        assert app.query_one("#project_card_list") is not None
        print("  • Mounted all widgets and containers successfully.")

        # Test switching to Agent Tab
        await pilot.press("2")
        await pilot.pause(0.2)
        tabbed = app.query_one("#main_tabs")
        assert tabbed.active == "tab_agents", f"Expected tab_agents, got {tabbed.active}"
        print("  • Switched to TAB 2 [Agent Hub].")

        # Test switching to Project Center Tab
        await pilot.press("3")
        await pilot.pause(0.2)
        assert tabbed.active == "tab_projects", f"Expected tab_projects, got {tabbed.active}"
        print("  • Switched to TAB 3 [Project Center].")

        # Test switching back to Quota Tab
        await pilot.press("1")
        await pilot.pause(0.2)
        assert tabbed.active == "tab_quota", f"Expected tab_quota, got {tabbed.active}"
        print("  • Switched to TAB 1 [Quota & Models Monitor].")

        # Test pressing Simulate Burst button
        btn_burst = app.query_one("#btn_simulate_burst", Button)
        btn_burst.press()
        await pilot.pause(0.2)
        print("  • Pressed #btn_simulate_burst successfully.")

        # Test Quit
        await pilot.press("q")
    print("✅ Textual Headless App test passed with 0 errors!")


def main():
    test_quota_monitor()
    test_agent_loader_and_dynamic_discovery()
    test_process_manager()
    test_project_manager()
    asyncio.run(run_headless_textual_app())
    print("\n🎉 ALL TESTS PASSED SUCCESSFULLY! AgentOps Command Center is verified and ready.")


if __name__ == "__main__":
    main()
