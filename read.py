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
DELAY = 2

def on_connect(client, userdata, flags, rc, properties=None):
    print("CONNACK received with code %s." % rc)

def on_publish(client, userdata, mid, properties=None):
    print("mid: " + str(mid))

def on_subscribe(client, userdata, mid, granted_qos, properties=None):
    print("Subscribed: " + str(mid) + " " + str(granted_qos))

def on_message(client, userdata, msg):
    print(msg.topic + " " + str(msg.qos) + " " + str(msg.payload))

client = paho.Client(client_id="", userdata=None, protocol=paho.MQTTv5)
client.on_connect = on_connect

client.tls_set(tls_version=mqtt.client.ssl.PROTOCOL_TLS)
client.username_pw_set("your username", "your password")
client.connect("your client", 8883)

client.on_subscribe = on_subscribe
client.on_message = on_message
client.on_publish = on_publish

client.subscribe("api/" + BADGER_ID, qos=1)

try:
  while True:
    print("Place your card to read UID")
    (status, TagType) = reader.MFRC522_Request(reader.PICC_REQIDL)
    if status == reader.MI_OK:
      print("Card detected")
    (status, uid) = reader.MFRC522_Anticoll()
    if uid is None:
        continue
    if status == reader.MI_OK:
      # This is the default key for authentication
      # Select the scanned tag
      reader.MFRC522_SelectTag(uid)
      # Authenticate
      status = reader.MFRC522_Auth(reader.PICC_AUTHENT1A, 6, CARD_KEY, uid)
      # Check if authenticated
      if status == reader.MI_OK:
        data = reader.MFRC522_Read(6)
        reader.MFRC522_StopCrypto1()
        for i in range(0, 4):
          if HEADER[i] != data[i]:
            print("Card is not valid")
            time.sleep(DELAY)
            break
          else:
            student_id = ''.join([str(x) for x in data[4:9]])
            print('Student Id: %s' % student_id)
            client.loop_start()
            x = {
                "school_student_id": "202200" + student_id,
            }
            message = json.dumps(x)
            client.publish("badger/" + BADGER_ID, payload=message, qos=1)
            client.loop_stop()
            time.sleep(DELAY);
            break
      else:
        print("Authentication error")
    else:
      print("No card detected")

except KeyboardInterrupt:
  GPIO.cleanup()
  print("Bye")
except Exception as e:
  GPIO.cleanup()
  print(e)
finally:
  GPIO.cleanup()
