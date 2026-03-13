#codice per connettere lo shelly plug s all'IoT Azure
#http://192.168.8.123/rpc/Switch.GetStatus?id=0 IP dello smart plug su Postman
from azure.iot.device import IoTHubDeviceClient, Message
import requests
import json
import time

# 🔧 CONFIGURA QUI
SHELLY_IP = "172.20.10.4"
DEVICE_CONNECTION_STRING = "HostName=hubIoTCDL2.azure-devices.net;DeviceId=shelly-bridge;SharedAccessKey=vMK35yxl2WYkf3X2+MT3Y6yOe9QDm3NWCe22E3kA0fQ="

client = IoTHubDeviceClient.create_from_connection_string(DEVICE_CONNECTION_STRING)

from azure.iot.device import IoTHubDeviceClient

try:
    client = IoTHubDeviceClient.create_from_connection_string("HostName=hubIoTCDL2.azure-devices.net;DeviceId=shelly-bridge;SharedAccessKey=vMK35yxl2WYkf3X2+MT3Y6yOe9QDm3NWCe22E3kA0fQ=")
    client.connect()
    print("✅ Connessione a IoT Hub riuscita!")
except Exception as e:
    print("❌ Connessione fallita:", e)

def get_shelly_data():
    url = f"http://{SHELLY_IP}/rpc/Switch.GetStatus?id=0"
    r = requests.get(url, timeout=5)
    data = r.json()
    return {
        "power": data.get("apower"),
        "voltage": data.get("voltage"),
        "current": data.get("current"),
        "energyTotalWh": data.get("aenergy", {}).get("total"),
        "temperatureC": data.get("temperature", {}).get("tC"),
        "isOn": data.get("output")
    }

while True:
    try:
        data = get_shelly_data()
        msg = Message(json.dumps(data))
        print("📤 Inviando a IoT Hub:", data)
        client.send_message(msg)
    except Exception as e:
        print("❌ Errore:", e)
    
    time.sleep(10)  # ogni 10 secondi
