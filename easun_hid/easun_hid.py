#!/usr/bin/env python3
import time
import struct
import json
import paho.mqtt.client as mqtt
import os

# ========= KONFIGURACE =========

HID_DEVICE = os.environ.get("HID_DEVICE", "/dev/hidraw0")

MQTT_HOST = os.environ.get("MQTT_HOST", "localhost")
MQTT_PORT = int(os.environ.get("MQTT_PORT", "1883"))
MQTT_USER = os.environ.get("MQTT_USER", "")
MQTT_PASSWORD = os.environ.get("MQTT_PASSWORD", "")
MQTT_PREFIX = os.environ.get("MQTT_PREFIX", "easun1")

POLL_INTERVAL = 10  # sekundy

# ========= CRC =========

def calc_crc(command: bytes) -> bytes:
    crc = 0
    for b in command:
        crc ^= b << 8
        for _ in range(8):
            if crc & 0x8000:
                crc = (crc << 1) ^ 0x1021
            else:
                crc <<= 1
            crc &= 0xFFFF
    return struct.pack(">H", crc)

# ========= HID KOMUNIKACE =========

def send_command(dev, cmd: str) -> bytes:
    payload = cmd.encode()
    crc = calc_crc(payload)
    packet = payload + crc + b"\r"

    dev.write(packet)
    time.sleep(0.4)

    # SM IV často posílá víc dat
    return dev.read(128)

# ========= PARSOVÁNÍ =========

def parse_qpigs(resp: bytes) -> dict:
    try:
        text = resp.decode(errors="ignore").strip("\x00\r\n")
        print("RAW TEXT:", text)

        if not text.startswith("("):
            return {}

        values = text[1:].split(" ")

        return {
            "grid_voltage": float(values[0]),
            "grid_frequency": float(values[1]),
            "ac_output_voltage": float(values[2]),
            "ac_output_frequency": float(values[3]),
            "ac_output_apparent_power": int(values[4]),
            "ac_output_active_power": int(values[5]),
            "battery_voltage": float(values[8]),
            "battery_capacity": int(values[9]),
            "pv_input_voltage": float(values[10]),
            "pv_input_power": int(values[12]),
        }

    except Exception as e:
        print("Parse error:", e)
        return {}

# ========= START =========

print("===================================")
print("Starting EASUN HID Reader SM IV 5.6kW")
print("HID device:", HID_DEVICE)
print("MQTT:", MQTT_HOST, MQTT_PORT)
print("Prefix:", MQTT_PREFIX)
print("===================================")

mqttc = mqtt.Client()
if MQTT_USER:
    mqttc.username_pw_set(MQTT_USER, MQTT_PASSWORD)

mqttc.connect(MQTT_HOST, MQTT_PORT, 60)
mqttc.loop_start()

with open(HID_DEVICE, "rb+", buffering=0) as hid:
    print("HID device opened")

    while True:
        try:
            resp = send_command(hid, "QPIGS")
            print("RAW BYTES:", resp)

            data = parse_qpigs(resp)

            if data:
                print("QPIGS:", data)
                for k, v in data.items():
                    mqttc.publish(f"{MQTT_PREFIX}/{k}", v)

        except Exception as e:
            print("ERROR:", e)

        time.sleep(POLL_INTERVAL)
