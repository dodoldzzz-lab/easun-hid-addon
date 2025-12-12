# Easun HID Add-on (placeholder)

This repository contains a Home Assistant add-on that reads from EASUN inverters via USB HID and publishes basic telemetry to MQTT.

**Important:** This is a placeholder implementation. The script will attempt to find a USB device with vendor/product 0x0665/0x5161 and publish simulated values if not present. You should adapt `easun_hid.py` to the exact HID protocol of your inverter.

Files:
- repository.yaml - repository metadata
- easun_hid/config.json - add-on configuration
- easun_hid/Dockerfile
- easun_hid/run.sh
- easun_hid/requirements.txt
- easun_hid/easun_hid.py - main script (placeholder)
