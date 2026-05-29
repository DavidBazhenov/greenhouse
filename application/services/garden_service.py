from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime
from uuid import uuid4

from domain.models import GardenState, Plant, PLANT_PRESETS


@dataclass
class PlantCreationResult:
    plant: Plant
    message: str


class GardenService:
    def __init__(self, state: GardenState, hardware, runtime_config=None, state_store=None):
        self.state = state
        self.hardware = hardware
        self.runtime_config = runtime_config
        self.state_store = state_store

    def _calculate_light_schedule(self) -> tuple[int, int]:
        start_hour = 8 if self.runtime_config is None else self.runtime_config.light_start_hour
        light_hours = int(self.state.config["light"])
        if light_hours >= 24:
            return 0, 24
        return start_hour, min(24, start_hour + light_hours)

    def save_state(self) -> None:
        if self.state_store is not None:
            self.state_store.save(self.state)

    def sync_hardware(self) -> None:
        self.hardware.update_garden(self.state.plants)

    def restore_runtime_state(self) -> None:
        if self.state.plants:
            start_hour, end_hour = self._calculate_light_schedule()
            self.hardware.set_light_schedule(start_hour, end_hour)
            self.sync_hardware()
            if self.state.settings.get("auto_mode", True):
                self.hardware.start_auto_mode()

    def add_selected_plant(self) -> PlantCreationResult:
        preset = PLANT_PRESETS[self.state.config["selectedPlant"]]
        now = datetime.now()

        plant = Plant(
            name=self.state.config["selectedPlant"],
            icon=preset.icon,
            start_date=now,
            last_water_date=now,
            light=self.state.config["light"],
            watering=self.state.config["watering"],
            fertilizer=self.state.config["fertilizer"],
            days=preset.days,
            temp=preset.temp,
            unique_id=f"plant-{uuid4().hex}",
        )
        self.state.plants.append(plant)

        start_hour, end_hour = self._calculate_light_schedule()
        self.hardware.set_light_schedule(start_hour, end_hour)
        self.sync_hardware()

        if self.state.settings.get("auto_mode", True):
            self.hardware.start_auto_mode()

        self.save_state()

        message = (
            f"{self.state.config['selectedPlant']} добавлен!\n"
            f"💡 Свет: {self.state.config['light']}ч/день\n"
            f"💧 Полив: каждые {self.state.config['watering']} дней"
        )
        return PlantCreationResult(plant=plant, message=message)

    def remove_plant(self, index: int) -> str:
        plant_name = self.state.plants[index].name
        del self.state.plants[index]
        self.sync_hardware()
        self.save_state()
        return plant_name

    def shutdown(self) -> None:
        self.save_state()
        self.hardware.cleanup()
