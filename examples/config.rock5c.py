LANGUAGE = "zh-cn"
# 根据实际接线修改对应板型的引脚。GPIO 编号使用 gpiochip 的 line offset。
#dc GPIO1_B5
#backlight GPIO1_A4
DISPLAY_CONFIG = {'port': 4, 'cs': 0, 'dc': (1, 13), 'rst': None, 'backlight': (1, 4), 'spi_speed_hz': 40 * 1000 * 1000}


