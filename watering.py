from http.server import BaseHTTPRequestHandler, HTTPServer
import threading, logging, json, os, sys
import pytz, requests
import RPi.GPIO as GPIO
import time
from gpiozero import Button
from datetime import datetime
from urllib.parse import urlparse, parse_qs


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

def start_server():
    port = config["server"]["port"]
    logging.info("--- Start server on port {} ---".format(port))
    
    server_address = ('', port)
    httpd = HTTPServer(server_address, RequestHandler)
    httpd.serve_forever()

class RequestHandler(BaseHTTPRequestHandler):
    def do_GET(self):
        parsed_path = urlparse(self.path)
        query_params = parse_qs(parsed_path.query)

        if parsed_path.path == '/api/watering' and 'pump' in query_params:
            pump_param = query_params['pump'][0]
            pump_number = int(pump_param)
            name = config["pumps"][pump_number]["name"]
            relay_gpio = config["pumps"][pump_number]["relay_gpio"]
            duration = config["pumps"][pump_number]["duration"]
            logging.info("{} -> API call".format(name))
            
            relayOnForSeconds(name, relay_gpio, duration)

            self.send_response(200)
            self.send_header('Content-type', 'application/json')
            self.end_headers()
            self.wfile.write(json.dumps({'message': 'Watering started for pump {}'.format(pump_number)}).encode('utf-8'))
        else:
            self.send_response(400)
            self.send_header('Content-type', 'application/json')
            self.end_headers()
            self.wfile.write(json.dumps({'error': 'Invalid request. Please provide pump number in query parameter. Ex: /api/watering?pump=2'}).encode('utf-8'))


def relayOnForSeconds(name, relay_gpio, duration):
    logging.info("{} ...relay on".format(name))
    GPIO.output(relay_gpio, GPIO.LOW)
    time.sleep(duration)
    logging.info("{} relay off...".format(name))
    GPIO.output(relay_gpio, GPIO.HIGH)

def infiniteloop1(name, relay_gpio, periodic_task_in_seconds, duration):
    while True:
        logging.info("{} -> Periodic task".format(name))
        relayOnForSeconds(name, relay_gpio, duration)
        time.sleep(periodic_task_in_seconds)

def infiniteloop2(name, relay_gpio, button, duration):
    while True:
        try:
            button.wait_for_press()
            logging.info("{} -> Button pushed".format(name))
            relayOnForSeconds(name, relay_gpio, duration)
            
        except KeyboardInterrupt:
            break


for pump in config["pumps"]:
    
    name = pump["name"]
    button_gpio = pump["button_gpio"]
    relay_gpio = pump["relay_gpio"]
    duration = pump["duration"]
    periodic_task_in_seconds = pump["periodic_task_in_seconds"]

    logging.info("--- Reading configuration file for {} ---".format(name))
    logging.info("{} Button GPIO {}".format(name, button_gpio))
    logging.info("{} Relay  GPIO {}".format(name, relay_gpio))
    logging.info("{} Watering duration {} sec".format(name, duration))
    logging.info("{} Periodic task {} seconds".format(name, periodic_task_in_seconds))

    ## button = GPIO 26 et GROUND
    ## https://projects.raspberrypi.org/en/projects/push-button-stop-motion/6
    button = Button(button_gpio)
    GPIO.setmode(GPIO.BCM) # Broadcom pin-numbering scheme
    GPIO.setup(relay_gpio, GPIO.OUT, initial=GPIO.HIGH)

    thread1 = threading.Thread(target=infiniteloop1, args=(name, relay_gpio, periodic_task_in_seconds, duration))
    thread1.start()

    thread2 = threading.Thread(target=infiniteloop2, args=(name, relay_gpio, button, duration))
    thread2.start()

if config["server"]["isActive"] == True:
    server_thread = threading.Thread(target=start_server)
    server_thread.start()
else:
    logging.info("--- Server feature is disabled ---")
