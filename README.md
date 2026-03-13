# 🏠 Digital Twin Framework for Smart Building Energy Management

## Overview

This repository implements a **sensor-driven Digital Twin (DT) framework** for personalised energy management in smart buildings, with an application to Ambient Assisted Living (AAL). The system integrates:

- A three-class ontology (**BDT / ODT / PDT**) deployed on **Azure Digital Twins**
- A heterogeneous **IoT sensing layer** (Shelly, Tuya, Sensibo devices)
- A local **MQTT backbone** (Mosquitto on Raspberry Pi 5)
- **Azure IoT Hub + Cosmos DB** for cloud telemetry and history
- A **Flask web dashboard** for real-time and dataset-based visualisation

The framework was designed following a **non-intrusive philosophy**: the system delivers informative energy feedback to occupants via a dashboard without issuing direct appliance control commands.

> 📄 Reference paper: *"Digital Twin Framework for Personalized Building Management in Ambient Assisted Living"* – Marcello F., Chouquir A.Y., Atzori L., Pilloni V. (2024)  
> 📘 Reference thesis: *"Sviluppo di un modello ontologico basato sul paradigma di Digital Twin per l'efficientamento energetico negli edifici"*

---

## System Architecture

```
┌─────────────────────────────────────────────────────────────────────────┐
│                        PHYSICAL LAYER (IoT Devices)                     │
│  Shelly Plus Plug S · Shelly EM 50A · Shelly H&T · Tuya PIR/Light/Door │
│                     Sensibo Sky · Raspberry Pi 5                        │
└───────────┬─────────────────────────────────────┬───────────────────────┘
            │  MQTT (Mosquitto)                   │  HTTP REST
            ▼                                     ▼
┌───────────────────────┐             ┌───────────────────────────────────┐
│   Local CSV Storage   │             │        Azure IoT Hub              │
│  (edge persistence)   │             │  (hubIoTCDL2.azure-devices.net)   │
└───────────────────────┘             └────────────────┬──────────────────┘
                                                       │
                                            ┌──────────▼──────────┐
                                            │   Azure Event Hub   │
                                            └──────────┬──────────┘
                                                       │
                                            ┌──────────▼──────────┐
                                            │   Azure Function    │
                                            └──────────┬──────────┘
                                                       │
                              ┌────────────────────────▼──────────────────┐
                              │          Azure Digital Twins               │
                              │   BDT ←──── ODT ────→ PDT                 │
                              └────────────────────────┬──────────────────┘
                                                       │
                                            ┌──────────▼──────────┐
                                            │   Azure Cosmos DB   │
                                            │   (NoSQL history)   │
                                            └──────────┬──────────┘
                                                       │
                                            ┌──────────▼──────────┐
                                            │  Flask Dashboard    │
                                            │  localhost:5000     │
                                            └─────────────────────┘
```

### Digital Twin Classes

| Class | Full Name | Models |
|-------|-----------|--------|
| **BDT** | Building Digital Twin | Building structure, energy state, indoor/outdoor parameters, RES production |
| **ODT** | Object Digital Twin | Individual devices and appliances: consumption profile, operational state, sensor readings |
| **PDT** | Personal Digital Twin | Occupant behaviour = **Habit** (historical pattern) + **Activity** (current detected action) |

Relationships are bidirectional: BDTs contain ODTs and PDTs; ODTs feed data into both BDTs and PDTs; PDTs trigger state changes in the BDT.

### IoT Acquisition Paths

Two parallel acquisition strategies are implemented:

**Path A – MQTT (Mosquitto)**
```
Shelly/Tuya devices  →  Mosquitto broker (Raspberry Pi 5)
                     →  mqtt_rasp.py / mqtt_windows_*.py  →  CSV files
```

**Path B – HTTP + Azure**
```
Shelly Plus Plug S  →  HTTP REST polling (shelly-bridge.py)
                    →  Azure IoT Hub  →  Cosmos DB  →  Digital Twins
```

---

## Repository Structure

