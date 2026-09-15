"""
Dynamic Agent Discovery and Loader Module
Scans the `agents/` directory, discovers all classes inheriting from BaseAgent,
and instantiates them. Automatically picks up new agent files added at runtime.
"""

import os
import sys
import importlib
import importlib.util
import inspect
from pathlib import Path
from typing import Dict, List, Type
from agents.base_agent import BaseAgent


class AgentLoader:
    def __init__(self, agents_dir: str = None):
        if agents_dir is None:
            # Default to the agents/ directory in project root
            self.agents_dir = Path(__file__).resolve().parent.parent / "agents"
        else:
            self.agents_dir = Path(agents_dir)

        self.agents: Dict[str, BaseAgent] = {}
        self.agent_metadata: Dict[str, Dict[str, str]] = {}
        self.reload()

    def reload(self) -> Dict[str, BaseAgent]:
        """
        Scans the agents/ directory and dynamically loads all BaseAgent classes.
        """
        self.agents.clear()
        self.agent_metadata.clear()

        if not self.agents_dir.exists():
            return self.agents

        # Ensure project root is in sys.path
        root_dir = str(self.agents_dir.parent)
        if root_dir not in sys.path:
            sys.path.insert(0, root_dir)

        for file_path in self.agents_dir.glob("*.py"):
            filename = file_path.name
            if filename in ("__init__.py", "base_agent.py"):
                continue

            module_name = f"agents.{file_path.stem}"
            try:
                # Reload module if already imported, else import fresh
                if module_name in sys.modules:
                    module = importlib.reload(sys.modules[module_name])
                else:
                    spec = importlib.util.spec_from_file_location(module_name, str(file_path))
                    if spec and spec.loader:
                        module = importlib.util.module_from_spec(spec)
                        sys.modules[module_name] = module
                        spec.loader.exec_module(module)
                    else:
                        continue

                # Inspect module for BaseAgent subclasses
                for attr_name in dir(module):
                    attr = getattr(module, attr_name)
                    if (
                        inspect.isclass(attr)
                        and issubclass(attr, BaseAgent)
                        and attr is not BaseAgent
                    ):
                        agent_id = f"{file_path.stem}.{attr.__name__}"
                        instance = attr()
                        self.agents[agent_id] = instance
                        self.agent_metadata[agent_id] = {
                            "id": agent_id,
                            "name": getattr(instance, "name", attr.__name__),
                            "description": getattr(instance, "description", "No description"),
                            "version": getattr(instance, "version", "1.0.0"),
                            "category": getattr(instance, "category", "General"),
                            "author": getattr(instance, "author", "Unknown"),
                            "default_input": getattr(instance, "default_input", ""),
                            "file": filename,
                        }
            except Exception as e:
                print(f"[AgentLoader] Error loading {file_path}: {e}", file=sys.stderr)

        return self.agents

    def get_agent_list(self) -> List[Dict[str, str]]:
        return list(self.agent_metadata.values())

    def get_agent(self, agent_id: str) -> BaseAgent:
        return self.agents.get(agent_id)

