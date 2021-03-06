# MQTT
import ibmiotf.application
import time
import json
import math
# External module imports                                                                                                        
import RPi.GPIO as GPIO

#logging module
import logging 

# twilio module
from twilio.rest import TwilioRestClient
from twilio import TwilioRestException

# datetime module
import datetime

LOG_FILENAME = 'Trashcanlogs.log'
logging.basicConfig(filename=LOG_FILENAME,level=logging.DEBUG,format='%(asctime)s, %(levelname)s, %(message)s', datefmt='%Y-%m-%d %H:%M:%S')


account_sid = "AC161d5213dce9632db6d2b6febdad21eb" 
auth_token  = "9ee4b0327f1e3d09b7a8928bb602ac9b"

twilioClient = TwilioRestClient(account_sid, auth_token)



# Pin Definitons:                                                                                                                
TRIG = 5 # Broadcom pin 18 (P1 pin 12)                                                                                     
ECHO = 6 # Broadcom pin 23 (P1 pin 16)                                                                                   
LIDCOVER = 15
alarmOut = 22 # Broadcom pin 22 (P1 pin 15) 

#################################
timeList = [None]*3

START_TIME = 0
END_TIME = 1
TOTAL_TIME = 2

timerFlag = 0

#################################

CRITICAL_DISTANCE = 50
LOOP_SAMPLING_TIME = 2
NOTIFICATION_TIME_DELAY = 2



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

def timerFunction():
    global timerFlag,NOTIFICATION_TIME_DELAY
    # obtains the present time, used for the 15 min interval calculation
    timeList[END_TIME] = datetime.datetime.now() 
    
    messageBody = "Trashcan at xyz filled please come to pickup"
    if(timerFlag == 0):
        timerFlag = 1
        try:
            # twilio message sent option
            message = twilioClient.messages.create(body=messageBody,to="+919738300498",from_="+12512724152")
            print "first"
        except TwilioRestException as e:
            logging.error("The 1)twilio exception is %s,%s"%(e,type(e)))	
    else:
        timeList[TOTAL_TIME] = (timeList[END_TIME] - timeList[START_TIME]).total_seconds() / 60
        print timeList[TOTAL_TIME], timeList[START_TIME], timeList[END_TIME]
        if(timeList[TOTAL_TIME] > 15):
            timerFlag = 0
            try:
                # twilio message sent option
                message = twilioClient.messages.create(body=messageBody,to="+919738300498",from_="+12512724152")	
                print 'second'
            except TwilioRestException as e:
                logging.error("The 2)twilio exception is %s,%s"%(e,type(e)))




'''****************************************************************************************
Function Name 	:	distanceMeasurement()
Description		:	Function calculates the amount of waste in the trashcan and send it to the client
					and sends an alert message when trash can reaches the threshold
Parameters 		:	-
****************************************************************************************'''

def distanceMeasurement():
    global timerFlag,client,deviceType,LOOP_SAMPLING_TIME,CRITICAL_DISTANCE
    try:
        l_prev_distance = 0

        ultrasonicSensorInit()
			
        while 1:
            if (GPIO.input(LIDCOVER) == 0):
                
                time.sleep(LOOP_SAMPLING_TIME)		
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
                l_distance = (int(math.floor(l_distance)))
                if(l_prev_distance != l_distance and l_prev_distance > (l_distance+3) or l_prev_distance < (l_distance-3)):
                    
                    
                    l_prev_distance = l_distance
                    message = {"ID":1,"distance":l_distance}
                    
                    deviceId = "TRASHCANAPP_001"
                    deviceType = "IOTIFY_APP"
                    
                    try:
                        # publishing the message to the Device called APP
                        pubReturn = client.publishEvent(deviceType, deviceId, "status", "json", message)
                        if pubReturn ==True:
                            logging.info("The message successfully sent")
                    except Exception  as e:
                        logging.info("The sent message Failed")
                        logging.error("The publishEvent exception httpcode :%s,message:%s,response:%s"(e.httpcode,e.message,e.response))
                
                if l_distance < criticalDistance:
                    GPIO.output(alarmOut,True)
                    if (timerFlag == 0):
                        timeList[START_TIME] = datetime.datetime.now()
                    timerFunction()
                else:
                    GPIO.output(alarmOut,False)
                    timerFlag = 0
	
    except KeyboardInterrupt: 
        GPIO.cleanup()
    except Exception as e:
        logging.error("The distanceMeasurement exception is %s,%s"%(e,type(e)))	

	

'''****************************************************************************************
Function Name   :   init()
Description     :   Function which connects to the ibmiotf service
Parameters      :   -
****************************************************************************************'''

def init():
    global client,deviceType
    organization = "c25kx4" #Your organization ID
    appId = "TRASHCAN_001"   # The Device you've created and wants to connect with
    authMethod = "apikey" #Method of authentication (the only value currently supported is apikey)
    authKey = "a-c25kx4-8jlsytrdfu" #API key (required if auth-method is apikey).
    authToken = "mK&L+ymD*pI5tzKv0s"#API key token (required if auth-method is apikey).
    deviceType = "iotify_trashcan" # The Type of the device created in your organization 
    deviceId = "TRASHCAN_001" # The Device you've created and wants to connect with                                                                                                       
    try:
        # options require for the connection
        options = {"org": organization, "id":appId, "auth-method": authMethod, "auth-key": authKey, "auth-token": authToken}
        client = ibmiotf.application.Client(options)
        client.connect()
    except ibmiotf.connectionException as e:
        logging.error("The iotfconnection Exception is %s,%s"%(e,type(e)))  


if __name__ == '__main__':
    init()
    distanceMeasurement()   