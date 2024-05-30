"""Processes."""
from psutil import AccessDenied, NoSuchProcess, process_iter
from systembridgemodels.modules.processes import Process

from systembridgeshared.base import Base


class Processes(Base):
    """Processes data."""

    async def get_processes(self) -> list[Process]:
        """Update all data."""
        process_list = list(process_iter())

        # Get names of processes
        items = []
        for process in process_list:
            model = Process(id=process.pid)

            try:
                model.name = process.name()
                model.cpu_usage = process.cpu_percent()
                model.created = process.create_time()
                model.memory_usage = process.memory_percent()
                model.path = process.exe()
                model.status = process.status()
                model.username = process.username()
            except (AccessDenied, NoSuchProcess, OSError):
                pass
            items.append(model)
        # Sort by name
        items = sorted(items, key=lambda item: item.name or "")

        return items
