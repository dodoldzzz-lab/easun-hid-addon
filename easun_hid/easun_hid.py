#!/usr/bin/env python3
import time
import json
import os
import sys
import traceback

# Import pyusb
try:
    import usb.core
    import usb.util
except ImportError:
    usb = None

# Import paho-mqtt
try:
    import paho.mqtt.client as mqtt
except ImportError:
    mqtt = None

OPTIONS_PATH = "/data/options.json"

def load_options():
    """Load Home Assistant add-on options."""
    try:
        with open(OPTIONS_PATH, "r") as f:
            return json.load(f)
    except Exception as e:
        print("Failed to load options.json:", e)
        return {}

def mqtt_connect(host, port, user=None, password=None):
    """Connect to MQTT broker."""
    if mqtt is None:
        print("paho-mqtt not installed, exiting.")
        sys.exit(1)

    client = mqtt.Client()
    if user:
        client.username_pw_set(user, password)
    try:
        client.connect(host, port, 60)
        client.loop_start()
        print(f"Connected to MQTT broker at {host}:{port}")
        return client
    except Exception as e:
        print("MQTT connect failed:", e)
        return None

def find_device(vendor=0x0665, product=0x5161):
    """Find USB device using pyusb."""
    if usb is None:
        print("pyusb not installed, exiting.")
        sys.exit(1)
    dev = usb.core.find(idVendor=vendor, idProduct=product)
    return dev

def publish(client, topic, payload):
    """Publish data to MQTT."""
    if client:
        try:
            client.publish(topic, json.dumps(payload))
        except Exception as e:
            print("MQTT publish error:", e)
    else:
        print("MQTT not connected:", topic, payload)

def read_loop(options):
    """Main loop to read inverter data and publish via MQTT."""
    mqtt_client = mqtt_connect(
        options.get("mqtt_host", "localhost"),
        options.get("mqtt_port", 1883),
        options.get("mqtt_user", ""),
        options.get("mqtt_password", "")
    )

    inverters = options.get("inverters", [])
    if not inverters:
        inverters = [{"name":"easun1","device":"/dev/hidraw0","mqtt_prefix":"easun/1"}]

    while True:
        try:
            for inv in inverters:
                name = inv.get("name", "easun")
                prefix = inv.get("mqtt_prefix", f"easun/{name}")
                # Try to find USB device
                dev = find_device()
                if dev is None:
                    # Publish dummy telemetry if device not found
                    data = {
                        "name": name,
                        "status": "no_device",
                        "power_w": 0,
                        "voltage_v": 0,
                        "timestamp": int(time.time())
                    }
                    publish(mqtt_client, f"{prefix}/telemetry", data)
                    print(f"No device found for {name}, publishing dummy data.")
                else:
                    # TODO: Implement actual HID protocol reading here
                    data = {
                        "name": name,
                        "status": "device_found",
                        "idVendor": hex(dev.idVendor),
                        "idProduct": hex(dev.idProduct),
                        "timestamp": int(time.time())
                    }
                    publish(mqtt_client, f"{prefix}/telemetry", data)
                    print(f"Device found for {name}, publishing data.")
            time.sleep(10)
        except KeyboardInterrupt:
            print("Keyboard interrupt received, exiting.")
            break
        except Exception:
            traceback.print_exc()
            time.sleep(5)

def main():
    if usb is None or mqtt is None:
        print("Required libraries missing. Exiting.")
        sys.exit(1)
    
    options = load_options()
    read_loop(options)

if __name__ == "__main__":
    main()
