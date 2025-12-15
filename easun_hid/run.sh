#!/bin/sh
set -e

echo "Starting EASUN HID Reader add-on..."

export HID_DEVICE=/dev/hidraw0
export MQTT_HOST=localhost
export MQTT_PORT=1883
export MQTT_PREFIX=easun1

exec python3 /app/easun_hid.py

