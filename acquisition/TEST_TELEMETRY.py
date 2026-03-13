#TEST TELEMETRY 1 

import random
import time
from azure.iot.device import IoTHubDeviceClient, Message


# Replace with your device connection string
CONNECTION_STRING = "HostName=hubIoTCDL2.azure-devices.net;DeviceId=ontology;SharedAccessKey=F4wQKY+f7ti1mAdcVj8L1BE6xb0zvXyMOAIoTBNdAvI="
# Define the JSON message to send to IoT Hub.
MSG_TXT = '{{"msgCount": {msgCount}, "temperature": {temperature}, "humidity": {humidity}}}'
def iothub_client_init():
# Create an IoT Hub client
  client = IoTHubDeviceClient.create_from_connection_string(CONNECTION_STRING)
  return client
  client = iothub_client_init()

#TEST TELEMETRY 2

client = IoTHubDeviceClient.create_from_connection_string(CONNECTION_STRING)

# Disconnect from IoT Hub
client.disconnect()
# Connect to IoT Hub
client.connect()
# Run the telemetry sample


#telemetry test 2
CONNECTION_STRING = "HostName=hubIoTCDL2.azure-devices.net;DeviceId=ontology;SharedAccessKey=F4wQKY+f7ti1mAdcVj8L1BE6xb0zvXyMOAIoTBNdAvI="
MSG_TXT = '{{"deviceId": "myDevice","temperature": {temperature},"humidity": {humidity},"age":{age}}}'
#MSG_TXT = '{{"deviceId": "myDevice","age": {age},"humidity": {humidity}}}'
def iothub_client_telemetry_sample_run():
    try:
        print("IoT Hub device sending periodic messages, press Ctrl-C to exit")
        msgCount = 0
        while True:
            # Build the message with simulated telemetry values.
            temperature = round(random.uniform(24, 27), 2)
            age = random.uniform(18, 90)
            humidity = round(random.uniform(30, 50), 2)
            msg_txt_formatted = MSG_TXT.format(msgCount=msgCount, temperature=temperature, humidity=humidity, age=age)
            message = Message(msg_txt_formatted)

            # Send the message.
            print("Sending message: {}".format(message))
            client.send_message(message)
            print("Message successfully sent")
            msgCount += 1

            # Wait for 30 seconds before sending the next message
            time.sleep(30)

    except KeyboardInterrupt:
        print("IoTHubClient sample stopped")

# Initialize the device client
client = IoTHubDeviceClient.create_from_connection_string(CONNECTION_STRING)

# Run the telemetry sample
iothub_client_telemetry_sample_run()

