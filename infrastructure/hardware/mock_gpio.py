from __future__ import annotations

from infrastructure.config.runtime_config import RuntimeConfig
from infrastructure.hardware.base import BaseGardenHardware


class MockGardenHardware(BaseGardenHardware):
    def __init__(self, runtime_config: RuntimeConfig) -> None:
        self._light_on = False
        self._water_on = False
        self._fertilizer_on = False
        super().__init__(runtime_config)

    def _initialize_outputs(self) -> None:
        print("🔧 Режим эмуляции GPIO")

    def _light_is_on(self) -> bool:
        return self._light_on

    def _set_light_output(self, state: bool) -> None:
        self._light_on = state

    def _set_water_output(self, state: bool) -> None:
        self._water_on = state

    def _set_fertilizer_output(self, state: bool) -> None:
        self._fertilizer_on = state

    def _safe_turn_off_outputs(self) -> None:
        self._light_on = False
        self._water_on = False
        self._fertilizer_on = False
