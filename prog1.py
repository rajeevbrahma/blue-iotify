
# MQTT
import ibmiotf.application
import threading
import time
import json

def pubFunc():
	i = 0
	while True:

		myData={"message" : "Hello Iotify!","number":i}
		# print myData
		deviceId = "APP"
		client.publishEvent(deviceType, deviceId, "status", "json", myData)
		i+=1
		time.sleep(10)



def callback(event):
	print json.dumps(event.data)

	

organization = "5q764p"

appId = "DEVICE"

authMethod = "apikey"
authKey = "a-5q764p-bpnugpigze"
authToken = "JZ4YT5_*n+9OWXw9*w"

deviceType = "Trashcan"

deviceId = "DEVICE"

options = {"org": organization, "id":appId, "auth-method": authMethod, "auth-key": authKey, "auth-token": authToken}

client = ibmiotf.application.Client(options)

client.connect()

client.deviceEventCallback = callback
client.subscribeToDeviceEvents(deviceType=deviceType)

pubFunc()
