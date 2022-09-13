#!/usr/bin/env python

import time
import RPi.GPIO as GPIO
from mfrc522 import MFRC522
import paho.mqtt.client as paho
import json
from paho import mqtt

BADGER_ID = "cesi/reims/1"
reader = MFRC522()
HEADER = b'CESI'
CARD_KEY = b'\xFF\xFF\xFF\xFF\xFF\xFF'
DELAY = 0.5
USERNAME = ""
PASSWORD = ""
HOST = ""
BLOCK_NUMBER = 6

GPIO.setwarnings(False)


def on_connect(client, userdata, flags, rc, properties=None):
    print("CONNACK received with code %s." % rc)


def on_publish(client, userdata, mid, properties=None):
    print("mid: " + str(mid))


def on_subscribe(client, userdata, mid, granted_qos, properties=None):
    print("Subscribed: " + str(mid) + " " + str(granted_qos))


def on_message(client, userdata, msg):
    print(msg.topic + " " + str(msg.qos) + " " + str(msg.payload))


client = paho.Client(client_id="badger_1", userdata=None, protocol=paho.MQTTv5)
client.on_connect = on_connect

client.tls_set(tls_version=mqtt.client.ssl.PROTOCOL_TLS)
client.username_pw_set(USERNAME, PASSWORD)
client.connect(HOST, 8883)

client.on_subscribe = on_subscribe
client.on_message = on_message
client.on_publish = on_publish

client.subscribe("api/" + BADGER_ID, qos=1)
print("Place your card to read UID")


try:
    while True:
        client.loop_start()
        (status, TagType) = reader.MFRC522_Request(reader.PICC_REQIDL)
        if status == reader.MI_OK:
            print("Card detected")
        (status, uid) = reader.MFRC522_Anticoll()
        if uid is None:
            time.sleep(DELAY)
            continue
        if status == reader.MI_OK:
            # This is the default key for authentication
            # Select the scanned tag
            reader.MFRC522_SelectTag(uid)
            # Authenticate
            status = reader.MFRC522_Auth(
                reader.PICC_AUTHENT1A, BLOCK_NUMBER, CARD_KEY, uid)
            # Check if authenticated
            if status == reader.MI_OK:
                data = reader.MFRC522_Read(BLOCK_NUMBER)
                reader.MFRC522_StopCrypto1()
                # if HEADER != data[0:3]:
                #     print("Card is not valid")
                #     continue
                student_id = ''.join([str(x) for x in data[4:11]])
                print('Student Id: %s' % student_id)
                message = json.dumps({
                    "school_student_id": student_id,
                })
                client.publish("badger/" + BADGER_ID,
                               payload=message, qos=1)
                time.sleep(DELAY)
            client.loop_stop()


except KeyboardInterrupt:
    print("Bye")
    GPIO.cleanup()

except Exception as e:
    print(e)
finally:
    GPIO.cleanup()
