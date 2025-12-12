#!/bin/sh

echo "Starting EASUN HID reader..."

while true; do
    # Read raw HID frame
    hid_output=$(cat /dev/hidraw0 2>/dev/null)

    if [ ! -z "$hid_output" ]; then
        echo "HID DATA: $hid_output"
    fi

    sleep 1
done
