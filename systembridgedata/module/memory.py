"""Memory."""

from psutil import swap_memory, virtual_memory
from systembridgemodels.modules.memory import MemorySwap, MemoryVirtual

from systembridgeshared.base import Base


class Memory(Base):
    """Memory data."""

    def get_swap(self) -> MemorySwap:
        """Swap memory."""
        data = swap_memory()
        return MemorySwap(
            total=data.total,
            used=data.used,
            free=data.free,
            percent=data.percent,
            sin=data.sin,
            sout=data.sout,
        )

    def get_virtual(self) -> MemoryVirtual:
        """Virtual memory."""
        data = virtual_memory()
        return MemoryVirtual(
            total=data.total,
            available=data.available,
            percent=data.percent,
            used=data.used,
            free=data.free,
        )
