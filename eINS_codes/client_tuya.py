# Get device information from the Tuya Developer Platform.
DeviceID = '265ec6f2ffd8110bb83vq2'
DeviceSecret = 'bZw561R47Szib3uX'

# Default settings
Address='localhost'
Port = 1883

# Calculate Client ID
ClientID = 'tuyalink_'+DeviceID

# Calculate user name
import time
T = int(time.time())
UserName= f'''{DeviceID}|signMethod=hmacSha256,timestamp={T},secureMode=1,accessType=1'''

# Calculate password
import hmac
from hashlib import sha256

data = f'''deviceId={DeviceID},timestamp={T},secureMode=1,accessType=1'''.encode('utf-8')  # Encrypted data
appsecret = DeviceSecret.encode('utf-8')  # Secret key

Password = hmac.new(appsecret, data, digestmod=sha256).hexdigest()

# Print the parameters required for connecting to MQTT.
print('-'*20)
print('Client ID: ',ClientID)
print('Server address: ',Address)
print('Port: ',Port)
print('*Username: ',UserName)
print('*Password: ',Password)

print('SSL/TLS: true\nCertificate type: CA signed server\nSSL secure: Enable')
print('-'*20)

import paho.mqtt.client as mqtt

# Configura il client
client = mqtt.Client(client_id="tuyalink_265ec6f2ffd8110bb83vq2")

# Connettiti al broker Mosquitto locale
client.connect("localhost", 1883, 60)

# Sottoscriviti a un topic
client.subscribe("#")

# Callback per la ricezione dei messaggi
def on_message(client, userdata, msg):
    print(f"Messaggio ricevuto su {msg.topic}: {msg.payload.decode()}")

client.on_message = on_message

# Avvia il loop per ascoltare i messaggi
client.loop_forever()
