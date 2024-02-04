#!/usr/bin/env bash

set -Ee
if [[ ${UID} = "0" ]]; then
    echo Don\'t run this as root!
    exit 1
fi

DIR=$( realpath "$( cd -- "$( dirname -- "${BASH_SOURCE[0]}" )" &> /dev/null && pwd )"/.. )
COMPONENT="${DIR}/component/spoolman_klipper_extensions.py"
MACRO="${DIR}/klipper_macro/spoolman_klipper_extensions.cfg"

COMPONENTS_DIR="${HOME}/moonraker/moonraker/components"
CONFIG_DIR="${HOME}/printer_data/config"

sudo systemctl stop klipper
sudo systemctl stop moonraker

ln -s "${COMPONENT}" "${COMPONENTS_DIR}"
ln -s "${MACRO}" "${CONFIG_DIR}"

sudo systemctl start klipper
sudo systemctl start moonraker
