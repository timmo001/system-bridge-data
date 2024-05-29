"""Memory."""

from typing import NamedTuple

from psutil import swap_memory, virtual_memory
from psutil._common import sswap

from systembridgeshared.base import Base


class Memory(Base):
    """Memory data."""

    async def get_swap(self) -> sswap:
        """Swap memory."""
        return swap_memory()

    async def get_virtual(self) -> NamedTuple:
        """Virtual memory."""
        return virtual_memory()
