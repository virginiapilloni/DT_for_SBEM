import paho.mqtt.client as mqtt
import csv
import os
import json
from datetime import datetime, timedelta
 
# File CSV per salvare i dati
csv_file = "dati_Shelly11.csv"
 
# Crea il file CSV con intestazioni, se non esiste
if not os.path.exists(csv_file):
    with open(csv_file, mode="w", newline="") as file:
        writer = csv.writer(file)
        writer.writerow(["Timestamp", "Topic", "Key", "Value"])
 
# Credenziali per il broker MQTT
mqtt_username = "mio_utente"
mqtt_password = "ciao"

# Dizionario per tracciare i valori più recenti
latest_data = {}
last_save_time = datetime.min
 
# Topic da ignorare
ignored_topics = []#["online","cloud"]

# Callback quando il client si connette
def on_connect(client, userdata, flags, rc):
    if rc == 0:
        print("Connesso al broker MQTT con successo!")
        client.subscribe("#")  # Sottoscrive a tutti i topic
    else:
        print(f"Errore nella connessione al broker. Codice: {rc}")
 
# Callback quando arriva un messaggio
def on_message(client, userdata, msg):
    global latest_data
    topic = msg.topic
    payload = msg.payload.decode()
    print(f"Ricevuto messaggio su {topic}: {payload}")

    # Ignora topic non rilevanti
    if any(ignored in topic for ignored in ignored_topics):
        return
 
    # Prova a decodificare il payload come JSON
    try:
        data = json.loads(payload)
        latest_data[topic] = data  # Salva i dati come JSON
    except json.JSONDecodeError:
        # Salva come stringa normale se non è JSON
        latest_data[topic] = payload
 
# Funzione per salvare i dati filtrati nel CSV
def save_to_csv():
    global latest_data, last_save_time
    current_time = datetime.now()
 
    if current_time - last_save_time >= timedelta(seconds=5):
        with open(csv_file, mode="a", newline="") as file:
            writer = csv.writer(file)
 
            for topic, value in latest_data.items():
                print(f"latest_data: {latest_data}")
                # Estrai dati utili dal JSON o salva il valore direttamente
                if isinstance(value, dict):
                    # Salva solo chiavi utili (es. apower, voltage, current, aenergy)
                    for key in ["apower", "voltage", "current", "output", "temperature", "aenergy"]:
                        if key in value:
                            writer.writerow([current_time.strftime("%Y-%m-%d %H:%M:%S"), topic, key, value[key]])
                else:
                    # Salva direttamente se il valore non è JSON
                    writer.writerow([current_time.strftime("%Y-%m-%d %H:%M:%S"), topic, "raw", value])
 
        last_save_time = current_time  # Aggiorna l'ultimo salvataggio
 
# Configurazione del client MQTT
client = mqtt.Client()
client.username_pw_set(mqtt_username, mqtt_password)
client.on_connect = on_connect
client.on_message = on_message
 
# Connessione al broker MQTT
broker_address = "localhost"
broker_port = 1883
client.connect(broker_address, broker_port, 60)
 
# Loop principale
try:
    while True:
        client.loop(timeout=5.0)
        save_to_csv()  # Salva i dati ogni 5 secondi
        print("salvataggio\n")

except KeyboardInterrupt:
    print("Chiusura script...")
    client.disconnect()