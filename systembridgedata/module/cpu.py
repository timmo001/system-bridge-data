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
from psutil._common import shwtemp
from systembridgemodels.modules.cpu import CPUFrequency, CPUStats, CPUTimes
from systembridgemodels.modules.sensors import Sensors

from systembridgeshared.base import Base


class CPU(Base):
    """CPU data."""

    def __init__(self) -> None:
        """Initialise."""
        super().__init__()

        self._count: int = cpu_count()

        self.sensors: Sensors | None = None

    def get_frequency(self) -> CPUFrequency:
        """CPU frequency."""
        data = cpu_freq()
        return CPUFrequency(
            current=data.current,
            min=data.min,
            max=data.max,
        )

    def get_frequency_per_cpu(
        self,
    ) -> list[CPUFrequency]:
        """CPU frequency per CPU."""
        data = cpu_freq(percpu=True)

        return [
            CPUFrequency(
                current=item.current,  # type: ignore
                min=item.min,  # type: ignore
                max=item.max,  # type: ignore
            )
            for item in data
        ]

    def get_load_average(self) -> float:
        """Get load average."""
        avg_tuple = getloadavg()
        return sum([avg_tuple[0], avg_tuple[1], avg_tuple[2]]) / 3

    def get_power_package(self) -> float | None:
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

    def get_power_per_cpu(self) -> list[float] | None:
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

    def get_stats(self) -> CPUStats:
        """CPU stats."""
        data = cpu_stats()
        return CPUStats(
            ctx_switches=data.ctx_switches,
            interrupts=data.interrupts,
            soft_interrupts=data.soft_interrupts,
            syscalls=data.syscalls,
        )

    def get_temperature(self) -> float | None:
        """CPU temperature."""
        if self.sensors is not None:
            if self.sensors.temperatures is not None:
                temperatures: dict[str, list[shwtemp]
                                   ] = self.sensors.temperatures
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

    def get_times(self) -> CPUTimes:
        """CPU times."""
        data = cpu_times(percpu=False)
        return CPUTimes(
            user=data.user,
            system=data.system,
            idle=data.idle,
            interrupt=data.interrupt if hasattr(data, "interrupt") else None,
            dpc=data.dpc if hasattr(data, "dpc") else None,
        )

    def get_times_percent(self) -> CPUTimes:
        """CPU times percent."""
        data = cpu_times_percent(interval=1, percpu=False)
        return CPUTimes(
            user=data.user,
            system=data.system,
            idle=data.idle,
            interrupt=data.interrupt
            if hasattr(data, "interrupt")
            else None,
            dpc=data.dpc if hasattr(data, "dpc") else None,
        )

    def get_times_per_cpu(
        self,
    ) -> list[CPUTimes]:
        """CPU times per CPU."""
        data = cpu_times(percpu=True)

        return [
            CPUTimes(
                user=item.user,
                system=item.system,
                idle=item.idle,
                interrupt=item.interrupt if hasattr(
                    item, "interrupt") else None,
                dpc=item.dpc if hasattr(item, "dpc") else None,
            )
            for item in data
        ]

    def get_times_per_cpu_percent(
        self,
    ) -> list[CPUTimes]:
        """CPU times per CPU percent."""
        data = cpu_times_percent(interval=1, percpu=True)

        return [
            CPUTimes(
                user=item.user,
                system=item.system,
                idle=item.idle,
                interrupt=item.interrupt if hasattr(
                    item, "interrupt") else None,
                dpc=item.dpc if hasattr(item, "dpc") else None,
            )
            for item in data
        ]

    def get_usage(self) -> float:
        """CPU usage."""
        return cpu_percent(interval=1, percpu=False)

    def get_usage_per_cpu(
        self,
    ) -> list[float]:
        """CPU usage per CPU."""
        return cpu_percent(interval=1, percpu=True)  # type: ignore

    def get_voltages(self) -> tuple[float | None, list[float]]:
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