```
.
├── file_ontologia/               # DTDL JSON ontology models
│   ├── BDT.json                  #   Building Digital Twin model
│   ├── ODT.json                  #   Object Digital Twin model
│   ├── PDT.json                  #   Personal Digital Twin model
│   └── ...                       #   Additional entity models
│
├── codici_eINS/                  # IoT acquisition scripts
│   ├── client_tuya.py            #   Tuya MQTT client
│   ├── mqtt_rasp.py              #   Raspberry Pi MQTT collector (Shelly)
│   ├── mqtt_windows_smartplug.py #   Windows MQTT collector (Shelly Plug S)
│   ├── mqtt_windows_h_t.py       #   Windows MQTT collector (Shelly H&T)
│   ├── shelly-bridge.py          #   Shelly → Azure IoT Hub bridge
│   └── TEST_TELEMETRY.py         #   Azure IoT Hub telemetry test
│
├── Dashboard/                    # Flask web application
│   ├── app.py                    #   Flask routes (/example, /getdata2, /getdata3, ...)
│   ├── templates/
│   │   └── index.html            #   Main dashboard page (appliance visualisation)
│   └── static/
│       ├── styles.css
│       ├── script.js
│       ├── coffee_machine.png
│       └── washing_machine.png
│
├── Tutorial_HA/                  # Home Assistant integration guide (Phase 1)
├── passwd_mosquitto_raspberry.txt # Mosquitto hashed password file
└── README.md
```

---

## Hardware Devices

| Device | Function | Protocol | Output |
|--------|----------|----------|--------|
| **Raspberry Pi 5** (8 GB) | Local controller, MQTT broker host | — | — |
| **Shelly Plus Plug S** | Appliance-level energy monitoring | Wi-Fi / MQTT + HTTP | Power (W), Energy (kWh) |
| **Shelly EM 50A** | Building-level metering (2 channels, 50 A clamps) | Wi-Fi / MQTT | Voltage, Current, Active/Apparent Power |
| **Shelly H&T** | Temperature and humidity sensing | Wi-Fi / MQTT | °C, % RH |
| **Tuya PIR Sensor** | Occupancy detection | Wi-Fi / MQTT | Motion boolean |
| **Tuya Illuminance Sensor** | Ambient light monitoring | Wi-Fi / MQTT | Lux (0–1000) |
| **Tuya Door/Window Sensor** | Open/closed state monitoring | Wi-Fi / MQTT | Boolean |
| **Sensibo Sky** | HVAC control via infrared | Wi-Fi / IR | On/off state, temperature setpoint |

---

## Getting Started

### Prerequisites

```bash
# Python environment
python3 -m venv venv
source venv/bin/activate          # Linux/macOS
venv\Scripts\activate             # Windows

pip install paho-mqtt azure-iot-device requests flask
```

| Requirement | Details |
|-------------|---------|
| Python | ≥ 3.8 |
| Mosquitto MQTT broker | Running on Raspberry Pi 5 (or any local host) |
| Azure subscription | IoT Hub · Digital Twins · Cosmos DB provisioned |
| Azure Digital Twins Explorer | Web portal for model upload |

---

### 1. Ontology Upload (Azure Digital Twins)

