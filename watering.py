import threading, logging, json, os, sys
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

# Parse config file
config = {}
try:
    with open("./config.json") as f:
        config = json.loads(f.read())
except Exception as e:
    logging.error("Error: {}".format(e))
    sys.exit(1)

logging.info("config file value for key {} -> {}".format("key", config["key"]))
button_gpio = config["button_gpio"]
relay_gpio = config["relay_gpio"]
periodic_task_in_seconds = config["periodic_task_in_seconds"]

## button = GPIO 26 et GROUND
## https://projects.raspberrypi.org/en/projects/push-button-stop-motion/6
button = Button(button_gpio)
GPIO.setmode(GPIO.BCM) # Broadcom pin-numbering scheme
GPIO.setup(relay_gpio, GPIO.OUT)
GPIO.output(relay_gpio, GPIO.LOW)


def relayOnForSeconds():
    logging.info('...relay on')
    GPIO.output(relay_gpio, GPIO.LOW)
    time.sleep(1)
    logging.info('relay off...')
    GPIO.output(relay_gpio, GPIO.HIGH)

def infiniteloop1():
    while True:
        logging.info('-> Periodic task')
        relayOnForSeconds()
        sendStat()
        time.sleep(periodic_task_in_seconds)

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
