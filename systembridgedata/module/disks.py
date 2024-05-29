"""Disks."""

from psutil import disk_io_counters, disk_partitions, disk_usage
from psutil._common import sdiskio, sdiskpart, sdiskusage

from systembridgeshared.base import Base


class Disks(Base):
    """Disks data."""

    def get_io_counters(self) -> sdiskio | None:
        """Disk IO counters."""
        return disk_io_counters()

    def get_io_counters_per_disk(self) -> dict[str, sdiskio]:
        """Disk IO counters per disk."""
        return disk_io_counters(perdisk=True)

    def get_partitions(self) -> list[sdiskpart]:
        """Disk partitions."""
        return disk_partitions(all=True)

    def get_usage(self, path: str) -> sdiskusage | None:
        """Disk usage."""
        try:
            return disk_usage(path)
        except (FileNotFoundError, PermissionError) as error:
            self._logger.warning(
                "Error getting disk usage for: %s",
                path,
                exc_info=error,
            )
            return None
