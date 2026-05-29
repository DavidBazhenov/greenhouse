from __future__ import annotations

import re
import threading
import time
from abc import ABC, abstractmethod
from datetime import datetime
from typing import Dict

from infrastructure.config.runtime_config import RuntimeConfig


class BaseGardenHardware(ABC):
    def __init__(self, runtime_config: RuntimeConfig) -> None:
        self.runtime_config = runtime_config
        self.light_schedule: tuple[int, int] | None = None
        self._scheduler_thread: threading.Thread | None = None
        self._garden_plants: list[dict] = []
        self._stop_event = threading.Event()
        self._cleanup_done = False
        self._initialize_outputs()

    @abstractmethod
    def _initialize_outputs(self) -> None:
        pass

    @abstractmethod
    def _light_is_on(self) -> bool:
        pass

    @abstractmethod
    def _set_light_output(self, state: bool) -> None:
        pass

    @abstractmethod
    def _set_water_output(self, state: bool) -> None:
        pass

    @abstractmethod
    def _set_fertilizer_output(self, state: bool) -> None:
        pass

    @abstractmethod
    def _safe_turn_off_outputs(self) -> None:
        pass

    def set_light_schedule(self, start_hour: int, end_hour: int) -> None:
        self.light_schedule = (start_hour, end_hour)
        print(f"💡 Расписание света: {start_hour}:00 - {end_hour}:00")

    def _parse_days(self, days_str: str | None) -> int:
        if days_str is None:
            return 60
        match = re.search(r"(\d+)", str(days_str))
        return int(match.group(1)) if match else 60

    def set_light_manual(self, state: bool) -> None:
        self._set_light_output(state)
        print(f"💡 Свет {'ВКЛЮЧЕН' if state else 'ВЫКЛЮЧЕН'} (ручной режим)")

    def water_plant(self, plant_name: str, duration_seconds: int = 5) -> None:
        print(f"💧 ПОЛИВ: {plant_name} на {duration_seconds} сек")
        self._set_water_output(True)
        try:
            self._stop_event.wait(duration_seconds)
        finally:
            self._set_water_output(False)
        print(f"✅ Полив {plant_name} завершён")

    def fertilize(self, plant_name: str, fert_type, duration_seconds: int = 3) -> None:
        fert_value = getattr(fert_type, "value", str(fert_type))
        if fert_value == "Без":
            print(f"🌱 Подкормка не требуется для {plant_name}")
            return

        print(f"🌱 ПОДКОРМКА: {plant_name} ({fert_value}) на {duration_seconds} сек")
        self._set_fertilizer_output(True)
        try:
            self._stop_event.wait(duration_seconds)
        finally:
            self._set_fertilizer_output(False)
        print(f"✅ Подкормка {plant_name} завершена")

    def get_temperature(self) -> float:
        if self._garden_plants:
            temp_range = self._garden_plants[0].get("temp", "18-26")
            try:
                if "-" in str(temp_range):
                    low, high = map(int, str(temp_range).split("-"))
                    return round((low + high) / 2, 1)
                return float(temp_range)
            except Exception:
                return 22.0
        return 22.0

    def get_humidity(self) -> int:
        return 50

    def update_garden(self, garden_plants: list) -> None:
        self._garden_plants = []
        for idx, plant in enumerate(garden_plants):
            plant_copy = plant.copy()
            if not plant_copy.get("unique_id"):
                start_date = plant_copy.get("start_date", datetime.now())
                time_str = (
                    start_date.strftime("%H%M%S")
                    if isinstance(start_date, datetime)
                    else str(idx)
                )
                plant_copy["unique_id"] = f"{plant_copy['name']}_{time_str}_{idx}"
            if "last_water_date" not in plant_copy:
                plant_copy["last_water_date"] = plant_copy.get("start_date", datetime.now())
            self._garden_plants.append(plant_copy)

        print(f"🌱 Обновлён сад: {len(self._garden_plants)} растений")
        for plant in self._garden_plants:
            print(
                f"   - {plant['name']} (ID: {plant['unique_id'][-12:]}) | "
                f"Свет: {plant.get('light', '?')}ч | Полив: {plant.get('watering', '?')}дн"
            )

    def start_auto_mode(self) -> None:
        if self._scheduler_thread and self._scheduler_thread.is_alive():
            print("🤖 Автоматический режим уже запущен")
            return

        self._stop_event.clear()
        self._scheduler_thread = threading.Thread(
            target=self._scheduler_loop,
            daemon=True,
            name="greenbox-hardware-scheduler",
        )
        self._scheduler_thread.start()

    def _scheduler_loop(self) -> None:
        last_water: Dict[str, datetime] = {}
        last_status_print: Dict[str, datetime] = {}

        print("=" * 50)
        print("🤖 АВТОМАТИЧЕСКИЙ РЕЖИМ ЗАПУЩЕН")
        print("=" * 50)

        while not self._stop_event.is_set():
            now = datetime.now()

            if self.light_schedule:
                start_h, end_h = self.light_schedule
                should_be_on = start_h <= now.hour < end_h
                if should_be_on != self._light_is_on():
                    self._set_light_output(should_be_on)
                    state_label = "ВКЛЮЧИЛСЯ" if should_be_on else "ВЫКЛЮЧИЛСЯ"
                    print(f"💡 [{now.strftime('%H:%M:%S')}] Свет {state_label} по расписанию")

            for plant in self._garden_plants:
                plant_name = plant.get("name", "?")
                unique_id = plant.get("unique_id", plant_name)
                water_interval = plant.get("watering", 7)
                total_days = self._parse_days(plant.get("days", "60"))
                start_date = plant.get("start_date", now)
                light_hours = plant.get("light", 12)

                if isinstance(start_date, str):
                    try:
                        start_date = datetime.fromisoformat(start_date)
                    except ValueError:
                        start_date = now

                days_passed = (now - start_date).days
                progress = min(100, int((days_passed / total_days) * 100)) if total_days > 0 else 0

                last = last_water.get(unique_id)
                if last is None:
                    last = plant.get("last_water_date", start_date)
                    if isinstance(last, str):
                        try:
                            last = datetime.fromisoformat(last)
                        except ValueError:
                            last = start_date
                    last_water[unique_id] = last

                days_since_water = (now - last).days
                if days_since_water >= water_interval:
                    print(
                        f"💧 [{now.strftime('%H:%M:%S')}] ПОЛИВ: {plant_name} "
                        f"(прошло {days_since_water} дней, норма {water_interval} дней)"
                    )
                    self.water_plant(plant_name, duration_seconds=3)
                    last_water[unique_id] = now
                    plant["last_water_date"] = now
                    days_since_water = 0

                last_print = last_status_print.get(unique_id)
                if last_print is None or (now - last_print).seconds >= 30:
                    status_icon = "✅" if progress >= 100 else "🌿" if progress >= 75 else "🌱" if progress >= 50 else "🌰"
                    fert_name = getattr(plant.get("fertilizer", "NONE"), "value", plant.get("fertilizer", "NONE"))
                    days_until_water = max(0, water_interval - days_since_water)
                    print(f"\n📊 [{now.strftime('%H:%M:%S')}] {plant_name}")
                    print(f"   🌱 Прогресс: {progress}% | День {days_passed}/{total_days} {status_icon}")
                    print(f"   💧 Полив: через {days_until_water} дн (последний {days_since_water} дн назад)")
                    print(f"   🌱 Удобрение: {fert_name} | Свет: {light_hours}ч/день")
                    last_status_print[unique_id] = now

            self._stop_event.wait(self.runtime_config.scheduler_interval_seconds)

        print("\n🛑 АВТОМАТИЧЕСКИЙ РЕЖИМ ОСТАНОВЛЕН")
        print("=" * 50)

    def stop_auto_mode(self) -> None:
        self._stop_event.set()
        if self._scheduler_thread and self._scheduler_thread.is_alive():
            self._scheduler_thread.join(timeout=self.runtime_config.shutdown_timeout_seconds)
        print("🛑 Автоматический режим ОСТАНОВЛЕН")

    def cleanup(self) -> None:
        if self._cleanup_done:
            return
        self._cleanup_done = True
        self.stop_auto_mode()
        self._safe_turn_off_outputs()
        print("🧹 GPIO очищены")
