# MQTT
import ibmiotf.application
import time
import json


# External module imports                                                                                                        
import RPi.GPIO as GPIO   



# Pin Definitons:                                                                                                                
TRIG = 5 # Broadcom pin 18 (P1 pin 12)                                                                                     
ECHO = 6 # Broadcom pin 23 (P1 pin 16)                                                                                   
LIDCOVER = 15
alarmOut = 22 # Broadcom pin 22 (P1 pin 15) 




def ultrasonicSensor_init():
	GPIO.setmode(GPIO.BCM)
	GPIO.setup(TRIG,GPIO.OUT)
	GPIO.setup(ECHO,GPIO.IN)
	GPIO.setup(LIDCOVER,GPIO.IN)
	GPIO.setup(alarmOut,OUT)
	GPIO.output(TRIG, False)
	GPIO.output(alarmOut,False)

def distanceMeasurement():
	try:
		global client,deviceType,deviceId
		l_prev_distance = 0
		while 1:
			ultrasonicSensor_init()
			if GPIO.input(LIDCOVER) == 0:
				time.sleep(2)		
				GPIO.output(TRIG, True)
				time.sleep(0.00001)
				GPIO.output(TRIG, False)
				#Starts the timer 
				while GPIO.input(ECHO)==0:
					pulse_start = time.time()
				#Waits for the timer to end once the pin is high
				while GPIO.input(ECHO)==1:
					pulse_end = time.time()

				pulse_duration = pulse_end - pulse_start

				l_distance = pulse_duration * 17150

				l_distance = round(l_distance, 2)

				if(l_prev_distance != l_distance and l_prev_distance > (l_distance+3) or l_prev_distance < (l_distance-3)):
					l_prev_distance = l_distance
					message = {"ID":1,"distance":l_distance}
					client.publishEvent(deviceType, deviceId, "status", "json", message)
			
				if l_distance <50:
					GPIO.output(alarmOut,True) 

				print "Distance:",l_distance,"cm"
	except KeyboardInterrupt:			
		GPIO.cleanup()

def init():
	global client,deviceType,deviceId
	organization = "5q764p"
	appId = "APP"
	authMethod = "apikey"
	authKey = "a-5q764p-bpnugpigze"
	authToken = "JZ4YT5_*n+9OWXw9*w"
	deviceType = "Trashcan"
	deviceId = "APP"                                                                                                        
	options = {"org": organization, "id":appId, "auth-method": authMethod, "auth-key": authKey, "auth-token": authToken}
	client = ibmiotf.application.Client(options)
	client.connect()


if __name__ == '__main__':
	init()
	distanceMeasurement()		