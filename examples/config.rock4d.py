LANGUAGE = "zh-cn"
# 根据实际接线修改对应板型的引脚。GPIO 编号使用 gpiochip 的 line offset。
#dc GPIO2_D7
#backlight GPIO1_C0
DISPLAY_CONFIG = {'port': 1, 'cs': 0, 'dc': (2, 31), 'rst': None, 'backlight': (1, 16), 'spi_speed_hz': 40 * 1000 * 1000}