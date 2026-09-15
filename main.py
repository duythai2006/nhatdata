"""
AgentOps Terminal Command Center
Main entry point for the Textual TUI Application.
Provides:
  - TAB 1: Quota & Models Monitor (Green Progress Bars, RPM/TPM, Live Reset Countdown)
  - TAB 2: Agent Hub (Modular Discovery, Live Streaming Output, Stop/Run)
  - TAB 3: Project Center (Local Services, Toggle Start/Stop, Live Uptime)
"""

import sys
from pathlib import Path
from datetime import datetime
from typing import Dict, Any

from textual.app import App, ComposeResult
from textual.containers import Container, Horizontal, Vertical, VerticalScroll
from textual.widgets import (
    Header,
    Footer,
    TabbedContent,
    TabPane,
    Static,
    Button,
    ProgressBar,
    RichLog,
    Input,
    OptionList,
    Label,
    Rule,
)
from textual.widgets.option_list import Option
from textual.binding import Binding

# Ensure project root in sys.path
ROOT_DIR = Path(__file__).resolve().parent
if str(ROOT_DIR) not in sys.path:
    sys.path.insert(0, str(ROOT_DIR))

from core.quota_monitor import QuotaMonitor
from core.agent_loader import AgentLoader
from core.process_manager import ProcessManager
from core.project_manager import ProjectManager


APP_CSS = """
Screen {
    background: #0d1117;
    color: #c9d1d9;
}

Header {
    background: #161b22;
    color: #58a6ff;
    dock: top;
    height: 1;
}

Footer {
    background: #161b22;
    color: #8b949e;
    dock: bottom;
    height: 1;
}

TabbedContent {
    height: 1fr;
}

TabPane {
    padding: 1 1;
}

/* Custom Green ProgressBar Styling */
ProgressBar {
    width: 1fr;
    height: 1;
    margin: 0 0;
}

ProgressBar > Bar {
    width: 1fr;
}

ProgressBar > Bar > .bar--bar {
    color: #00e676;
    background: #21262d;
}

ProgressBar > Bar > .bar--complete {
    color: #00e676;
    background: #21262d;
}

/* Panel Containers */
.card {
    background: #161b22;
    border: round #30363d;
    padding: 1 1;
    margin-bottom: 1;
}

.card-header {
    background: #21262d;
    color: #58a6ff;
    text-style: bold;
    padding: 0 1;
    margin-bottom: 1;
}

.model-row {
    background: #0d1117;
    border: solid #21262d;
    padding: 1 1;
    margin-bottom: 1;
}

.stat-badge {
    color: #00e676;
    text-style: bold;
}

.timer-badge {
    color: #ffd600;
    text-style: bold;
}

.section-title {
    color: #58a6ff;
    text-style: bold;
    margin-bottom: 1;
}

/* Agent Hub Layout */
#agent_hub_container {
    height: 1fr;
}

#agent_list_column {
    width: 35%;
    border-right: solid #30363d;
    padding-right: 1;
}

#agent_exec_column {
    width: 65%;
    padding-left: 1;
}

#agent_option_list {
    height: 1fr;
    background: #161b22;
    border: round #30363d;
}

#agent_log_view {
    height: 1fr;
    background: #090d13;
    border: round #30363d;
    color: #e6edf3;
    padding: 0 1;
}

/* Project Center Layout */
.project-card {
    background: #161b22;
    border: round #30363d;
    padding: 1 1;
    margin-bottom: 1;
}

.project-running {
    border-left: wide #00e676;
}

.project-stopped {
    border-left: wide #ff5252;
}

#project_log_view {
    height: 12;
    background: #090d13;
    border: round #30363d;
    margin-top: 1;
}

Button {
    min-width: 12;
    margin-right: 1;
}
"""


