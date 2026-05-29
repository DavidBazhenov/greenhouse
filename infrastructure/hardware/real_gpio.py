from __future__ import annotations

from infrastructure.config.runtime_config import RuntimeConfig
from infrastructure.hardware.base import BaseGardenHardware

try:
    from gpiozero import LED, DigitalOutputDevice

    GPIOZERO_AVAILABLE = True
except Exception:
    GPIOZERO_AVAILABLE = False
    LED = None
    DigitalOutputDevice = None


class RealGardenHardware(BaseGardenHardware):
    def __init__(self, runtime_config: RuntimeConfig) -> None:
        self.led = None
        self.water_pump = None
        self.fertilizer_pump = None
        super().__init__(runtime_config)

    def _initialize_outputs(self) -> None:
        if not GPIOZERO_AVAILABLE:
            raise RuntimeError("gpiozero is not available")

        pin_mapping = self.runtime_config.pin_mapping
        self.led = LED(pin_mapping.light)
        self.water_pump = DigitalOutputDevice(pin_mapping.water, active_high=False)
        self.fertilizer_pump = DigitalOutputDevice(pin_mapping.fertilizer, active_high=False)
        print("🔧 Режим реального Raspberry Pi")
        print("✅ Оборудование инициализировано")

    def _light_is_on(self) -> bool:
        return bool(self.led and self.led.is_lit)

    def _set_light_output(self, state: bool) -> None:
        if self.led is None:
            return
        if state:
            self.led.on()
        else:
            self.led.off()

    def _set_water_output(self, state: bool) -> None:
        if self.water_pump is None:
            return
        if state:
            self.water_pump.on()
        else:
            self.water_pump.off()

    def _set_fertilizer_output(self, state: bool) -> None:
        if self.fertilizer_pump is None:
            return
        if state:
            self.fertilizer_pump.on()
        else:
            self.fertilizer_pump.off()

    def _safe_turn_off_outputs(self) -> None:
        self._set_light_output(False)
        self._set_water_output(False)
        self._set_fertilizer_output(False)
