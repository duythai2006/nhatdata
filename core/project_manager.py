"""
Local Project Manager
Handles starting, stopping, toggling, and tracking local project services.
"""

import random
import time
from typing import List, Optional, Dict
from projects.project_registry import LocalProject, get_default_projects


class ProjectManager:
    def __init__(self):
        self._projects: Dict[str, LocalProject] = {
            p.id: p for p in get_default_projects()
        }

    def list_projects(self) -> List[LocalProject]:
        return list(self._projects.values())

    def get_project(self, project_id: str) -> Optional[LocalProject]:
        return self._projects.get(project_id)

    def start_project(self, project_id: str) -> bool:
        project = self._projects.get(project_id)
        if not project:
            return False

        if project.status == "RUNNING":
            return True

        project.status = "RUNNING"
        project.pid = random.randint(20000, 65000)
        project.started_at = time.time()
        cur_time = time.strftime("%H:%M:%S")
        project.logs.append(f"[{cur_time}] Service started with PID {project.pid} via '{project.command}'.")
        return True

    def stop_project(self, project_id: str) -> bool:
        project = self._projects.get(project_id)
        if not project:
            return False

        if project.status == "STOPPED":
            return True

        cur_time = time.strftime("%H:%M:%S")
        project.logs.append(f"[{cur_time}] Graceful shutdown requested for PID {project.pid}.")
        project.status = "STOPPED"
        project.pid = None
        project.started_at = None
        return True

    def toggle_project(self, project_id: str) -> bool:
        project = self._projects.get(project_id)
        if not project:
            return False

        if project.status == "RUNNING":
            return self.stop_project(project_id)
        else:
            return self.start_project(project_id)

