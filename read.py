#!/usr/bin/env python

import time
import RPi.GPIO as GPIO
from mfrc522 import MFRC522

reader = MFRC522()
HEADER = b'CESI'
CARD_KEY = b'\xFF\xFF\xFF\xFF\xFF\xFF'
DELAY = 2


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
            break
        student_id = ''.join([str(x) for x in data[4:9]])
        print('Student Id: %s' % student_id)
        time.sleep(DELAY);
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