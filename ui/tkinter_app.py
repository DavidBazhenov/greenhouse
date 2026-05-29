from __future__ import annotations

import tkinter as tk
from tkinter import font
from pathlib import Path

import tkinter.messagebox as messagebox

from application.services.garden_service import GardenService
from domain.models import GardenState, FertilizerType, PLANT_PRESETS
from infrastructure.config.runtime_config import RuntimeConfig
from ui.view_helpers import configure_modal, enable_touch_scroll

# Цветовая схема (контрастная, для TFT экрана)
COLORS = {
    "primary": "#008000",
    "primary_light": "#00A000",
    "primary_dark": "#006000",
    "surface": "#FFFFFF",
    "bg": "#F0F0F0",
    "text": "#000000",
    "text_secondary": "#333333",
    "divider": "#CCCCCC",
    "inactive": "#999999",
    "white": "#FFFFFF",
    "error": "#FF0000",
    "wifi_connected": "#008000",
    "wifi_disconnected": "#666666"
}


class SmartGardenApp:
    def __init__(
        self,
        root,
        state: GardenState | None = None,
        runtime_config: RuntimeConfig | None = None,
        service: GardenService | None = None,
    ):
        self.root = root
        self.runtime_config = runtime_config or RuntimeConfig()
        if state is None and service is not None:
            state = service.state
        self.state = state or GardenState()
        if service is not None and service.state is not self.state:
            service.state = self.state
        self.config = self.state.config
        self.my_garden = self.state.plants
        self.app_settings = self.state.settings
        self.service = service
        self.assets_dir = Path(__file__).resolve().parent.parent / "assets" / "icons" / "openmoji"
        self.icon_cache: dict[str, tk.PhotoImage] = {}
        self.root.title("Умный сад")
        self.root.geometry(
            f"{self.runtime_config.window_width}x{self.runtime_config.window_height}"
        )
        self.root.configure(bg=COLORS["bg"])
        self.root.resizable(True, True)
        self.root.minsize(
            self.runtime_config.minimum_width,
            self.runtime_config.minimum_height,
        )
        self.root.attributes("-fullscreen", self.runtime_config.fullscreen)
        self.root.bind("<Escape>", self._exit_fullscreen)
        self.root.bind("<F11>", self._toggle_fullscreen)

        self.main_layout = tk.Frame(self.root, bg=COLORS["bg"])
        self.main_layout.pack(fill="both", expand=True)
        self.nav_host = tk.Frame(self.main_layout, bg=COLORS["bg"], height=38)
        self.nav_host.pack(side="bottom", fill="x")
        self.nav_host.pack_propagate(False)
        self.content_host = tk.Frame(self.main_layout, bg=COLORS["bg"])
        self.content_host.pack(side="top", fill="both", expand=True)

        # Шрифты (увеличены для большого окна)
        self.font_title = font.Font(family="Roboto", size=15, weight="bold")
        self.font_heading = font.Font(family="Roboto", size=11, weight="bold")
        self.font_subheading = font.Font(
            family="Roboto", size=10, weight="bold")
        self.font_body = font.Font(family="Roboto", size=9)
        self.font_button = font.Font(family="Roboto", size=9, weight="bold")
        self.font_nav = font.Font(family="Roboto", size=8, weight="bold")
        self.font_small = font.Font(family="Roboto", size=8)

        self.current_screen = None
        self.active_tab = "light"
        self.current_nav = "main"
        self.current_light = self.config["light"]
        self.current_watering = self.config["watering"]
        self.current_fertilizer_index = 0

        # Флаг для обновления навигации
        self.nav_bar = None
        self._closed = False

        self.show_main_screen()

    def clear_screen(self):
        if self.current_screen:
            self.current_screen.destroy()
        self.current_screen = tk.Frame(self.content_host, bg=COLORS["bg"])
        self.current_screen.pack(fill="both", expand=True)

    def _primary_button_options(self):
        return {
            "bg": COLORS["primary"],
            "fg": COLORS["text"],
            "activebackground": COLORS["primary_dark"],
            "activeforeground": COLORS["text"],
            "highlightbackground": COLORS["primary_dark"],
            "relief": "flat",
            "cursor": "hand2",
            "bd": 0,
        }

    def _surface_button_options(self, fg=None):
        button_fg = fg or COLORS["text"]
        return {
            "bg": COLORS["surface"],
            "fg": button_fg,
            "activebackground": COLORS["surface"],
            "activeforeground": button_fg,
            "highlightbackground": COLORS["divider"],
            "relief": "flat",
            "cursor": "hand2",
            "bd": 0,
        }

    def _load_icon(self, icon_name: str, size: int) -> tk.PhotoImage:
        cache_key = f"{icon_name}:{size}"
        if cache_key in self.icon_cache:
            return self.icon_cache[cache_key]

        image = tk.PhotoImage(file=str(self.assets_dir / f"{icon_name}.png"))
        base_size = max(image.width(), 1)
        if size < base_size:
            factor = max(1, round(base_size / size))
            if factor > 1:
                image = image.subsample(factor, factor)
        elif size > base_size:
            factor = max(1, round(size / base_size))
            if factor > 1:
                image = image.zoom(factor, factor)

        self.icon_cache[cache_key] = image
        return image

    def _plant_icon_name(self, plant_name: str) -> str:
        return {
            "Черри": "cherries",
            "Перец": "pepper",
            "Огурец": "cucumber",
            "Базилик": "herb",
            "Салат": "leafy_green",
            "Помидоры": "tomato",
        }.get(plant_name, "seedling")

    def _toggle_fullscreen(self, event=None):
        current = bool(self.root.attributes("-fullscreen"))
        self.root.attributes("-fullscreen", not current)

    def _exit_fullscreen(self, event=None):
        self.root.attributes("-fullscreen", False)

    # ========== НИЖНЯЯ ПАНЕЛЬ НАВИГАЦИИ ==========
    def show_nav_bar(self):
        # Удаляем старую панель если есть
        if self.nav_bar:
            self.nav_bar.destroy()

        self.nav_bar = tk.Frame(self.nav_host, bg=COLORS["primary"], height=38)
        self.nav_bar.pack(fill="both", expand=True)
        self.nav_bar.pack_propagate(False)

        # Кнопка Главная
        home_icon = self._load_icon("home", 18)
        home_btn = tk.Button(
            self.nav_bar,
            text="Главная",
            image=home_icon,
            compound="left",
            font=self.font_nav,
            command=self.show_main_screen,
            **self._primary_button_options(),
        )
        home_btn.image = home_icon
        home_btn.pack(side="left", expand=True, fill="both")

        # Кнопка Каталог
        catalog_icon = self._load_icon("books", 18)
        catalog_btn = tk.Button(
            self.nav_bar,
            text="Каталог",
            image=catalog_icon,
            compound="left",
            font=self.font_nav,
            command=self.show_catalog_screen,
            **self._primary_button_options(),
        )
        catalog_btn.image = catalog_icon
        catalog_btn.pack(side="left", expand=True, fill="both")

        # Кнопка Мой сад
        garden_icon = self._load_icon("seedling", 18)
        garden_btn = tk.Button(
            self.nav_bar,
            text="Мой сад",
            image=garden_icon,
            compound="left",
            font=self.font_nav,
            command=self.show_my_garden_screen,
            **self._primary_button_options(),
        )
        garden_btn.image = garden_icon
        garden_btn.pack(side="left", expand=True, fill="both")

    # ========== ЭКРАН 1: ГЛАВНАЯ ==========
    def show_main_screen(self):
        self.clear_screen()
        self.current_nav = "main"

        # Верхняя панель
        top_bar = tk.Frame(self.current_screen, bg=COLORS["bg"], height=28)
        top_bar.pack(fill="x", padx=8, pady=(4, 0))
        top_bar.pack_propagate(False)

        # WiFi слева
        wifi_frame = tk.Frame(top_bar, bg=COLORS["bg"])
        wifi_frame.pack(side="left")

        wifi_icon = self._load_icon("wifi", 16)
        wifi_label = tk.Label(wifi_frame, image=wifi_icon, bg=COLORS["bg"])
        wifi_label.image = wifi_icon
        wifi_label.pack(side="left")

        wifi_btn = tk.Button(wifi_frame, text="WiFi", font=self.font_small,
                             bg=COLORS["surface"], fg=COLORS["primary"],
                             relief="flat", cursor="hand2",
                             command=self.show_wifi_settings, bd=1, padx=5, pady=1)
        wifi_btn.pack(side="left", padx=(3, 0))

        # Настройки справа
        settings_frame = tk.Frame(top_bar, bg=COLORS["bg"])
        settings_frame.pack(side="right")

        settings_icon = self._load_icon("settings", 16)
        settings_label = tk.Label(settings_frame, image=settings_icon, bg=COLORS["bg"], cursor="hand2")
        settings_label.image = settings_icon
        settings_label.pack(side="left")
        settings_label.bind("<Button-1>", lambda e: self.show_app_settings())

        # Скроллируемый контент
        canvas = tk.Canvas(self.current_screen, bg=COLORS["bg"], highlightthickness=0)
        scrollbar = tk.Scrollbar(
            self.current_screen, orient="vertical", command=canvas.yview)
        scrollable = tk.Frame(canvas, bg=COLORS["bg"])

        scrollable.bind("<Configure>", lambda e: canvas.configure(
            scrollregion=canvas.bbox("all")))
        window_id = canvas.create_window((0, 0), window=scrollable, anchor="nw")
        canvas.bind(
            "<Configure>",
            lambda e: canvas.itemconfigure(window_id, width=e.width),
        )
        canvas.configure(yscrollcommand=scrollbar.set)

        canvas.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")

        main_panel = tk.Frame(scrollable, bg=COLORS["bg"])
        main_panel.pack(fill="both", expand=True)
        main_panel.grid_rowconfigure(0, weight=1)
        main_panel.grid_rowconfigure(2, weight=1)
        main_panel.grid_columnconfigure(0, weight=1)

        center_frame = tk.Frame(main_panel, bg=COLORS["bg"])
        center_frame.grid(row=1, column=0, sticky="n")

        # Заголовок
        title = tk.Label(center_frame, text="УМНЫЙ САД", font=self.font_title,
                         bg=COLORS["bg"], fg=COLORS["primary"])
        title.pack(pady=(0, 6))

        subtitle = tk.Label(center_frame, text="ваш помощник в выращивании растений",
                            font=self.font_body, bg=COLORS["bg"], fg=COLORS["text_secondary"])
        subtitle.pack(pady=(0, 8))

        # Статистика
        stats_frame = tk.Frame(
            center_frame, bg=COLORS["surface"], relief="flat", bd=2)
        stats_frame.pack(fill="x", pady=6)
        stats_frame.configure(
            highlightbackground=COLORS["divider"], highlightthickness=1)

        stats_title_icon = self._load_icon("chart", 14)
        stats_title = tk.Label(stats_frame, text=" СТАТИСТИКА", image=stats_title_icon, compound="left",
                               font=self.font_heading, bg=COLORS["surface"], fg=COLORS["primary"])
        stats_title.image = stats_title_icon
        stats_title.pack(anchor="w", padx=10, pady=(5, 2))

        garden_count_icon = self._load_icon("seedling", 12)
        garden_count = tk.Label(stats_frame, text=f" Растений в саду: {len(self.my_garden)}",
                                image=garden_count_icon, compound="left", font=self.font_body,
                                bg=COLORS["surface"], fg=COLORS["text"])
        garden_count.image = garden_count_icon
        garden_count.pack(anchor="w", padx=10, pady=1)

        available_icon = self._load_icon("books", 12)
        available_count = tk.Label(stats_frame, text=f" Доступно растений: {len(PLANT_PRESETS)}",
                                   image=available_icon, compound="left", font=self.font_body,
                                   bg=COLORS["surface"], fg=COLORS["text"])
        available_count.image = available_icon
        available_count.pack(anchor="w", padx=10, pady=(1, 5))

        enable_touch_scroll(canvas, scrollable)
        self.show_nav_bar()

    # ========== ЭКРАН 2: КАТАЛОГ ==========
    def show_catalog_screen(self):
        self.clear_screen()
        self.current_nav = "catalog"

        header = tk.Frame(self.current_screen, bg=COLORS["primary"], height=34)
        header.pack(fill="x")
        header.pack_propagate(False)

        # Кнопка назад в header
        back_icon = self._load_icon("back", 16)
        back_btn = tk.Button(
            header,
            image=back_icon,
            command=self.show_main_screen,
            **self._primary_button_options(),
        )
        back_btn.image = back_icon
        back_btn.pack(side="left", padx=8)

        tk.Label(header, text="КАТАЛОГ РАСТЕНИЙ", font=self.font_body,
                 bg=COLORS["primary"], fg="white").pack(pady=6)

        # Скроллинг
        canvas = tk.Canvas(self.current_screen,
                           bg=COLORS["bg"], highlightthickness=0)
        scrollbar = tk.Scrollbar(
            self.current_screen, orient="vertical", command=canvas.yview)
        scrollable = tk.Frame(canvas, bg=COLORS["bg"])

        scrollable.bind("<Configure>", lambda e: canvas.configure(
            scrollregion=canvas.bbox("all")))
        canvas.create_window(
            (0, 0),
            window=scrollable,
            anchor="nw",
            width=self.runtime_config.catalog_canvas_width,
        )
        canvas.configure(yscrollcommand=scrollbar.set)

        canvas.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")

        # Карточки растений (все 6)
        for plant_name in PLANT_PRESETS.keys():
            preset = PLANT_PRESETS[plant_name]
            card = tk.Frame(
                scrollable, bg=COLORS["surface"], relief="flat", bd=2)
            card.pack(fill="x", padx=10, pady=5)
            card.configure(
                highlightbackground=COLORS["divider"], highlightthickness=1)

            # Заголовок карточки
            title_frame = tk.Frame(card, bg=COLORS["surface"])
            title_frame.pack(fill="x", padx=10, pady=(5, 2))

            plant_icon = self._load_icon(self._plant_icon_name(plant_name), 20)
            tk.Label(title_frame, image=plant_icon, bg=COLORS["surface"]).pack(side="left", padx=(0, 8))
            self.icon_cache[f"{plant_name}:catalog:20"] = plant_icon

            tk.Label(title_frame, text=plant_name, font=self.font_heading,
                     bg=COLORS["surface"], fg=COLORS["text"]).pack(side="left")

            # Параметры
            params_frame = tk.Frame(card, bg=COLORS["surface"])
            params_frame.pack(fill="x", padx=10, pady=(0, 5))

            days_icon = self._load_icon("chart", 10)
            light_icon = self._load_icon("lightbulb", 10)
            water_icon = self._load_icon("drop", 10)

            days_label = tk.Label(params_frame, text=f" {preset.days} дн", image=days_icon, compound="left",
                                  font=self.font_small, bg=COLORS["surface"], fg=COLORS["text_secondary"])
            days_label.image = days_icon
            days_label.pack(side="left", padx=(0, 8))

            light_label = tk.Label(params_frame, text=f" {preset.light}ч", image=light_icon, compound="left",
                                   font=self.font_small, bg=COLORS["surface"], fg=COLORS["text_secondary"])
            light_label.image = light_icon
            light_label.pack(side="left", padx=(0, 8))

            water_label = tk.Label(params_frame, text=f" {preset.water}дн", image=water_icon, compound="left",
                                   font=self.font_body, bg=COLORS["surface"], fg=COLORS["text_secondary"])
            water_label.image = water_icon
            water_label.pack(side="left")

            # Описание
            tk.Label(card, text=preset.description, font=self.font_small,
                     bg=COLORS["surface"], fg=COLORS["text_secondary"]).pack(anchor="w", padx=10, pady=(0, 4))

            # Кнопка Выбрать
            select_btn = tk.Button(card, text="ВЫБРАТЬ", font=self.font_button,
                                   command=lambda p=plant_name: self.select_plant(p),
                                   pady=4, **self._primary_button_options())
            select_btn.pack(fill="x", padx=10, pady=(0, 5))

        enable_touch_scroll(canvas, scrollable)
        self.show_nav_bar()

    def select_plant(self, plant_name):
        preset = PLANT_PRESETS[plant_name]
        self.config["selectedPlant"] = plant_name
        self.config["light"] = preset.light
        self.config["watering"] = preset.water
        self.config["fertilizer"] = preset.fertilizer
        self._persist_state()
        self.show_settings_screen()

    # ========== ЭКРАН 3: НАСТРОЙКИ ПАРАМЕТРОВ ==========
    def show_settings_screen(self):
        self.clear_screen()

        header = tk.Frame(self.current_screen, bg=COLORS["primary"], height=34)
        header.pack(fill="x")
        header.pack_propagate(False)

        # Кнопка назад
        back_icon = self._load_icon("back", 16)
        back_btn = tk.Button(
            header,
            image=back_icon,
            command=self.show_catalog_screen,
            **self._primary_button_options(),
        )
        back_btn.image = back_icon
        back_btn.pack(side="left", padx=8)

        plant_icon = self._load_icon(self._plant_icon_name(self.config["selectedPlant"]), 16)
        tk.Label(header, image=plant_icon,
                 text=f" {self.config['selectedPlant']} - НАСТРОЙКИ",
                 compound="left",
                 font=self.font_body, bg=COLORS["primary"], fg="white").pack(pady=6)

        content = tk.Frame(self.current_screen, bg=COLORS["bg"])
        content.pack(fill="both", expand=True, padx=10, pady=8)

        # Таб-селектор
        tab_frame = tk.Frame(content, bg=COLORS["bg"])
        tab_frame.pack(fill="x", pady=(0, 8))

        light_icon = self._load_icon("lightbulb", 12)
        self.light_tab = tk.Button(tab_frame, text=" Свет", image=light_icon, compound="left", font=self.font_body,
                                   bg=COLORS["surface"] if self.active_tab == "light" else COLORS["bg"],
                                   fg=COLORS["primary"] if self.active_tab == "light" else COLORS["text_secondary"],
                                   relief="flat", command=lambda: self.switch_tab("light"), padx=8, pady=4)
        self.light_tab.image = light_icon
        self.light_tab.pack(side="left", expand=True, padx=2)

        water_icon = self._load_icon("drop", 12)
        self.water_tab = tk.Button(tab_frame, text=" Полив", image=water_icon, compound="left", font=self.font_body,
                                   bg=COLORS["surface"] if self.active_tab == "watering" else COLORS["bg"],
                                   fg=COLORS["primary"] if self.active_tab == "watering" else COLORS["text_secondary"],
                                   relief="flat", command=lambda: self.switch_tab("watering"), padx=8, pady=4)
        self.water_tab.image = water_icon
        self.water_tab.pack(side="left", expand=True, padx=2)

        fert_icon = self._load_icon("seedling", 12)
        self.fert_tab = tk.Button(tab_frame, text=" Подкормка", image=fert_icon, compound="left", font=self.font_body,
                                  bg=COLORS["surface"] if self.active_tab == "fertilizer" else COLORS["bg"],
                                  fg=COLORS["primary"] if self.active_tab == "fertilizer" else COLORS["text_secondary"],
                                  relief="flat", command=lambda: self.switch_tab("fertilizer"), padx=8, pady=4)
        self.fert_tab.image = fert_icon
        self.fert_tab.pack(side="left", expand=True, padx=2)

        # Регулятор
        self.regulator_frame = tk.Frame(content, bg=COLORS["bg"])
        self.regulator_frame.pack(pady=10)
        self.update_regulator()

        # Кнопки
        btn_frame = tk.Frame(content, bg=COLORS["bg"])
        btn_frame.pack(fill="x", pady=8)

        tk.Button(btn_frame, text="СОХРАНИТЬ И ДОБАВИТЬ В САД", font=self.font_button,
                  command=self.save_and_start, pady=4, **self._primary_button_options()).pack(fill="x", pady=4)

        self.show_nav_bar()

    def switch_tab(self, tab_name):
        # СОХРАНЯЕМ текущее значение перед переключением
        if self.active_tab == "light" and hasattr(self, 'current_value'):
            self.config["light"] = self.current_value
        elif self.active_tab == "watering" and hasattr(self, 'current_value'):
            self.config["watering"] = self.current_value
        elif self.active_tab == "fertilizer" and hasattr(self, 'current_fert_index'):
            self.config["fertilizer"] = self.fertilizer_values[self.current_fert_index]

        # Переключаем вкладку
        self.active_tab = tab_name

        # Обновляем внешний вид кнопок вкладок
        self.light_tab.config(bg=COLORS["surface"] if tab_name == "light" else COLORS["bg"],
                              fg=COLORS["primary"] if tab_name == "light" else COLORS["text_secondary"])
        self.water_tab.config(bg=COLORS["surface"] if tab_name == "watering" else COLORS["bg"],
                              fg=COLORS["primary"] if tab_name == "watering" else COLORS["text_secondary"])
        self.fert_tab.config(bg=COLORS["surface"] if tab_name == "fertilizer" else COLORS["bg"],
                             fg=COLORS["primary"] if tab_name == "fertilizer" else COLORS["text_secondary"])

        # Обновляем регулятор для новой вкладки
        self.update_regulator()

    def update_regulator(self):
        # Очищаем старые виджеты
        for widget in self.regulator_frame.winfo_children():
            widget.destroy()

        # Загружаем значения из config для текущей вкладки
        if self.active_tab == "light":
            self.current_light = self.config["light"]
            self.min_val = 12
            self.max_val = 24
            self.unit = "ч/день"
            display_value = self.current_light
        elif self.active_tab == "watering":
            self.current_watering = self.config["watering"]
            self.min_val = 1
            self.max_val = 14
            self.unit = "дней"
            display_value = self.current_watering
        else:  # fertilizer
            self.fertilizer_values = list(FertilizerType)
            self.current_fertilizer_index = self.fertilizer_values.index(
                self.config["fertilizer"])
            display_value = self.fertilizer_values[self.current_fertilizer_index].value

        # Кнопка "-"
        btn_minus = tk.Button(self.regulator_frame, text="-", font=self.font_heading,
                              command=self.decrement, width=3, height=1,
                              **self._surface_button_options())
        btn_minus.pack(side="left", padx=12)

        # Отображение значения
        if self.active_tab != "fertilizer":
            display_text = f"{display_value} {self.unit}"
        else:
            display_text = display_value

        self.value_display = tk.Label(self.regulator_frame, text=display_text,
                                      font=self.font_heading, bg=COLORS["bg"],
                                      fg=COLORS["primary"])
        self.value_display.pack(side="left", padx=14)

        # Кнопка "+"
        btn_plus = tk.Button(self.regulator_frame, text="+", font=self.font_heading,
                             command=self.increment, width=3, height=1,
                             **self._surface_button_options())
        btn_plus.pack(side="left", padx=12)

    def decrement(self):
        if self.active_tab == "light":
            if hasattr(self, 'current_light') and self.current_light > self.min_val:
                self.current_light -= 1
                self.value_display.config(
                    text=f"{self.current_light} {self.unit}")
                self.config["light"] = self.current_light
                self._persist_state()
                if self.service is not None:
                    self.service.apply_runtime_state()
        elif self.active_tab == "watering":
            if hasattr(self, 'current_watering') and self.current_watering > self.min_val:
                self.current_watering -= 1
                self.value_display.config(
                    text=f"{self.current_watering} {self.unit}")
                self.config["watering"] = self.current_watering
                self._persist_state()
        elif self.active_tab == "fertilizer":
            if hasattr(self, 'current_fertilizer_index') and self.current_fertilizer_index > 0:
                self.current_fertilizer_index -= 1
                fert_value = self.fertilizer_values[self.current_fertilizer_index].value
                self.value_display.config(text=fert_value)
                self.config["fertilizer"] = self.fertilizer_values[self.current_fertilizer_index]
                self._persist_state()

    def increment(self):
        if self.active_tab == "light":
            if hasattr(self, 'current_light') and self.current_light < self.max_val:
                self.current_light += 1
                self.value_display.config(
                    text=f"{self.current_light} {self.unit}")
                self.config["light"] = self.current_light
                self._persist_state()
                if self.service is not None:
                    self.service.apply_runtime_state()
        elif self.active_tab == "watering":
            if hasattr(self, 'current_watering') and self.current_watering < self.max_val:
                self.current_watering += 1
                self.value_display.config(
                    text=f"{self.current_watering} {self.unit}")
                self.config["watering"] = self.current_watering
                self._persist_state()
        elif self.active_tab == "fertilizer":
            if hasattr(self, 'current_fertilizer_index') and self.current_fertilizer_index < len(self.fertilizer_values) - 1:
                self.current_fertilizer_index += 1
                fert_value = self.fertilizer_values[self.current_fertilizer_index].value
                self.value_display.config(text=fert_value)
                self.config["fertilizer"] = self.fertilizer_values[self.current_fertilizer_index]
                self._persist_state()

    def save_and_start(self):
        # Сохраняем значения из текущих переменных в config
        if hasattr(self, 'current_light'):
            self.config["light"] = self.current_light
        if hasattr(self, 'current_watering'):
            self.config["watering"] = self.current_watering
        if hasattr(self, 'current_fertilizer_index') and hasattr(self, 'fertilizer_values'):
            self.config["fertilizer"] = self.fertilizer_values[self.current_fertilizer_index]
        if self.service is None:
            raise RuntimeError("GardenService is not configured")

        self.service.apply_runtime_state()
        result = self.service.add_selected_plant()
        messagebox.showinfo("Успех", result.message)
        self.show_my_garden_screen()

    # ========== ЭКРАН 4: МОЙ САД ==========
    def show_my_garden_screen(self):
        if self.service is not None:
            self.service.sync_hardware()
        self.clear_screen()
        self.current_nav = "mygarden"

        header = tk.Frame(self.current_screen, bg=COLORS["primary"], height=34)
        header.pack(fill="x")
        header.pack_propagate(False)

        # Кнопка назад
        back_icon = self._load_icon("back", 16)
        back_btn = tk.Button(
            header,
            image=back_icon,
            command=self.show_main_screen,
            **self._primary_button_options(),
        )
        back_btn.image = back_icon
        back_btn.pack(side="left", padx=8)

        tk.Label(header, text="МОЙ САД", font=self.font_heading,
                 bg=COLORS["primary"], fg="white").pack(pady=6)

        canvas = tk.Canvas(self.current_screen, bg=COLORS["bg"], highlightthickness=0)
        scrollbar = tk.Scrollbar(
            self.current_screen, orient="vertical", command=canvas.yview)
        scrollable = tk.Frame(canvas, bg=COLORS["bg"])

        scrollable.bind("<Configure>", lambda e: canvas.configure(
            scrollregion=canvas.bbox("all")))
        window_id = canvas.create_window((0, 0), window=scrollable, anchor="nw")
        canvas.bind(
            "<Configure>",
            lambda e: canvas.itemconfigure(window_id, width=e.width),
        )
        canvas.configure(yscrollcommand=scrollbar.set)

        canvas.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")

        content = tk.Frame(scrollable, bg=COLORS["bg"])
        content.pack(fill="x", padx=10, pady=6)

        if len(self.my_garden) == 0:
            # Пустой сад
            empty_frame = tk.Frame(content, bg=COLORS["bg"])
            empty_frame.pack(fill="x", pady=(12, 0))

            empty_icon = self._load_icon("seedling", 28)
            tk.Label(empty_frame, image=empty_icon, bg=COLORS["bg"]).pack()
            empty_frame.empty_icon = empty_icon
            tk.Label(empty_frame, text="Ваш сад пуст", font=self.font_heading,
                     bg=COLORS["bg"], fg=COLORS["text"]).pack(pady=4)
            tk.Label(empty_frame, text="Добавьте растения из каталога", font=self.font_body,
                     bg=COLORS["bg"], fg=COLORS["text_secondary"]).pack()

            add_btn = tk.Button(empty_frame, text="ПЕРЕЙТИ В КАТАЛОГ", font=self.font_button,
                                command=self.show_catalog_screen, padx=10, pady=4,
                                **self._primary_button_options())
            add_btn.pack(pady=8)
        else:
            # Отображаем активные растения
            for i, plant in enumerate(self.my_garden):
                card = tk.Frame(
                    scrollable, bg=COLORS["surface"], relief="flat", bd=2)
                card.pack(fill="x", pady=6)
                card.configure(
                    highlightbackground=COLORS["divider"], highlightthickness=1)

                # Иконка и название
                top_frame = tk.Frame(card, bg=COLORS["surface"])
                top_frame.pack(fill="x", padx=10, pady=(4, 2))

                icon_name = self._plant_icon_name(plant["name"])
                plant_icon = self._load_icon(icon_name, 18)
                plant_icon_label = tk.Label(top_frame, image=plant_icon, bg=COLORS["surface"])
                plant_icon_label.image = plant_icon
                plant_icon_label.pack(side="left", padx=(0, 6))

                tk.Label(top_frame, text=plant["name"], font=self.font_heading,
                         bg=COLORS["surface"], fg=COLORS["text"]).pack(side="left")

                # Статус
                status = tk.Label(top_frame, text="● РАСТЕТ", font=self.font_small,
                                  bg=COLORS["surface"], fg=COLORS["primary"])
                status.pack(side="right")

                # Параметры
                params_frame = tk.Frame(card, bg=COLORS["surface"])
                params_frame.pack(fill="x", padx=10, pady=(0, 4))

                start_date_str = plant["start_date"].strftime("%d.%m.%Y %H:%M")
                start_icon = self._load_icon("calendar", 10)
                start_label = tk.Label(params_frame, text=f" Старт: {start_date_str}", image=start_icon, compound="left",
                                       font=self.font_small, bg=COLORS["surface"], fg=COLORS["text_secondary"])
                start_label.image = start_icon
                start_label.pack(anchor="w")

                metrics_frame = tk.Frame(params_frame, bg=COLORS["surface"])
                metrics_frame.pack(anchor="w", pady=1)

                light_icon = self._load_icon("lightbulb", 10)
                water_icon = self._load_icon("drop", 10)
                temp_icon = self._load_icon("thermometer", 10)

                light_label = tk.Label(metrics_frame, text=f" {plant['light']}ч",
                                       image=light_icon, compound="left",
                                       font=self.font_small, bg=COLORS["surface"], fg=COLORS["text_secondary"])
                light_label.image = light_icon
                light_label.pack(side="left", padx=(0, 8))

                water_label = tk.Label(metrics_frame, text=f" {plant['watering']}дн",
                                       image=water_icon, compound="left",
                                       font=self.font_small, bg=COLORS["surface"], fg=COLORS["text_secondary"])
                water_label.image = water_icon
                water_label.pack(side="left", padx=(0, 8))

                temp_label = tk.Label(metrics_frame, text=f" {plant['temp']}°C",
                                      image=temp_icon, compound="left",
                                      font=self.font_small, bg=COLORS["surface"], fg=COLORS["text_secondary"])
                temp_label.image = temp_icon
                temp_label.pack(side="left")

                # Кнопка удаления
                trash_icon = self._load_icon("trash", 12)
                remove_btn = tk.Label(
                    card,
                    text=" УДАЛИТЬ",
                    font=self.font_small,
                    image=trash_icon,
                    compound="left",
                    bg=COLORS["error"],
                    fg=COLORS["white"],
                    cursor="hand2",
                    padx=8,
                    pady=4,
                )
                remove_btn.image = trash_icon
                remove_btn.pack(fill="x", padx=10, pady=(0, 6))
                remove_btn.bind("<Button-1>", lambda e, idx=i: self.remove_from_garden(idx))
                remove_btn.bind("<Enter>", lambda e, w=remove_btn: w.configure(bg="#CC0000"))
                remove_btn.bind("<Leave>", lambda e, w=remove_btn: w.configure(bg=COLORS["error"]))

        if len(self.my_garden) == 0:
            enable_touch_scroll(canvas, scrollable)
        else:
            enable_touch_scroll(canvas, scrollable)

        self.show_nav_bar()

    def remove_from_garden(self, index):
        if self.service is None:
            raise RuntimeError("GardenService is not configured")

        plant_name = self.service.remove_plant(index)
        messagebox.showinfo("Удалено", f"{plant_name} удален из вашего сада")
        self.show_my_garden_screen()

    # ========== НАСТРОЙКИ ==========
    def show_app_settings(self):
        settings_window = tk.Toplevel(self.root)
        settings_window.configure(bg=COLORS["bg"])
        content = configure_modal(
            settings_window,
            self.root,
            self.runtime_config.settings_window_width,
            self.runtime_config.settings_window_height,
            "Настройки",
        )
        content.configure(bg=COLORS["bg"])

        tk.Label(content, text="НАСТРОЙКИ ПРИЛОЖЕНИЯ", font=self.font_heading,
                 bg=COLORS["bg"], fg=COLORS["primary"]).pack(pady=(0, 8))

        notifications_var = tk.BooleanVar(
            value=self.app_settings["notifications"])
        bell_icon = self._load_icon("bell", 12)
        notifications_btn = tk.Checkbutton(
            content,
            text=" Включить уведомления",
            variable=notifications_var,
            font=self.font_body,
            bg=COLORS["bg"],
            fg=COLORS["text"],
            image=bell_icon,
            compound="left",
        )
        notifications_btn.image = bell_icon
        notifications_btn.pack(anchor="w", pady=4)

        auto_var = tk.BooleanVar(value=self.app_settings["auto_mode"])
        robot_icon = self._load_icon("robot", 12)
        auto_btn = tk.Checkbutton(
            content,
            text=" Автоматический режим",
            variable=auto_var,
            font=self.font_body,
            bg=COLORS["bg"],
            fg=COLORS["text"],
            image=robot_icon,
            compound="left",
        )
        auto_btn.image = robot_icon
        auto_btn.pack(anchor="w", pady=4)

        def save_settings():
            self.app_settings["notifications"] = notifications_var.get()
            self.app_settings["auto_mode"] = auto_var.get()
            self._persist_state()
            if self.service is not None:
                self.service.apply_runtime_state()
            messagebox.showinfo("Успех", "Настройки сохранены!")
            settings_window.destroy()

        tk.Button(content, text="СОХРАНИТЬ", font=self.font_button,
                  command=save_settings, pady=4, **self._primary_button_options()).pack(fill="x", pady=8)

    def show_wifi_settings(self):
        wifi_window = tk.Toplevel(self.root)
        wifi_window.configure(bg=COLORS["bg"])
        content = configure_modal(
            wifi_window,
            self.root,
            self.runtime_config.wifi_window_width,
            self.runtime_config.wifi_window_height,
            "Подключение WiFi",
        )
        content.configure(bg=COLORS["bg"])

        tk.Label(content, text="ПОДКЛЮЧЕНИЕ К WiFi", font=self.font_heading,
                 bg=COLORS["bg"], fg=COLORS["primary"]).pack(pady=(0, 8))

        # Список сетей
        networks = ["Home_WiFi", "Guest_Net", "Office_2.4G", "Public_WiFi"]
        for net in networks:
            net_frame = tk.Frame(
                content, bg=COLORS["surface"], relief="flat", bd=1)
            net_frame.pack(fill="x", pady=3)
            net_frame.configure(
                highlightbackground=COLORS["divider"], highlightthickness=1)

            network_icon = self._load_icon("antenna", 12)
            net_label = tk.Label(
                net_frame,
                text=f" {net}",
                image=network_icon,
                compound="left",
                font=self.font_body,
                bg=COLORS["surface"],
                fg=COLORS["text"],
            )
            net_label.image = network_icon
            net_label.pack(side="left", padx=10, pady=4)

            tk.Button(net_frame, text="Подключить", font=self.font_small,
                      command=lambda n=net: self.connect_to_wifi(
                          n, wifi_window),
                      padx=8, pady=3, **self._primary_button_options()).pack(side="right", padx=8)

        tk.Label(content, text="Или подключиться вручную:", font=self.font_small,
                 bg=COLORS["bg"], fg=COLORS["text"]).pack(anchor="w", pady=(8, 4))

        # Ручное подключение
        manual_frame = tk.Frame(content, bg=COLORS["bg"])
        manual_frame.pack(fill="x", pady=3)

        ssid_entry = tk.Entry(manual_frame, font=self.font_small, bd=1,
                              relief="solid", highlightbackground=COLORS["divider"])
        ssid_entry.pack(fill="x", pady=2)
        ssid_entry.insert(0, "Введите SSID")

        def clear_ssid(event):
            if ssid_entry.get() == "Введите SSID":
                ssid_entry.delete(0, tk.END)

        ssid_entry.bind("<FocusIn>", clear_ssid)

        def manual_connect():
            ssid = ssid_entry.get()
            if ssid and ssid != "Введите SSID":
                self.connect_to_wifi(ssid, wifi_window)
            else:
                messagebox.showwarning("Ошибка", "Введите название сети")

        tk.Button(content, text="РУЧНОЕ ПОДКЛЮЧЕНИЕ", font=self.font_button,
                  command=manual_connect, pady=4, **self._primary_button_options()).pack(fill="x", pady=8)

    def connect_to_wifi(self, network_name, window, password=None):
        self.config["wifi_connected"] = True
        self._persist_state()
        messagebox.showinfo("WiFi", f"Подключено к {network_name}!")
        window.destroy()
        # Обновляем главный экран чтобы показать статус WiFi
        self.show_main_screen()

    def _persist_state(self):
        if self.service is not None:
            self.service.save_state()

    def on_closing(self):
        if self._closed:
            return
        self._closed = True
        if self.service is not None:
            self.service.shutdown()
        self.root.destroy()


if __name__ == "__main__":
    from runtime.bootstrap import main

    main()
