LANGUAGE = "zh-cn"
# 根据实际接线修改对应板型的引脚。GPIO 编号使用 gpiochip 的 line offset。
DISPLAY_CONFIG = {'port': 0, 'cs': 0, 'dc': (0, 23), 'rst': (0, 24), 'backlight': (0, 13),  'spi_speed_hz': 40 * 1000 * 1000}