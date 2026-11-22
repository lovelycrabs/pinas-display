LANGUAGE = "zh-cn"
# 根据实际接线修改对应板型的引脚。GPIO 编号使用 gpiochip 的 line offset。
#dc GPIO1_B2
#backlight GPIO4_C1
DISPLAY_CONFIG = {'port': 0, 'cs': 0, 'dc': (1, 10), 'rst': None, 'backlight': (4, 17), 'spi_speed_hz': 40 * 1000 * 1000}