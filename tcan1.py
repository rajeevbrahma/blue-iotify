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



'''****************************************************************************************
Function Name 	:	ultrasonicSensorInit()
Description		:	Function which initilizes the GPIO pins
Parameters 		:	-
****************************************************************************************'''

def ultrasonicSensorInit():
	GPIO.setwarnings(False)
	GPIO.setmode(GPIO.BCM)
	GPIO.setup(TRIG,GPIO.OUT)
	GPIO.setup(ECHO,GPIO.IN)
	GPIO.setup(LIDCOVER,GPIO.IN)
	GPIO.setup(alarmOut,GPIO.OUT)
	GPIO.output(TRIG, False)
	GPIO.output(alarmOut,False)

'''****************************************************************************************
Function Name 	:	distanceMeasurement()
Description		:	Function calculates the amount of waste in the trashcan and send it to the client
					and sends an alert message when trash can reaches the threshold
Parameters 		:	-
****************************************************************************************'''

def distanceMeasurement():
	try:
		global client,deviceType
		l_prev_distance = 0
		previousTime = 0
		while 1:
			ultrasonicSensorInit()
		
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
					deviceId = "APP"
					try:
						# publishing the message to the Device called APP
						pubReturn = client.publishEvent(deviceType, deviceId, "status", "json", message)
						if pubReturn ==True:
							logging.info("The message successfully sent")
					except IoTFCReSTExcetption  as e:
							print e
							# logging.info("The sent message Failed")
							# logging.error("The publishEvent exception httpcode :%s,message:%s,response:%s"(e.httpcode,e.message,e.response))
				if l_distance <50:
					GPIO.output(alarmOut,True)
					presentTime = datetime.datetime.now() 
					 
					messageBody = "Trashcan filled"
					if (previousTime!=0):
						diff = presentTime - previousTime 
				
						day  = diff.days
						hour = (day*24 + diff.seconds/3600)
						diff_minutes = (diff.days *24*60)+(diff.seconds/60)
						if diff_minutes >= 15:		
						  
							try:
								message = client.messages.create(body=messageBody,to="+919738300498",from_="+12512724152")	
								previousTime = datetime.datetime.now()
							except TwilioRestException as e:
								previousTime = datetime.datetime.now()
								print e	
					elif(previousTime == 0):
						try:
							message = client.messages.create(body=messageBody,to="+919738300498",from_="+12512724152")	
							previousTime = datetime.datetime.now()
						except TwilioRestException as e:
							previousTime = datetime.datetime.now()
							print e	
					else:
						pass	

	
	except KeyboardInterrupt: 
		GPIO.cleanup()
	except Exception as e:
		print e
		# logging.error("The distanceMeasurement exception is %s,%s"%(e,type(e)))	

	

'''****************************************************************************************
Function Name 	:	init()
Description		:	Function which connects to the ibmiotf service
Parameters 		:	-
****************************************************************************************'''

def init():
	global client,deviceType
	organization = "5q764p" #Your organization ID
	appId = "DEVICE"   # The Device you've created and wants to connect with
	authMethod = "apikey" #Method of authentication (the only value currently supported is apikey)
	authKey = "a-5q764p-bpnugpigze" #API key (required if auth-method is apikey).
	authToken = "JZ4YT5_*n+9OWXw9*w"#API key token (required if auth-method is apikey).
	deviceType = "Trashcan" # The Type of the device created in your organization 
	deviceId = "DEVICE" # The Device you've created and wants to connect with                                                                                                       
	try:
		# options require for the connection
		options = {"org": organization, "id":appId, "auth-method": authMethod, "auth-key": authKey, "auth-token": authToken}
		client = ibmiotf.application.Client(options)
		client.connect()
	except ibmiotf.connectionException as e:
		print e
		# logging.error("The iotfconnection Exception is %s,%s"%(e,type(e)))	


if __name__ == '__main__':
	init()
	distanceMeasurement()		
