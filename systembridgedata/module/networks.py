"""Network."""

from psutil import net_connections, net_if_addrs, net_if_stats, net_io_counters
from systembridgemodels.modules.networks import (
    NetworkAddress,
    NetworkConnection,
    NetworkIO,
    NetworkStats,
)

from systembridgeshared.base import Base


class Networks(Base):
    """Networks data."""

    def get_addresses(
        self,
    ) -> dict[str, list[NetworkAddress]]:
        """Addresses."""
        data = net_if_addrs()

        result = {}
        for key, value in data.items():
            result[key] = [
                NetworkAddress(
                    address=item.address,
                    netmask=item.netmask,
                    broadcast=item.broadcast,
                    ptp=item.ptp,
                )
                for item in value
            ]

        return result

    def get_connections(self) -> list[NetworkConnection]:
        """Get connections."""
        data = net_connections("all")

        return [
            NetworkConnection(
                fd=item.fd,
                family=item.family,
                type=item.type,
                laddr=str(item.laddr),
                raddr=str(item.raddr),
                status=item.status,
                pid=item.pid,
            )
            for item in data
        ]

    def get_io_counters(self) -> NetworkIO:
        """IO Counters."""
        data = net_io_counters()

        return NetworkIO(
            bytes_sent=data.bytes_sent,
            bytes_recv=data.bytes_recv,
            packets_sent=data.packets_sent,
            packets_recv=data.packets_recv,
            errin=data.errin,
            errout=data.errout,
            dropin=data.dropin,
            dropout=data.dropout,
        )

    def get_stats(self) -> dict[str, NetworkStats]:
        """Stats."""
        data = net_if_stats()

        result = {}
        for key, value in data.items():
            result[key] = NetworkStats(
                isup=value.isup,
                duplex=str(value.duplex),
                speed=value.speed,
                mtu=value.mtu,
                flags=value.flags.split(",") if value.flags else None,
            )

        return result
