#!/usr/bin/env python3
import sys
import signal

import time
import st7789
import psutil
import os
from config import DISPLAY_CONFIG, TITLE


ROW_POSITIONS = [0, 24, 46, 68, 90, 112]
GRID_POSITIONS = [0, 40, 140, 172]
TITLE_FONT_COLOR = (255, 255, 255)
SUB_FONT_COLOR = (240, 240, 240)
COLOR_BLUE = (147, 208, 253)
COLOR_GREEN = (119, 255, 193)
COLOR_PURPLE = (236, 97, 254)
GRID_COLOR = (64, 64, 64)
SUB_FONT_SIZE = 16

shutdown_requested = False
display = None


hwmon_base_path = "/sys/class/hwmon"

def get_string(file):
    str = None
    with open(file, 'r') as f:
        str = f.read().strip()
    return str

def get_hwmon_path(dev_name):
    for dir in os.listdir(hwmon_base_path):
        full_path = os.path.join(hwmon_base_path, dir)
        dev_name_file = os.path.join(full_path, "name")
        if os.path.exists(dev_name_file):
            hw_name = get_string(dev_name_file)
            #print(hw_name)
            if hw_name == dev_name:
                return full_path

    return None

cpu_hwmon_path = get_hwmon_path("cpu_thermal")
if cpu_hwmon_path is None:
    cpu_hwmon_path = get_hwmon_path("soc-thermal")
if cpu_hwmon_path is None:
    cpu_hwmon_path = get_hwmon_path("cpu-thermal")
if cpu_hwmon_path is None:
    cpu_hwmon_path = get_hwmon_path("soc_thermal")
lm75_hwmon_path = get_hwmon_path("lm75")
if lm75_hwmon_path is None:
    lm75_hwmon_path = get_hwmon_path("lm75b")
ina226_hwmon_path = get_hwmon_path("ina226")

int_addresses = ''
power_info = {"pw":0, "vol":0}
temperature_info = {"cpu":0, "board":0}

def get_temp(file):
    temp = 0
    with open(file, 'r') as f:
        temp = int(f.read())
    return temp

def draw_text(disp, text, x, y, font_size, color=(255, 255, 255)):
    disp.text(text, x=x, y=y, font_size=font_size, color=color)


def draw_time(disp, x, y, w, h, font_size):
    now_time = time.localtime()
    current_time = time.strftime('%a,    %Y-%m-%d %H:%M:%S', now_time)
    draw_text(disp,current_time,x,y,w,h,font_size)

def draw_cpuinfo(disp):
    cpu_percent = psutil.cpu_percent()
    draw_percent(disp, cpu_percent/100.0, GRID_POSITIONS[1]+6, ROW_POSITIONS[1]+4, 120, 14)
    disp.fill_rect((0,0,0), GRID_POSITIONS[3]+1, ROW_POSITIONS[1]+1, disp.width-GRID_POSITIONS[3]-2, 20)
    draw_text(disp,format(cpu_percent, '.1f')+"%", x=GRID_POSITIONS[3]+6,y=ROW_POSITIONS[1]+3, font_size=SUB_FONT_SIZE, color= SUB_FONT_COLOR)

def draw_mem(disp):
    mem_info = psutil.virtual_memory()
    draw_percent(disp, mem_info.percent/100.0, GRID_POSITIONS[1]+6, ROW_POSITIONS[2]+4, 120, 14)
    disp.fill_rect((0,0,0), GRID_POSITIONS[3]+1, ROW_POSITIONS[2]+1, disp.width-GRID_POSITIONS[3]-2, 20)
    draw_text(disp,format(mem_info.percent, '.1f')+"%", x=GRID_POSITIONS[3]+6,y=ROW_POSITIONS[2]+3, font_size=SUB_FONT_SIZE, color= SUB_FONT_COLOR)


def draw_net(disp):
    interfaces = psutil.net_if_addrs()
    global int_addresses
    new_addresses = ''
    for name, addrs in interfaces.items():
        if name == "lo":
            continue
        new_addresses = "{0}:{1}".format(name, addrs[0].address)
        break
    if new_addresses != int_addresses:
        int_addresses = new_addresses
        disp.fill_rect((0,0,0), GRID_POSITIONS[1]+4, ROW_POSITIONS[5]+1, disp.width-GRID_POSITIONS[1]-4, 20)
        disp.text(int_addresses, GRID_POSITIONS[1]+4, ROW_POSITIONS[5]+3, font_size=SUB_FONT_SIZE, color=SUB_FONT_COLOR)


def draw_temp(disp):
    cpu_temp = get_temp(os.path.join(cpu_hwmon_path, "temp1_input"))
    if lm75_hwmon_path:
        temp_hwmon_file = os.path.join(lm75_hwmon_path, "temp1_input")
        if os.path.exists(temp_hwmon_file):
            temp_value = get_temp(temp_hwmon_file)
            board_temp = format(temp_value/1000,'.1f')
        else:
            board_temp = "err"
    else:
        board_temp = "err"
    cpu_temp_str = format(cpu_temp/1000,'.1f')
    if temperature_info["cpu"] != cpu_temp_str:
        temperature_info["cpu"] = cpu_temp_str
        disp.fill_rect((0,0,0), x=GRID_POSITIONS[1]+44, y=ROW_POSITIONS[3]+1, w=GRID_POSITIONS[2]-GRID_POSITIONS[1]-44, h=20)   
        draw_text(disp,cpu_temp_str, x=GRID_POSITIONS[1]+44,y=ROW_POSITIONS[3]+3, font_size=SUB_FONT_SIZE, color=COLOR_BLUE)
    if temperature_info["board"] != board_temp:
        temperature_info["board"] = board_temp
        disp.fill_rect((0,0,0), x=GRID_POSITIONS[2]+44, y=ROW_POSITIONS[3]+1, w=disp.width-GRID_POSITIONS[1]-44, h=20)
        draw_text(disp,board_temp, x=GRID_POSITIONS[2]+44,y=ROW_POSITIONS[3]+3, font_size=SUB_FONT_SIZE, color=COLOR_BLUE)


