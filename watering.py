import threading, logging, json
import pytz, requests
import RPi.GPIO as GPIO
import time
from gpiozero import Button
from datetime import datetime


logging.basicConfig(filename='/home/pi/growlab-watering/watering.log', level=logging.INFO, format='%(asctime)s %(message)s')
logging.getLogger("watering")

print("-----------")
logging.info("================")
logging.info("Starting watering tool")
logging.info("================")


## button = GPIO 26 et GROUND
## https://projects.raspberrypi.org/en/projects/push-button-stop-motion/6
button = Button(26)
GPIO.setmode(GPIO.BCM) # Broadcom pin-numbering scheme
GPIO.setup(23, GPIO.OUT)
GPIO.output(23, GPIO.LOW)


def relayOnForSeconds():
    logging.info('...relay on')
    GPIO.output(23, GPIO.LOW)
    time.sleep(1)
    logging.info('relay off...')
    GPIO.output(23, GPIO.HIGH)

def infiniteloop1():
    while True:
        logging.info('-> Periodic task')
        relayOnForSeconds()
        sendStat()
        time.sleep(86400)

def infiniteloop2():
    while True:
        try:
            button.wait_for_press()
            logging.info('-> Button pushed')
            relayOnForSeconds()
            sendStat()
            
        except KeyboardInterrupt:
            break

def sendStat():
    data = {"location":"growlab","table":[{"key":"watering","value":"1"}]}
    logging.info("request: {} {}".format("http://homedata:5000/generic", data))

    try:
        x = requests.post("http://homedata:5000/generic", json.dumps(data))
    except Exception as e:
        logging.error("Error: {}".format(e))

    #print the response text (the content of the requested file):
    logging.info("response: {}".format(x.text))

thread1 = threading.Thread(target=infiniteloop1)
thread1.start()

thread2 = threading.Thread(target=infiniteloop2)
thread2.start()
