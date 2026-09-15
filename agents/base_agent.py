"""
Base Agent Interface for AgentOps Command Center
All modular agents in the `agents/` directory should inherit from BaseAgent
to enable automatic discovery, execution, and real-time streaming to the UI.
"""

from abc import ABC, abstractmethod
from typing import Iterator, Dict, Any, Optional
import time


class BaseAgent(ABC):
    """
    Abstract Base Class for modular agents.
    Subclasses defined in any .py file under `agents/` will be automatically
    discovered and loaded into the Agent Hub.
    """
    name: str = "Base Agent"
    description: str = "Base template for AgentOps agents"
    version: str = "1.0.0"
    category: str = "General"
    author: str = "AgentOps Core"
    default_input: str = ""

    def __init__(self):
        self._stop_requested = False

    def request_stop(self):
        self._stop_requested = True

    def is_stopped(self) -> bool:
        return self._stop_requested

    @abstractmethod
    def run(self, input_text: str) -> Iterator[Dict[str, Any]]:
        """
        Execute the agent workflow and yield real-time events.
        
        Yield format:
        {
            "type": "log" | "step" | "warning" | "error" | "result",
            "message": str,
            "timestamp": Optional[float],
            "data": Optional[Any]
        }
        """
        pass

    def emit(self, msg_type: str, message: str, data: Optional[Any] = None) -> Dict[str, Any]:
        """Helper to create standardized stream payloads."""
        return {
            "type": msg_type,
            "message": message,
            "timestamp": time.time(),
            "data": data,
        }