def draw_power(disp):
    pw_file = os.path.join(ina226_hwmon_path, 'power1_input')
    if os.path.exists(pw_file):
        pw_val = get_temp(pw_file)
        pw = format(pw_val/1000000, '.1f')
    else:
        pw = "err"
    vol_file = os.path.join(ina226_hwmon_path, 'in1_input')
    if os.path.exists(vol_file):
        vol_val = get_temp(vol_file)
        vol = format(vol_val/1000, '.1f')
    else:
        vol = "err"
    if power_info["vol"] != vol:
        power_info["vol"] = vol
        disp.fill_rect((0,0,0), x=GRID_POSITIONS[1]+44, y=ROW_POSITIONS[4]+1, w=GRID_POSITIONS[2]-GRID_POSITIONS[1]-44, h=20)
        draw_text(disp,vol+"v", x=GRID_POSITIONS[1]+44,y=ROW_POSITIONS[4]+3, font_size=SUB_FONT_SIZE, color=COLOR_PURPLE)
    if power_info["pw"] != pw:
        power_info["pw"] = pw
        disp.fill_rect((0,0,0), x=GRID_POSITIONS[2]+44, y=ROW_POSITIONS[4]+1, w=disp.width-GRID_POSITIONS[1]-44, h=20)
        draw_text(disp,pw+"w", x=GRID_POSITIONS[2]+44,y=ROW_POSITIONS[4]+3, font_size=SUB_FONT_SIZE, color=COLOR_PURPLE)

def draw_percent(disp, percent, x, y, w, h,):
    light_width = int(w*percent)
    disp.fill_rect((128,128,128), x+light_width, y, w-light_width, h)
    disp.fill_rect((0,255,0), x, y, light_width, h)

def draw_background(disp):
    disp.fill_rect((0,0,0),0,0)
    for i in range(1, len(ROW_POSITIONS)):
        disp.line(0, ROW_POSITIONS[i], disp.width-1, ROW_POSITIONS[i], color=GRID_COLOR)

    disp.line(GRID_POSITIONS[3], ROW_POSITIONS[1], GRID_POSITIONS[3], ROW_POSITIONS[3], color=GRID_COLOR)
    
    disp.line(GRID_POSITIONS[1], ROW_POSITIONS[1], GRID_POSITIONS[1], disp.height-1, color=GRID_COLOR)
    disp.line(0, ROW_POSITIONS[4], disp.width-1, ROW_POSITIONS[4], color=GRID_COLOR)

    disp.text(TITLE, 0, 0, font_size=20, color=TITLE_FONT_COLOR)

    disp.text("CPU", 0, ROW_POSITIONS[1]+3, font_size=SUB_FONT_SIZE, color=SUB_FONT_COLOR)
    disp.text("内存", 0, ROW_POSITIONS[2]+3, font_size=SUB_FONT_SIZE, color=SUB_FONT_COLOR)
    disp.text("温度", 0, ROW_POSITIONS[3]+3, font_size=SUB_FONT_SIZE, color=SUB_FONT_COLOR)
    disp.text("CPU", GRID_POSITIONS[1]+4, ROW_POSITIONS[3]+3, font_size=SUB_FONT_SIZE, color=SUB_FONT_COLOR)
    disp.text("背板", GRID_POSITIONS[2]+4, ROW_POSITIONS[3]+3, font_size=SUB_FONT_SIZE, color=SUB_FONT_COLOR)

    disp.text("电源", 0, ROW_POSITIONS[4]+3, font_size=SUB_FONT_SIZE, color=SUB_FONT_COLOR)
    disp.text("电压", GRID_POSITIONS[1]+4, ROW_POSITIONS[4]+3, font_size=SUB_FONT_SIZE, color=SUB_FONT_COLOR)
    disp.text("功率", GRID_POSITIONS[2]+4, ROW_POSITIONS[4]+3, font_size=SUB_FONT_SIZE, color=SUB_FONT_COLOR)

    disp.text("网络", 0, ROW_POSITIONS[5]+3, font_size=SUB_FONT_SIZE, color=SUB_FONT_COLOR)

def handle_shutdown(signum, frame):
    """仅记录退出请求，避免在信号处理器中执行阻塞的 SPI 操作。"""
    global shutdown_requested
    shutdown_requested = True


def cleanup_display():
    """在主线程中清屏并关闭背光。"""
    if display is not None:
        try:
            display.fill_rect((0, 0, 0), 0, 0)
            display.set_backlight(False)
        except Exception as exc:
            print(f"清理显示屏失败: {exc}", file=sys.stderr)

def main():
    global display
    display = st7789.ST7789(
        height=135,
        width=240,
        rotation=0,
        **DISPLAY_CONFIG,
        offset_left=40,
        offset_top=53,
    )

    display.begin()
    draw_background(display)
    while not shutdown_requested:
        draw_cpuinfo(display)
        draw_mem(display)
        draw_temp(display)
        draw_power(display)
        draw_net(display)
        time.sleep(1)

if __name__ == "__main__":
    signal.signal(signal.SIGTERM, handle_shutdown)
    signal.signal(signal.SIGINT, handle_shutdown)
    try:
        main()
    finally:
        cleanup_display()
        sys.exit(0)
