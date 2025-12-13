\
#!/usr/bin/env python3
import time
import json
import os
import sys
import traceback

try:
    import usb.core
    import usb.util
except Exception:
    usb = None

try:
    import paho.mqtt.client as mqtt
except Exception:
    mqtt = None

OPTIONS_PATH = "/data/options.json"

def load_options():
    # Home Assistant Supervisor writes addon options to /data/options.json
    try:
        with open(OPTIONS_PATH, "r") as f:
            return json.load(f)
    except Exception:
        return None

def mqtt_connect(host, port, user, password):
    if mqtt is None:
        print("paho-mqtt not installed")
        return None
    client = mqtt.Client()
    if user:
        client.username_pw_set(user, password)
    try:
        client.connect(host, port, 60)
        client.loop_start()
        return client
    except Exception as e:
        print("MQTT connect failed:", e)
        return None

def find_device(vendor=0x0665, product=0x5161):
    if usb is None:
        print("pyusb not installed")
        return None
    dev = usb.core.find(idVendor=vendor, idProduct=product)
    return dev

def publish(client, topic, payload):
    if client:
        try:
            client.publish(topic, json.dumps(payload))
        except Exception as e:
            print("MQTT publish error:", e)
    else:
        print("MQTT:", topic, payload)

def read_loop(options):
    mqtt_client = mqtt_connect(options.get("mqtt_host","localhost"), options.get("mqtt_port",1883), options.get("mqtt_user",""), options.get("mqtt_password",""))
    inverters = options.get("inverters", [])
    if not inverters:
        inverters = [{"name":"easun1","device":"/dev/hidraw0","mqtt_prefix":"easun/1"}]
    while True:
        try:
            for inv in inverters:
                name = inv.get("name","easun")
                prefix = inv.get("mqtt_prefix", f"easun/{name}")
                # Try to find USB device
                dev = find_device()
                if dev is None:
                    # publish dummy telemetry
                    data = {
                        "name": name,
                        "status": "no_device",
                        "power_w": 0,
                        "voltage_v": 0,
                        "timestamp": int(time.time())
                    }
                    publish(mqtt_client, f"{prefix}/telemetry", data)
                else:
                    # Placeholder: actual HID protocol should be implemented here
                    data = {
                        "name": name,
                        "status": "device_found",
                        "idVendor": hex(dev.idVendor),
                        "idProduct": hex(dev.idProduct),
                        "timestamp": int(time.time())
                    }
                    publish(mqtt_client, f"{prefix}/telemetry", data)
            time.sleep(10)
        except KeyboardInterrupt:
            break
        except Exception:
            traceback.print_exc()
            time.sleep(5)

def main():
    options = load_options() or {}
    # merge defaults from config.json if needed (not required)
    read_loop(options.get("options", options))

if __name__ == "__main__":
    main()
