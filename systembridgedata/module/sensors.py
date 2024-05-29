"""Sensors."""

import json
import subprocess
import sys

import psutil
from psutil._common import sfan, shwtemp

from systembridgeshared.base import Base


class Sensors(Base):
    """Sensors data."""

    def get_fans(self) -> dict[str, list[sfan]] | None:
        """Get fans."""
        if not hasattr(psutil, "sensors_fans"):
            return None
        return psutil.sensors_fans()  # type: ignore

    def get_temperatures(self) -> dict[str, list[shwtemp]] | None:
        """Get temperatures."""
        if not hasattr(psutil, "sensors_temperatures"):
            return None
        return psutil.sensors_temperatures(fahrenheit=False)  # type: ignore

    def get_windows_sensors(self) -> dict | None:
        """Get windows sensors."""
        if sys.platform != "win32":
            return None

        try:
            # Import here to not raise error when importing file on linux
            # pylint: disable=import-error, import-outside-toplevel
            from systembridgewindowssensors import get_windowssensors_path
        except (ImportError, ModuleNotFoundError) as exception:
            self._logger.warning("Windows sensors not found", exc_info=exception)
            return None

        path = get_windowssensors_path()

        self._logger.debug("Windows sensors path: %s", path)
        try:
            with subprocess.Popen(
                [path],
                stdout=subprocess.PIPE,
            ) as pipe:
                result = pipe.communicate()[0].decode()
            self._logger.debug("Windows sensors result: %s", result)
        except Exception as exception:  # pylint: disable=broad-except
            self._logger.error(
                "Windows sensors error for path: %s", path, exc_info=exception
            )
            return None

        try:
            return json.loads(result)
        except json.decoder.JSONDecodeError as exception:
            self._logger.error("JSONDecodeError", exc_info=exception)
            return None
