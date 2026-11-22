LANGUAGE = "zh-cn"
# 根据实际接线修改对应板型的引脚。GPIO 编号使用 gpiochip 的 line offset。
DISPLAY_CONFIG = {'port': 0, 'cs': 0, 'dc': (0, 25), 'rst': None, 'backlight': (0, 7),  'spi_speed_hz': 40 * 1000 * 1000}

