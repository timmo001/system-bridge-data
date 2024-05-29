"""Network."""

from psutil import net_connections, net_if_addrs, net_if_stats, net_io_counters
from psutil._common import sconn, snetio, snicaddr, snicstats

from systembridgeshared.base import Base


class Networks(Base):
    """Networks data."""

    def get_addresses(
        self,
    ) -> dict[str, list[snicaddr]]:
        """Addresses."""
        return net_if_addrs()

    def get_connections(self) -> list[sconn]:
        """Get connections."""
        return net_connections("all")

    def get_io_counters(self) -> snetio:
        """IO Counters."""
        return net_io_counters()

    def get_stats(self) -> dict[str, snicstats]:
        """Stats."""
        return net_if_stats()
