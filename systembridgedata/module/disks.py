"""Disks."""

from psutil import disk_io_counters, disk_partitions, disk_usage
from systembridgemodels.modules.disks import DiskIOCounters, DiskPartition, DiskUsage

from systembridgeshared.base import Base


class Disks(Base):
    """Disks data."""

    def get_io_counters(self) -> DiskIOCounters | None:
        """Disk IO counters."""
        if (data := disk_io_counters()) is None:
            return None

        return DiskIOCounters(
            read_bytes=data.read_bytes,
            write_bytes=data.write_bytes,
            read_count=data.read_count,
            write_count=data.write_count,
            read_time=data.read_time,
            write_time=data.write_time,
        )

    def get_io_counters_per_disk(self) -> dict[str, DiskIOCounters]:
        """Disk IO counters per disk."""
        result: dict[str, DiskIOCounters] = {}
        if (data := disk_io_counters(perdisk=True)) is None:
            return result

        for disk, counters in data.items():
            result[disk] = DiskIOCounters(
                read_bytes=counters.read_bytes,
                write_bytes=counters.write_bytes,
                read_count=counters.read_count,
                write_count=counters.write_count,
                read_time=counters.read_time,
                write_time=counters.write_time,
            )

        return result

    def get_partitions(self) -> list[DiskPartition]:
        """Disk partitions."""
        data = disk_partitions(all=True)

        return [
            DiskPartition(
                device=item.device,
                mount_point=item.mountpoint,
                filesystem_type=item.fstype,
                options=item.opts,
                max_file_size=item.maxfile,
                max_path_length=item.maxpath,
                usage=self.get_usage(item.mountpoint),
            )
            for item in data
        ]

    def get_usage(self, path: str) -> DiskUsage | None:
        """Disk usage."""
        try:
            data = disk_usage(path)
            return DiskUsage(
                total=data.total,
                used=data.used,
                free=data.free,
                percent=data.percent,
            )
        except (FileNotFoundError, PermissionError) as error:
            self._logger.warning(
                "Error getting disk usage for: %s",
                path,
                exc_info=error,
            )
            return None
