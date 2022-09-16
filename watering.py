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
    with open("/home/pi/growlab-watering/config.json") as configFile:
        config = json.loads(configFile.read())
except Exception as e:
    logging.error("Error: {}".format(e))
    sys.exit(1)


def relayOnForSeconds(name, relay_gpio):
    logging.info("{} ...relay on".format(name))
    GPIO.output(relay_gpio, GPIO.LOW)
    time.sleep(1)
    logging.info("{} relay off...".format(name))
    GPIO.output(relay_gpio, GPIO.HIGH)

def infiniteloop1(name, relay_gpio, periodic_task_in_seconds):
    while True:
        logging.info('-> Periodic task')
        relayOnForSeconds(name, relay_gpio)
        sendStat(name)
        time.sleep(periodic_task_in_seconds)

def infiniteloop2(name, relay_gpio, button):
    while True:
        try:
            button.wait_for_press()
            logging.info('-> Button pushed')
            relayOnForSeconds(name, relay_gpio)
            sendStat(name)
            
        except KeyboardInterrupt:
            break

def sendStat(name):
    statServerUrl = config["stat"]["url"]

    data = {"location":"growlab","table":[{"key":"watering","value":"1"}, {"key":"name","value":name}]}
    logging.info("request: {} {}".format(statServerUrl, data))

    try:
        x = requests.post(statServerUrl, json.dumps(data))
    except Exception as e:
        logging.error("Error: {}".format(e))

    #print the response text (the content of the requested file):
    logging.info("response: {}".format(x.text))


for pump in config["pumps"]:
    
    print (pump["id"])

    name = pump["name"]
    button_gpio = pump["button_gpio"]
    relay_gpio = pump["relay_gpio"]
    periodic_task_in_seconds = pump["periodic_task_in_seconds"]

    logging.info("--- Reading configuration file for {} ---".format(name))
    logging.info("Button GPIO {}".format(button_gpio))
    logging.info("Relay  GPIO {}".format(relay_gpio))
    logging.info("Periodic task {} seconds".format(periodic_task_in_seconds))

    ## button = GPIO 26 et GROUND
    ## https://projects.raspberrypi.org/en/projects/push-button-stop-motion/6
    button = Button(button_gpio)
    GPIO.setmode(GPIO.BCM) # Broadcom pin-numbering scheme
    GPIO.setup(relay_gpio, GPIO.OUT, initial=GPIO.HIGH)

    thread1 = threading.Thread(target=infiniteloop1, args=(name, relay_gpio, periodic_task_in_seconds))
    thread1.start()

    thread2 = threading.Thread(target=infiniteloop2, args=(name, relay_gpio, button))
    thread2.start()

