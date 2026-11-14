#!/bin/bash

if [ "$(id -u)" -ne 0 ]; then
    echo 'install fail!'
    echo "This script must be run as root." >&2
    exit 1
fi
disp_dir=$(cd "$(dirname "$0")" && pwd)
board=rpi5

while [ "$#" -gt 0 ]; do
    case "$1" in
        -b|--board)
            if [ "$#" -lt 2 ]; then
                echo "Missing value for $1" >&2
                exit 1
            fi
            board=$2
            shift 2
            ;;
        --board=*)
            board=${1#*=}
            if [ -z "$board" ]; then
                echo "Missing value for --board" >&2
                exit 1
            fi
            shift
            ;;
        -h|--help)
            echo "Usage: $0 [-b|--board BOARD]"
            exit 0
            ;;
        *)
            echo "Unknown option: $1" >&2
            echo "Usage: $0 [-b|--board BOARD]" >&2
            exit 1
            ;;
    esac
done

config_file=${disp_dir}/examples/config.${board}.py
if [ ! -f "$config_file" ]; then
    echo "Board configuration not found: $config_file" >&2
    exit 1
fi

# Select the board-specific configuration before copying the project.
cp -f "$config_file" "${disp_dir}/config.py"
echo ${disp_dir}
#cp -rf ${cur_dir} /usr/local
apt install -y python3 python3-pip python3-venv python3-dev

python3 -m venv ${disp_dir}/venv
${disp_dir}/venv/bin/pip install -r ${disp_dir}/requirements.txt -i https://mirrors.aliyun.com/pypi/simple
#/usr/local/pinas-display/venv/bin/python /usr/local/pinas-display/main.py
if ! test -d "/usr/local/pinas-display"; then
    mkdir -p /usr/local/pinas-display
fi
cp -rf ${disp_dir}/* /usr/local/pinas-display
cp -f ${disp_dir}/spiled.service /etc/systemd/system
systemctl enable spiled.service
systemctl start spiled.service
echo 'install path: /usr/local/pinas-display'
echo 'install success!'