class AgentOpsApp(App):
    TITLE = "AGENTOPS COMMAND CENTER"
    SUB_TITLE = "Multi-Agent & Quota Mission Control"
    CSS = APP_CSS

    BINDINGS = [
        Binding("1", "show_tab('tab_quota')", "Quota Monitor", show=True),
        Binding("2", "show_tab('tab_agents')", "Agent Hub", show=True),
        Binding("3", "show_tab('tab_projects')", "Project Center", show=True),
        Binding("r", "refresh_data", "Refresh", show=True),
        Binding("q", "quit", "Quit", show=True),
    ]

    def __init__(self):
        super().__init__()
        self.quota_monitor = QuotaMonitor()
        self.agent_loader = AgentLoader()
        self.process_manager = ProcessManager()
        self.project_manager = ProjectManager()

        self.selected_agent_id = None
        self.selected_project_id = None
        self.progress_widgets: Dict[str, ProgressBar] = {}
        self.timer_widgets: Dict[str, Static] = {}

    def compose(self) -> ComposeResult:
        yield Header(show_clock=True)
        with TabbedContent(initial="tab_quota", id="main_tabs"):
            with TabPane("📊 Quota & Models Monitor", id="tab_quota"):
                yield from self.compose_quota_tab()

            with TabPane("🤖 Agent Hub", id="tab_agents"):
                yield from self.compose_agent_tab()

            with TabPane("🚀 Project Center", id="tab_projects"):
                yield from self.compose_project_tab()

        yield Footer()

    # =========================================================================
    # TAB 1: Quota & Models Monitor
    # =========================================================================
    def compose_quota_tab(self) -> ComposeResult:
        stats = self.quota_monitor.get_summary_stats()
        with VerticalScroll():
            with Horizontal(classes="card"):
                yield Static(
                    f"🟢 [bold green]SYSTEM HEALTH: OPTIMAL[/bold green]  │  "
                    f"Accounts: [bold cyan]{stats['total_accounts']}[/bold cyan]  │  "
                    f"Models Monitored: [bold cyan]{stats['total_models']}[/bold cyan]  │  "
                    f"Avg Available: [bold #00e676]{stats['avg_remaining']:.1f}%[/bold #00e676]  │  "
                    f"Auto-Refresher: [bold yellow]Active (1s tick)[/bold yellow]",
                    id="quota_summary_bar",
                )
                yield Button("🔄 Sync All Quotas", id="btn_sync_quotas", variant="primary")
                yield Button("⚡ Simulate Load", id="btn_simulate_burst", variant="default")

            # Iterate over Accounts
            for acc in self.quota_monitor.accounts:
                with Vertical(classes="card"):
                    yield Static(
                        f"🏢 [bold white]{acc.account_name}[/bold white]  "
                        f"[dim]({acc.organization})[/dim]  •  "
                        f"[cyan][{acc.tier}][/cyan]",
                        classes="card-header",
                    )

                    for model in acc.models:
                        clean_id = model.id.replace(".", "_").replace("-", "_")
                        with Vertical(classes="model-row"):
                            with Horizontal():
                                yield Static(
                                    f"✨ [bold]{model.name}[/bold]  [dim]({model.provider})[/dim]",
                                    classes="stat-badge",
                                )
                                timer_id = f"timer_{clean_id}"
                                timer_widget = Static(
                                    f"⏳ [bold yellow]Refreshes in {model.formatted_refresh_time}[/bold yellow]  │  "
                                    f"Status: [bold green]{model.remaining_percent:.1f}% Available[/bold green]",
                                    id=timer_id,
                                )
                                self.timer_widgets[model.id] = timer_widget
                                yield timer_widget

                            pbar = ProgressBar(total=100.0, show_eta=False, id=f"pbar_{clean_id}")
                            pbar.progress = model.remaining_percent
                            self.progress_widgets[model.id] = pbar
                            yield pbar

                            with Horizontal():
                                yield Static(
                                    f"  • TPM Used: [bold cyan]{model.used_tpm:,}[/bold cyan] / {model.max_tpm:,}  │  "
                                    f"RPM Used: [bold cyan]{model.used_rpm}[/bold cyan] / {model.max_rpm}  │  "
                                    f"Tier: [dim]{model.tier}[/dim]"
                                )

    # =========================================================================
    # TAB 2: Agent Hub
    # =========================================================================
    def compose_agent_tab(self) -> ComposeResult:
        with Horizontal(id="agent_hub_container"):
            # Left: Agent List
            with Vertical(id="agent_list_column"):
                with Horizontal():
                    yield Static("📦 [bold cyan]Registered Agents[/bold cyan]", classes="section-title")
                    yield Button("🔄 Rescan", id="btn_rescan_agents", variant="default")
                yield Static("[dim]Agents are auto-discovered from `agents/`[/dim]", classes="stat-badge")
                yield OptionList(id="agent_option_list")

            # Right: Agent Run & Log Monitor
            with Vertical(id="agent_exec_column"):
                with Vertical(classes="card"):
                    yield Static("🎯 [bold]Agent Details & Configuration[/bold]", id="agent_detail_title")
                    yield Static("Select an agent from the left panel to begin.", id="agent_detail_desc")
                    yield Rule()
                    yield Label("Prompt / Execution Parameters:")
                    yield Input(placeholder="Enter prompt or parameters for this agent...", id="agent_input_field")
                    with Horizontal():
                        yield Button("▶ Run Agent", id="btn_run_agent", variant="success")
                        yield Button("⏹ Stop Agent", id="btn_stop_agent", variant="error", disabled=True)
                        yield Button("🗑 Clear Console", id="btn_clear_agent_log", variant="default")
                        yield Static("Status: [bold yellow]IDLE[/bold yellow]", id="agent_status_badge")

                yield Static("📡 [bold cyan]Live Output & Real-time Execution Stream[/bold cyan]:")
                yield RichLog(id="agent_log_view", markup=True, highlight=True, wrap=True)

    # =========================================================================
    # TAB 3: Project Center
    # =========================================================================
    def compose_project_tab(self) -> ComposeResult:
        with VerticalScroll():
            with Horizontal(classes="card"):
                yield Static(
                    "💻 [bold green]LOCAL SERVICES & WORKERS[/bold green]  │  "
                    "Manage backend jobs, crawlers and dashboards",
                    classes="section-title",
                )
                yield Button("▶ Start All", id="btn_start_all_projects", variant="success")
                yield Button("⏹ Stop All", id="btn_stop_all_projects", variant="error")
                yield Button("🔄 Refresh List", id="btn_refresh_projects", variant="default")

            yield Vertical(id="project_card_list")

            yield Static("📜 [bold cyan]Selected Project Console Log[/bold cyan]:")
            yield RichLog(id="project_log_view", markup=True, highlight=True, wrap=True)

    # =========================================================================
    # App Lifecycle & Events
    # =========================================================================
    def on_mount(self) -> None:
        # Populate agent options
        self.populate_agents_list()

        # Populate projects list
        self.populate_projects_list()

        # Setup 1-second interval timer for countdowns and live metrics
        self.set_interval(1.0, self.update_quota_timers)

        # Initial log entry
        log_view = self.query_one("#agent_log_view", RichLog)
        log_view.write("[dim cyan]AgentOps Command Center initialized. Ready to execute modular tasks.[/dim cyan]")

    def action_show_tab(self, tab_id: str) -> None:
        self.query_one("#main_tabs", TabbedContent).active = tab_id

    def action_refresh_data(self) -> None:
        self.quota_monitor.refresh_data()
        self.populate_agents_list()
        self.populate_projects_list()
        self.notify("All system modules and quotas refreshed!", title="Refreshed")

    def update_quota_timers(self) -> None:
        """Runs every 1 second to tick countdown timers and update UI."""
        self.quota_monitor.tick_second()
        for acc in self.quota_monitor.accounts:
            for model in acc.models:
                # Update countdown widget
                if model.id in self.timer_widgets:
                    widget = self.timer_widgets[model.id]
                    color_status = "green" if model.remaining_percent > 50 else ("yellow" if model.remaining_percent > 20 else "red")
                    widget.update(
                        f"⏳ [bold yellow]Refreshes in {model.formatted_refresh_time}[/bold yellow]  │  "
                        f"Status: [bold {color_status}]{model.remaining_percent:.1f}% Available[/bold {color_status}]"
                    )

                # Update progress bar
                if model.id in self.progress_widgets:
                    pbar = self.progress_widgets[model.id]
                    pbar.progress = model.remaining_percent

    # =========================================================================
    # Agent Hub Handlers
    # =========================================================================
    def populate_agents_list(self) -> None:
        self.agent_loader.reload()
        option_list = self.query_one("#agent_option_list", OptionList)
        option_list.clear_options()

        agents = self.agent_loader.get_agent_list()
        if not agents:
            option_list.add_option(Option("No agents found in agents/", id="none"))
            return

        for meta in agents:
            label = f"🤖 {meta['name']} [dim]({meta['category']} • v{meta['version']})[/dim]"
            option_list.add_option(Option(label, id=meta["id"]))

        # Select first agent by default
        if agents:
            self.select_agent(agents[0]["id"])
            option_list.highlighted = 0

    def on_option_list_option_selected(self, event: OptionList.OptionSelected) -> None:
        if event.option_id and event.option_id != "none":
            self.select_agent(str(event.option_id))

    def select_agent(self, agent_id: str) -> None:
        self.selected_agent_id = agent_id
        agent = self.agent_loader.get_agent(agent_id)
        if not agent:
            return

        meta = self.agent_loader.agent_metadata.get(agent_id, {})
        title_widget = self.query_one("#agent_detail_title", Static)
        desc_widget = self.query_one("#agent_detail_desc", Static)
        input_field = self.query_one("#agent_input_field", Input)
        status_badge = self.query_one("#agent_status_badge", Static)

        title_widget.update(
            f"🎯 [bold cyan]{meta.get('name', 'Agent')}[/bold cyan]  "
            f"[dim]Category: {meta.get('category')}  │  Author: {meta.get('author')}  │  File: {meta.get('file')}[/dim]"
        )
        desc_widget.update(f"[italic]{meta.get('description', '')}[/italic]")
        input_field.value = meta.get("default_input", "")

        status = self.process_manager.get_status(agent_id)
        status_badge.update(f"Status: [bold yellow]{status}[/bold yellow]")

    # =========================================================================
    # Project Center Handlers
    # =========================================================================
    def populate_projects_list(self) -> None:
        container = self.query_one("#project_card_list", Vertical)
        container.remove_children()

        for proj in self.project_manager.list_projects():
            is_running = proj.status == "RUNNING"
            status_style = "project-running" if is_running else "project-stopped"
            status_icon = "🟢 RUNNING" if is_running else "🔴 STOPPED"
            btn_label = "⏹ Stop" if is_running else "▶ Start"
            btn_variant = "error" if is_running else "success"

            card = Vertical(
                Horizontal(
                    Static(f"📦 [bold white]{proj.name}[/bold white]  [dim]({proj.category})[/dim]", classes="stat-badge"),
                    Static(
                        f"State: [bold]{status_icon}[/bold]  │  "
                        f"PID: [cyan]{proj.pid or 'N/A'}[/cyan]  │  "
                        f"Uptime: [yellow]{proj.uptime}[/yellow]"
                    ),
                    Button(btn_label, id=f"btn_toggle_proj_{proj.id}", variant=btn_variant),
                    Button("View Logs", id=f"btn_view_proj_{proj.id}", variant="default"),
                ),
                Static(f"  [dim]Command: {proj.command}  │  Entry: {proj.entry_point}[/dim]"),
                classes=f"project-card {status_style}",
                id=f"card_{proj.id}",
            )
            container.mount(card)

    def display_project_logs(self, project_id: str) -> None:
        self.selected_project_id = project_id
        project = self.project_manager.get_project(project_id)
        log_view = self.query_one("#project_log_view", RichLog)
        log_view.clear()
        if not project:
            return

        log_view.write(f"[bold cyan]=== Live Logs: {project.name} (PID: {project.pid or 'OFFLINE'}) ===[/bold cyan]")
        for line in project.logs:
            log_view.write(f"[dim]{line}[/dim]")

    # =========================================================================
    # Button Click Handling
    # =========================================================================
    def on_button_pressed(self, event: Button.Pressed) -> None:
        btn_id = event.button.id

        # Quota Tab Buttons
        if btn_id == "btn_sync_quotas":
            self.quota_monitor.refresh_data()
            self.update_quota_timers()
            self.notify("API Quota metrics synchronized with gateway.", title="Synced")

        elif btn_id == "btn_simulate_burst":
            # Simulate high traffic burst by reducing quota
            for acc in self.quota_monitor.accounts:
                for m in acc.models:
                    m.remaining_percent = max(10.0, m.remaining_percent - 15.0)
            self.update_quota_timers()
            self.notify("Simulated burst load applied (-15% quota across models)", title="Simulated Traffic")

        # Agent Tab Buttons
        elif btn_id == "btn_rescan_agents":
            self.populate_agents_list()
            self.notify("Rescanned agents directory. Agent registry updated!", title="Discovery")

        elif btn_id == "btn_clear_agent_log":
            self.query_one("#agent_log_view", RichLog).clear()

        elif btn_id == "btn_run_agent":
            self.execute_current_agent()

        elif btn_id == "btn_stop_agent":
            self.stop_current_agent()

        # Project Tab Buttons
        elif btn_id == "btn_start_all_projects":
            for p in self.project_manager.list_projects():
                self.project_manager.start_project(p.id)
            self.populate_projects_list()
            self.notify("All local projects started.", title="Project Center")

        elif btn_id == "btn_stop_all_projects":
            for p in self.project_manager.list_projects():
                self.project_manager.stop_project(p.id)
            self.populate_projects_list()
            self.notify("All local projects stopped.", title="Project Center")

        elif btn_id == "btn_refresh_projects":
            self.populate_projects_list()

        elif btn_id and btn_id.startswith("btn_toggle_proj_"):
            proj_id = btn_id.replace("btn_toggle_proj_", "")
            self.project_manager.toggle_project(proj_id)
            self.populate_projects_list()
            self.display_project_logs(proj_id)

        elif btn_id and btn_id.startswith("btn_view_proj_"):
            proj_id = btn_id.replace("btn_view_proj_", "")
            self.display_project_logs(proj_id)

    # =========================================================================
    # Agent Execution Engine
    # =========================================================================
    def execute_current_agent(self) -> None:
        if not self.selected_agent_id:
            self.notify("Please select an agent first.", severity="warning")
            return

        agent = self.agent_loader.get_agent(self.selected_agent_id)
        if not agent:
            return

        input_field = self.query_one("#agent_input_field", Input)
        user_input = input_field.value.strip()

        btn_run = self.query_one("#btn_run_agent", Button)
        btn_stop = self.query_one("#btn_stop_agent", Button)
        status_badge = self.query_one("#agent_status_badge", Static)
        log_view = self.query_one("#agent_log_view", RichLog)

        btn_run.disabled = True
        btn_stop.disabled = False
        status_badge.update("Status: [bold green]RUNNING ⏳[/bold green]")

        log_view.write(f"\n[bold blue]{'═'*60}[/bold blue]")
        cur_ts = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        log_view.write(f"[bold cyan]▶ Launching Agent:[/bold cyan] {agent.name} at {cur_ts}")
        log_view.write(f"[bold dim]Input:[/bold dim] {user_input or '(None)'}\n")

        def stream_callback(event: Dict[str, Any]):
            # Thread-safe dispatch to Textual main loop
            self.call_from_thread(self._handle_agent_stream_event, event)

        def completion_callback(agent_id: str, success: bool):
            self.call_from_thread(self._handle_agent_completion, agent_id, success)

        self.process_manager.run_agent(
            agent_id=self.selected_agent_id,
            agent=agent,
            input_text=user_input,
            log_callback=stream_callback,
            completion_callback=completion_callback,
        )

    def _handle_agent_stream_event(self, event: Dict[str, Any]) -> None:
        log_view = self.query_one("#agent_log_view", RichLog)
        msg_type = event.get("type", "log")
        message = event.get("message", "")
        cur_time = datetime.now().strftime("%H:%M:%S")

        if msg_type == "step":
            log_view.write(f"[dim]{cur_time}[/dim] 🔷 [bold white]{message}[/bold white]")
        elif msg_type == "warning":
            log_view.write(f"[dim]{cur_time}[/dim] ⚠️ [bold yellow]{message}[/bold yellow]")
        elif msg_type == "error":
            log_view.write(f"[dim]{cur_time}[/dim] ❌ [bold red]{message}[/bold red]")
        elif msg_type == "result":
            log_view.write(f"\n[dim]{cur_time}[/dim] 🎯 [bold green]{message}[/bold green]")
            data = event.get("data")
            if data:
                log_view.write(f"  [dim cyan]Payload Result:[/dim cyan] {data}")
        else:
            log_view.write(f"[dim]{cur_time}[/dim]  {message}")

    def _handle_agent_completion(self, agent_id: str, success: bool) -> None:
        btn_run = self.query_one("#btn_run_agent", Button)
        btn_stop = self.query_one("#btn_stop_agent", Button)
        status_badge = self.query_one("#agent_status_badge", Static)
        log_view = self.query_one("#agent_log_view", RichLog)

        btn_run.disabled = False
        btn_stop.disabled = True

        status = self.process_manager.get_status(agent_id)
        if status == "STOPPED":
            status_badge.update("Status: [bold yellow]STOPPED[/bold yellow]")
            log_view.write("\n[bold yellow]Agent execution stopped by user request.[/bold yellow]")
        elif success:
            status_badge.update("Status: [bold green]FINISHED[/bold green]")
            log_view.write("\n[bold green]✔ Execution completed successfully.[/bold green]")
        else:
            status_badge.update("Status: [bold red]FAILED[/bold red]")
            log_view.write("\n[bold red]✖ Execution failed.[/bold red]")

    def stop_current_agent(self) -> None:
        if self.selected_agent_id:
            self.process_manager.stop_agent(self.selected_agent_id)
            self.query_one("#agent_status_badge", Static).update("Status: [bold yellow]STOPPING...[/bold yellow]")


if __name__ == "__main__":
    app = AgentOpsApp()
    app.run()
