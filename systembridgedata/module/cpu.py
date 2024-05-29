"""CPU."""

from psutil import (
    cpu_count,
    cpu_freq,
    cpu_percent,
    cpu_stats,
    cpu_times,
    cpu_times_percent,
    getloadavg,
)
from psutil._common import pcputimes, scpufreq, scpustats, shwtemp
from systembridgemodels.modules.sensors import Sensors

from systembridgeshared.base import Base


class CPU(Base):
    """CPU data."""

    def __init__(self) -> None:
        """Initialise."""
        super().__init__()

        self._count: int = cpu_count()

        self.sensors: Sensors | None = None

    async def get_frequency(self) -> scpufreq:
        """CPU frequency."""
        return cpu_freq()

    async def get_frequency_per_cpu(
        self,
    ) -> list[scpufreq]:
        """CPU frequency per CPU."""
        return cpu_freq(percpu=True)  # type: ignore

    async def get_load_average(self) -> float:
        """Get load average."""
        avg_tuple = getloadavg()
        return sum([avg_tuple[0], avg_tuple[1], avg_tuple[2]]) / 3

    async def get_power_package(self) -> float | None:
        """CPU package power."""
        if (
            self.sensors is None
            or self.sensors.windows_sensors is None
            or self.sensors.windows_sensors.hardware is None
        ):
            return None
        for hardware in self.sensors.windows_sensors.hardware:
            # Find type "CPU"
            if "CPU" not in hardware.type.upper():
                continue
            for sensor in hardware.sensors:
                # Find type "POWER" and name "PACKAGE"
                if (
                    "POWER" in sensor.type.upper()
                    and "PACKAGE" in sensor.name.upper()
                    and sensor.value is not None
                ):
                    self._logger.debug(
                        "Found CPU package power: %s = %s", sensor.name, sensor.value
                    )
                    return (
                        float(sensor.value)
                        if isinstance(sensor.value, (int, float))
                        else None
                    )
        return None

    async def get_power_per_cpu(self) -> list[float] | None:
        """CPU package power."""
        powers: list[float] = [-1] * self._count
        if (
            self.sensors is None
            or self.sensors.windows_sensors is None
            or self.sensors.windows_sensors.hardware is None
        ):
            return None
        for hardware in self.sensors.windows_sensors.hardware:
            # Find type "CPU"
            if "CPU" not in hardware.type.upper():
                continue
            for sensor in hardware.sensors:
                # Find type "POWER" and name "CORE"
                if (
                    "POWER" in sensor.type.upper()
                    and "CORE" in sensor.name.upper()
                    and sensor.value is not None
                ):
                    self._logger.debug(
                        "Found CPU core power: %s (%s) = %s",
                        sensor.name,
                        sensor.id,
                        sensor.value,
                    )
                    for sensor in hardware.sensors:
                        # Find type "POWER" and name "PACKAGE"
                        if (
                            "POWER" in sensor.type.upper()
                            and "PACKAGE" not in sensor.name.upper()
                            and sensor.value is not None
                        ):
                            self._logger.debug(
                                "Found CPU package power: %s (%s) = %s",
                                sensor.name,
                                sensor.id,
                                sensor.value,
                            )
                            index = int(sensor.id.split("/")[-1])
                            powers[index] = float(sensor.value)

        return powers

    async def get_stats(self) -> scpustats:
        """CPU stats."""
        return cpu_stats()

    async def get_temperature(self) -> float | None:
        """CPU temperature."""
        if self.sensors is not None:
            if self.sensors.temperatures is not None:
                temperatures: dict[str, list[shwtemp]] = self.sensors.temperatures
                if "k10temp" in temperatures:
                    for sensor in self.sensors.temperatures["k10temp"]:
                        self._logger.debug("k10temp: %s", sensor)
                        if "Tdie" in sensor or "Tctl" in sensor or "Tccd1" in sensor:
                            self._logger.debug(
                                "Found CPU temperature (k10temp): %s",
                                sensor,
                            )
                            return sensor.current
                if "coretemp" in self.sensors.temperatures:
                    for sensor in self.sensors.temperatures["coretemp"]:
                        self._logger.debug("coretemp: %s", sensor)
                        if (
                            "Package id 0" in sensor
                            or "Physical id 0" in sensor
                            or "Core 0" in sensor
                        ):
                            self._logger.debug(
                                "Found CPU temperature (coretemp): %s",
                                sensor,
                            )
                            return sensor.current
                if "atk0110" in self.sensors.temperatures:
                    for sensor in self.sensors.temperatures["atk0110"]:
                        self._logger.debug("atk0110: %s", sensor)
                        if "CPU" in sensor:
                            self._logger.debug(
                                "Found CPU temperature (atk0110): %s",
                                sensor,
                            )
                            return sensor.current
                # Use the first temperature sensor key
                for key in temperatures:
                    for sensor in temperatures[key]:
                        self._logger.warning(
                            "Unknown sensor used (may not be correct): %s", sensor
                        )
                        return sensor.current
            if (
                self.sensors.windows_sensors is not None
                and self.sensors.windows_sensors.hardware is not None
            ):
                for hardware in self.sensors.windows_sensors.hardware:
                    # Find type "CPU"
                    if "CPU" not in hardware.type.upper():
                        continue
                    for sensor in hardware.sensors:
                        name = sensor.name.upper()
                        # Find type "TEMPERATURE" and name "PACKAGE" or "AVERAGE"
                        if (
                            "TEMPERATURE" in sensor.type.upper()
                            and ("PACKAGE" in name or "AVERAGE" in name)
                            and sensor.value is not None
                        ):
                            self._logger.debug(
                                "Found CPU temperature: %s = %s",
                                sensor.name,
                                sensor.value,
                            )
                            return (
                                float(sensor.value)
                                if isinstance(sensor.value, (int, float, str))
                                else None
                            )
        return None

    async def get_times(self) -> pcputimes:
        """CPU times."""
        return cpu_times(percpu=False)

    async def get_times_percent(self) -> pcputimes:
        """CPU times percent."""
        return cpu_times_percent(interval=1, percpu=False)

    async def get_times_per_cpu(
        self,
    ) -> list[pcputimes]:
        """CPU times per CPU."""
        return cpu_times(percpu=True)

    async def get_times_per_cpu_percent(
        self,
    ) -> list[pcputimes]:
        """CPU times per CPU percent."""
        return cpu_times_percent(interval=1, percpu=True)

    async def get_usage(self) -> float:
        """CPU usage."""
        return cpu_percent(interval=1, percpu=False)

    async def get_usage_per_cpu(
        self,
    ) -> list[float]:
        """CPU usage per CPU."""
        return cpu_percent(interval=1, percpu=True)  # type: ignore

    async def get_voltages(self) -> tuple[float | None, list[float]]:
        """CPU voltage."""
        voltage: float | None = None
        voltages: list[float] = [-1] * self._count
        voltage_sensors = []
        if (
            self.sensors is None
            or self.sensors.windows_sensors is None
            or self.sensors.windows_sensors.hardware is None
        ):
            return (voltage, voltages)
        for hardware in self.sensors.windows_sensors.hardware:
            # Find type "CPU"
            if "CPU" not in hardware.type.upper():
                continue
            for sensor in hardware.sensors:
                # Find type "VOLTAGE"
                if "VOLTAGE" in sensor.type.upper() and sensor.value is not None:
                    self._logger.debug(
                        "Found CPU voltage: %s (%s) = %s",
                        sensor.name,
                        sensor.id,
                        sensor.value,
                    )
                    voltage_sensors.append(sensor)

        # Handle voltages
        if voltage_sensors is not None and len(voltage_sensors) > 0:
            for sensor in voltage_sensors:
                if sensor.value is not None:
                    self._logger.debug(
                        "CPU voltage: %s (%s) = %s",
                        sensor.name,
                        sensor.type,
                        sensor.value,
                    )
                    # "/amdcpu/0/voltage/16" -> 16
                    # Get the last part of the id
                    index = int(sensor.id.split("/")[-1])
                    if 0 <= index < self._count:
                        voltages[index] = float(sensor.value)
            voltage_sum = 0
            for voltage in voltages:
                if voltage is not None:
                    voltage_sum += voltage
            if voltage_sum > 0:
                voltage = voltage_sum / self._count
            else:
                # If we can't get the average, just use the first value
                voltage = voltage_sensors[0].value

        return (voltage, voltages)