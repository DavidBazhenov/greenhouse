# Импортируем встроенную фабрику "заглушек" из gpiozero
from time import sleep
from gpiozero import LED
from gpiozero.pins.mock import MockFactory
# Указываем библиотеке использовать эту фабрику для всех пинов
from gpiozero import Device
Device.pin_factory = MockFactory()

# Теперь импортируем всё как обычно

print("=" * 50)
print("Эмуляция GPIO успешно запущена на Windows!")
print("Сейчас 'виртуальный' светодиод должен моргнуть 5 раз.")
print("=" * 50)

# Создаём светодиод на GPIO18.
# На Windows это будет виртуальный объект, на Raspberry Pi — реальный.
led = LED(18)

for i in range(5):
    led.on()
    print(f"Итерация {i+1}: LED ON (симуляция)")
    sleep(1)
    led.off()
    print(f"Итерация {i+1}: LED OFF (симуляция)")
    sleep(1)

print("\n✅ Готово! Эмуляция отработала без ошибок.")
