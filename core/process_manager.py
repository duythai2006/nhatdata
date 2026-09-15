"""
Process and Execution Manager Module
Coordinates threaded/asynchronous execution of agents, provides non-blocking
log streaming to the UI, and allows graceful termination.
"""

import threading
import time
from typing import Callable, Dict, Any, Optional
from agents.base_agent import BaseAgent


class AgentProcess:
    def __init__(
        self,
        agent_id: str,
        agent: BaseAgent,
        input_text: str,
        log_callback: Callable[[Dict[str, Any]], None],
        completion_callback: Optional[Callable[[str, bool], None]] = None,
    ):
        self.agent_id = agent_id
        self.agent = agent
        self.input_text = input_text
        self.log_callback = log_callback
        self.completion_callback = completion_callback
        self.thread: Optional[threading.Thread] = None
        self.status = "IDLE"
        self.start_time: Optional[float] = None
        self.end_time: Optional[float] = None

    def start(self):
        self.status = "RUNNING"
        self.start_time = time.time()
        self.thread = threading.Thread(target=self._run_worker, daemon=True)
        self.thread.start()

    def stop(self):
        if self.status == "RUNNING":
            self.status = "STOPPING"
            self.agent.request_stop()

    def _run_worker(self):
        success = True
        try:
            for event in self.agent.run(self.input_text):
                if self.agent.is_stopped():
                    self.status = "STOPPED"
                    break
                self.log_callback(event)
        except Exception as e:
            success = False
            self.status = "ERROR"
            self.log_callback({
                "type": "error",
                "message": f"❌ Agent execution failed with exception: {e}",
                "timestamp": time.time(),
            })
        finally:
            self.end_time = time.time()
            if self.status != "STOPPED" and self.status != "ERROR":
                self.status = "FINISHED"

            if self.completion_callback:
                self.completion_callback(self.agent_id, success)


class ProcessManager:
    def __init__(self):
        self.active_processes: Dict[str, AgentProcess] = {}

    def run_agent(
        self,
        agent_id: str,
        agent: BaseAgent,
        input_text: str,
        log_callback: Callable[[Dict[str, Any]], None],
        completion_callback: Optional[Callable[[str, bool], None]] = None,
    ) -> AgentProcess:
        # Stop existing process for this agent if running
        if agent_id in self.active_processes:
            prev = self.active_processes[agent_id]
            if prev.status == "RUNNING":
                prev.stop()

        process = AgentProcess(
            agent_id=agent_id,
            agent=agent,
            input_text=input_text,
            log_callback=log_callback,
            completion_callback=completion_callback,
        )
        self.active_processes[agent_id] = process
        process.start()
        return process

    def stop_agent(self, agent_id: str):
        if agent_id in self.active_processes:
            self.active_processes[agent_id].stop()

    def get_status(self, agent_id: str) -> str:
        if agent_id in self.active_processes:
            return self.active_processes[agent_id].status
        return "IDLE"

    def is_running(self, agent_id: str) -> bool:
        return self.get_status(agent_id) in ("RUNNING", "STOPPING")