1. Open the [Azure Digital Twins Explorer](https://explorer.digitaltwins.azure.net) and connect to your ADT instance.
2. Click **Upload a model** and select all JSON files from `file_ontologia/`.
3. After upload, switch to the **Twin Graph** panel and manually create the relationships:

| Relationship | Direction | Description |
|---|---|---|
| `contains` | BDT → ODT | Building contains object/device |
| `contains` | BDT → PDT | Building contains occupant |
| `isUsedBy` | ODT → PDT | Device usage feeds occupant profile |
| `updates` | PDT → BDT | Occupant activity updates building state |

> **Note:** The current implementation simulates the Azure IoT Hub via local Python scripts. Physical sensor data is bridged to ADT via `shelly-bridge.py` + Azure Function routing.

---

### 2. Configure the MQTT Broker

On the **Raspberry Pi 5**:

```bash
# Install and start Mosquitto
sudo apt install mosquitto mosquitto-clients
sudo systemctl enable mosquitto

# Set up authentication
sudo mosquitto_passwd -c /etc/mosquitto/passwd <your_username>
# Reference the password file in /etc/mosquitto/mosquitto.conf:
#   allow_anonymous false
#   password_file /etc/mosquitto/passwd
```

Update credentials in the acquisition scripts before running:

```python
# In mqtt_rasp.py, mqtt_windows_*.py
mqtt_username = "your_username"
mqtt_password = "your_password"
```

---

### 3. Run Acquisition Scripts

**Option A – Raspberry Pi (MQTT collection for Shelly devices)**

```bash
python3 codici_eINS/mqtt_rasp.py
# → writes to shelly_filtered_data.csv (every 5 s)
```

**Option B – Windows PC (Shelly Plug S)**

```bash
python3 codici_eINS/mqtt_windows_smartplug.py
# → writes to dati_Shelly11.csv (every 5 s)
```

**Option B – Windows PC (Shelly H&T)**

```bash
python3 codici_eINS/mqtt_windows_h_t.py
# → writes to dati_H&T2.csv (every 5 s)
```

**Option C – Tuya device listener**

```bash
# Edit DeviceID and DeviceSecret in client_tuya.py first
python3 codici_eINS/client_tuya.py
```

**Option D – Shelly → Azure IoT Hub bridge**

```bash
# Edit SHELLY_IP and DEVICE_CONNECTION_STRING in shelly-bridge.py first
python3 codici_eINS/shelly-bridge.py
# → polls Shelly REST API every 10 s and sends to IoT Hub
```

**Validation – Azure telemetry test**

```bash
# Edit CONNECTION_STRING in TEST_TELEMETRY.py first
python3 codici_eINS/TEST_TELEMETRY.py
# → sends simulated temperature/humidity/age to IoT Hub every 30 s
```

---

### 4. Run the Dashboard

```bash
cd Dashboard/
python3 app.py
```

Open your browser at **http://127.0.0.1:5000/example**

---

## Scripts Reference

### `client_tuya.py`

Connects to the local Mosquitto broker as a Tuya-compatible MQTT client. Generates HMAC-SHA256 credentials from `DeviceID` and `DeviceSecret` at runtime.

```python
# Key parameters
DeviceID     = '265ec6f2ffd8110bb83vq2'
DeviceSecret = '<your_secret>'
Address      = 'localhost'
Port         = 1883
```

Subscribes to all topics (`#`) and prints incoming payloads. Useful for inspecting raw Tuya sensor messages before adding structured parsing.

---

### `mqtt_rasp.py`

Runs on the Raspberry Pi 5. Subscribes to all MQTT topics, silently drops `online` and `cloud` status messages, and every **5 seconds** appends the most recent values for the following Shelly fields to a CSV:

| Field | Meaning |
|-------|---------|
| `apower` | Active power (W) |
| `voltage` | Voltage (V) |
| `current` | Current (A) |
| `output` | On/off state |
| `temperature` | Device temperature (°C) |
| `aenergy` | Accumulated energy (kWh) |

Output file: `shelly_filtered_data.csv` (`Timestamp, Topic, Key, Value`)

---

### `mqtt_windows_smartplug.py`

Identical logic to `mqtt_rasp.py`, intended to run on a Windows PC. Saves to `dati_Shelly11.csv`. The same six Shelly fields are extracted.

---

### `mqtt_windows_h_t.py`

Runs on a Windows PC. Subscribes to all topics and saves **every JSON key-value pair** (not a fixed whitelist) to `dati_H&T2.csv`. This makes it suitable for capturing the full payload from Shelly H&T sensors, which publish `temperature` and `humidity` in a flat JSON object. Each received message is also printed to stdout for real-time debugging.

---

### `shelly-bridge.py`

Bridges the Shelly Plus Plug S to Azure IoT Hub by polling its HTTP REST endpoint every **10 seconds**.

```
GET http://<SHELLY_IP>/rpc/Switch.GetStatus?id=0
```

The response is mapped to the following telemetry message and sent to IoT Hub:

```json
{
  "power":         <apower>,
  "voltage":       <voltage>,
  "current":       <current>,
  "energyTotalWh": <aenergy.total>,
  "temperatureC":  <temperature.tC>,
  "isOn":          <output>
}
```

**Configuration:**

```python
SHELLY_IP                = "172.20.10.4"          # update to your device IP
DEVICE_CONNECTION_STRING = "HostName=...;DeviceId=shelly-bridge;SharedAccessKey=..."
```

---

### `TEST_TELEMETRY.py`

Validates end-to-end connectivity to Azure IoT Hub by sending simulated telemetry every **30 seconds**. Use this before deploying physical sensors to confirm that the hub ingestion pipeline, Cosmos DB routing, and DT update path are all functioning correctly.

```python
CONNECTION_STRING = "HostName=hubIoTCDL2.azure-devices.net;DeviceId=ontology;SharedAccessKey=..."
# Message format: { "deviceId": "myDevice", "temperature": float, "humidity": float, "age": float }
```

---

## Dashboard Pages

The Flask application exposes the following pages at `localhost:5000`:

| URL | Content |
|-----|---------|
| `/example` | **Home** – activity and consumption charts from CASAS, DEDDIAG, and PV datasets |
| `/example` → "Digital Twin" tab | **Ontology visualisation** + video of live Shelly Plus S → Azure Digital Twins integration |
| `/example` → "Smart Plug Sensing" | **Appliance monitoring** – real consumption trace of a microwave oven (residential deployment) |
| `/example` → "Smart Meter Sensing" | **Building metering** – energy consumption of the Civil Engineering building, UniCa campus, via Shelly EM 50A (contact: Andrea Frattolillo) |

The home dashboard fetches two JSON endpoints:

| Endpoint | Data | Appliance |
|----------|------|-----------|
| `/getdata3` | `consumption_coffee` (kWh), timestamp | Coffee machine |
| `/getdata2` | `consumption_wm` (kWh), time (minutes) | Washing machine |

Appliance icons animate **on** (coloured) / **off** (greyed) based on whether consumption > 0. Values update every **200 ms** to simulate real-time playback of the DEDDIAG dataset.

---

## Configuration

All sensitive parameters are currently hard-coded in the scripts. Before deploying to a shared or production environment, move them to environment variables or a `.env` file:

| Parameter | Script | Description |
|-----------|--------|-------------|
| `DeviceID` / `DeviceSecret` | `client_tuya.py` | Tuya developer platform credentials |
| `mqtt_username` / `mqtt_password` | `mqtt_rasp.py`, `mqtt_windows_*.py` | Mosquitto broker credentials |
| `SHELLY_IP` | `shelly-bridge.py` | Local IP address of the Shelly Plus Plug S |
| `DEVICE_CONNECTION_STRING` | `shelly-bridge.py`, `TEST_TELEMETRY.py` | Azure IoT Hub connection string |

> ⚠️ **Security note:** Never commit real connection strings or device secrets to a public repository. Use `python-dotenv` or GitHub Secrets for CI/CD pipelines.

---

## Dependencies

```
paho-mqtt>=1.6
azure-iot-device>=2.12
requests>=2.28
flask>=2.3
```

Front-end (loaded via CDN in `index.html`):

```
jQuery 3.6.0
Chart.js (latest)
Konva.js 8.3.3
```

---

## Related Publications

```bibtex
@inproceedings{marcello2024dt,
  author    = {Marcello, Francesca and Chouquir, Azzedine Youssef and Atzori, Luigi and Pilloni, Virginia},
  title     = {Digital Twin Framework for Personalized Building Management in Ambient Assisted Living},
  year      = {2024},
  note      = {Department of Electrical and Electronic Engineering, University of Cagliari}
}

@article{marcello2019activity,
  author    = {Marcello, Francesca and Pilloni, Virginia and Giusto, Daniele},
  title     = {Sensor-Based Early Activity Recognition Inside Buildings to Support Energy and Comfort Management Systems},
  journal   = {Energies},
  volume    = {12},
  number    = {13},
  pages     = {2631},
  year      = {2019}
}
```

---

## Acknowledgements

This work was partially supported by the European Union – NextGenerationEU (National Sustainable Mobility Center CN00000023, Italian Ministry of University and Research, Spoke 8), the Italian Ministry of Enterprises and Made in Italy (MIMIT) within the 5G technology support program – "Cagliari Digital Lab" (ID: G27F22000040008), the PRIN project HIPPOCRATES (ID: 2022YSRWEZ), and Fondazione di Sardegna – "SENeCO" project (F73C23001690007).

---

*University of Cagliari – DIEE / Net4U Lab · WP6 Digitalisation, Smart Grids and Flexibility*
