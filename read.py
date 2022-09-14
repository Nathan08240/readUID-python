#!/usr/bin/env python

from code import interact
from mfrc522 import MFRC522
from paho import mqtt
from dotenv import load_dotenv
import time
import RPi.GPIO as GPIO
import paho.mqtt.client as paho
import json
import os

load_dotenv()

BADGER_ID = "cesi/reims/2"
READER = MFRC522()
HEADER = b'CESI'
CARD_KEY = b'\xFF\xFF\xFF\xFF\xFF\xFF'
DELAY = 0.5
USERNAME = os.environ.get("USERNAME")
PASSWORD = os.environ.get("PASSWORD")
HOST = os.environ.get("HOST")
BLOCK_NUMBER = 6
CLIENT_ID = "badger_2"

PIN_BLUE_LED = 7
PIN_GREEN_LED = 11
PIN_RED_LED = 13
PIN_YELLOW_LED = 12

GPIO.setmode(GPIO.BOARD)
GPIO.setwarnings(False)

GPIO.setup(PIN_BLUE_LED, GPIO.OUT)
GPIO.setup(PIN_GREEN_LED, GPIO.OUT)
GPIO.setup(PIN_RED_LED, GPIO.OUT)
GPIO.setup(PIN_YELLOW_LED, GPIO.OUT)


def on_connect(client, userdata, flags, rc, properties=None):
    print("CONNACK received with code %s." % rc)


def on_publish(client, userdata, mid, properties=None):
    print("mid: " + str(mid))


def on_subscribe(client, userdata, mid, granted_qos, properties=None):
    print("Subscribed: " + str(mid) + " " + str(granted_qos))


def on_message(client, userdata, msg):
    payload = json.loads(msg.payload)
    checkCode(payload["code"])


client = paho.Client(client_id=CLIENT_ID, userdata=None, protocol=paho.MQTTv5)
client.on_connect = on_connect

client.tls_set(tls_version=mqtt.client.ssl.PROTOCOL_TLS)
client.username_pw_set(USERNAME, PASSWORD)
client.connect(HOST, 8883)

client.on_subscribe = on_subscribe
client.on_message = on_message
client.on_publish = on_publish

client.subscribe("api/" + BADGER_ID, qos=1)


def turnOnBlue():
    GPIO.output(PIN_GREEN_LED, GPIO.LOW)
    GPIO.output(PIN_BLUE_LED, GPIO.HIGH)
    GPIO.output(PIN_RED_LED, GPIO.LOW)
    GPIO.output(PIN_YELLOW_LED, GPIO.LOW)


def turnOnGreen(delay):
    GPIO.output(PIN_GREEN_LED, GPIO.HIGH)
    GPIO.output(PIN_BLUE_LED, GPIO.LOW)
    GPIO.output(PIN_RED_LED, GPIO.LOW)
    GPIO.output(PIN_YELLOW_LED, GPIO.LOW)
    time.sleep(delay)


def turnOnRed(delay):
    GPIO.output(PIN_GREEN_LED, GPIO.LOW)
    GPIO.output(PIN_BLUE_LED, GPIO.LOW)
    GPIO.output(PIN_RED_LED, GPIO.HIGH)
    GPIO.output(PIN_YELLOW_LED, GPIO.LOW)
    time.sleep(delay)


def turnOnYellow(delay):
    GPIO.output(PIN_GREEN_LED, GPIO.LOW)
    GPIO.output(PIN_BLUE_LED, GPIO.LOW)
    GPIO.output(PIN_RED_LED, GPIO.LOW)
    GPIO.output(PIN_YELLOW_LED, GPIO.HIGH)
    time.sleep(delay)


def turnOff(delay):
    GPIO.output(PIN_GREEN_LED, GPIO.LOW)
    GPIO.output(PIN_BLUE_LED, GPIO.LOW)
    GPIO.output(PIN_RED_LED, GPIO.LOW)
    GPIO.output(PIN_YELLOW_LED, GPIO.LOW)
    time.sleep(delay)


def checkCode(code):
    if code == 0:
        print("OK")
        turnOnGreen(1)
        turnOnBlue()
    elif code == 1:
        print("already registered")
        turnOnYellow(1)
        turnOnBlue()
    elif code == 2:
        print("Not found")
        turnOnRed(1)
        turnOnBlue()
    elif code == 3:
        print("Incorrect input")
        turnOnRed(1)
        turnOnBlue()
    else:
        print("Unknown")
        turnOnRed()
        turnOnBlue()


turnOnBlue()

try:
    while True:

        client.loop_start()
        (status, TagType) = READER.MFRC522_Request(READER.PICC_REQIDL)
        if status == READER.MI_OK:
            print("Card detected")
        else:
            client.loop_stop()
            continue
        (status, uid) = READER.MFRC522_Anticoll()
        if uid is None:
            client.loop_stop()
            continue
        if status == READER.MI_OK:
            READER.MFRC522_SelectTag(uid)
            status = READER.MFRC522_Auth(
                READER.PICC_AUTHENT1A, BLOCK_NUMBER, CARD_KEY, uid)
            if status == READER.MI_OK:
                data = READER.MFRC522_Read(BLOCK_NUMBER)
                READER.MFRC522_StopCrypto1()
                counter = 0
                for i in range(0, 4):
                    if HEADER[i] == data[i]:
                        counter += 1
                if counter != 4:
                    print("Carte invalide !")
                    continue
                student_id = ''.join([str(x) for x in data[4:11]])
                print('Student Id: %s' % student_id)
                message = json.dumps({
                    "school_student_id": student_id,
                })
                client.publish("badger/" + BADGER_ID,
                               payload=message, qos=1)
                client.loop_stop()
                time.sleep(DELAY)
            else:
                client.loop_stop()
                print("Authentication error")


except KeyboardInterrupt:
    print("Bye")
    GPIO.cleanup()

except Exception as e:
    print(e)
finally:
    GPIO.cleanup()
