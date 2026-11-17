# PiNAS Display

PiNAS Display 是一个运行在 Linux 单板机上的 SPI 屏幕信息显示程序，用于显示时间、CPU、内存、温度、网络地址和电源信息。

## 支持的板卡

当前提供 `rpi5`、`rock5c`、`rock4d`、`rock2a`、`rpi5-nas` 配置，文件位于 `examples/config.<board>.py`。

## 安装

```bash
cd pinas-display
sudo bash ./install.sh -b rpi5
```

老的6盘位、4盘位RPi5-NAS  板子使用：

```bash
sudo bash ./install.sh -b rpi5-nas
```

也可以使用 `sudo bash ./install.sh --board rock5c`。不指定板卡时默认使用 `rpi5`。脚本会选择对应配置并复制为根目录的 `config.py`，创建虚拟环境、安装依赖，将程序复制到 `/usr/local/pinas-display`，然后注册并启动 `spiled.service`。

查看状态和日志：

```bash
sudo systemctl status spiled.service
sudo journalctl -u spiled.service -f
```

## 手动运行

```bash
sudo /usr/local/pinas-display/venv/bin/python /usr/local/pinas-display/main.py
```

## 配置屏幕

修改 `config.py` 中的标题和 SPI/GPIO 参数：

```python
TITLE = "欢迎使用PiNAS!"
DISPLAY_CONFIG = {"port": 0, "cs": 0, "dc": 25, "rst": None, "backlight": None}
```

GPIO 编号使用 Linux `gpiochip` 的 line offset，不一定等于开发板丝印上的物理引脚编号。修改后执行 `sudo systemctl restart spiled.service`。

## 卸载

```bash
sudo systemctl disable --now spiled.service
sudo rm -rf /usr/local/pinas-display
sudo rm -f /etc/systemd/system/spiled.service
sudo systemctl daemon-reload
```

## 项目结构

```text
├── main.py                 # 主程序
├── config.py               # 当前配置
├── examples/               # 板卡配置示例
├── st7789/                 # ST7789 驱动和字体
├── requirements.txt        # Python 依赖
├── spiled.service          # systemd 服务
└── install.sh              # 安装脚本
```

## 注意事项

- 安装脚本需要 root 权限，设备必须启用 SPI。
- 请确认屏幕供电、电平和接线符合硬件规格。
- 服务启动失败时，请检查 GPIO、SPI 接线和 `journalctl` 日志。
- 安装脚本默认使用阿里云 PyPI 镜像安装依赖。
