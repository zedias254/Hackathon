from pirc522 import RFID
import RPi.GPIO as GPIO
import time
import requests


GPIO.setwarnings(False)
rdr = RFID()
GPIO.setup(37, GPIO.OUT)
GPIO.setup(35, GPIO.OUT)
GPIO.output(37, 0)
GPIO.output(35, 0)

outlet_allowed  = [[89, 108, 10, 187, 132]] # [6, 82, 243, 147, 52]
outlet_previous = []
outlet_plugged  = False

while True:
	rdr.wait_for_tag()
	error, tag_type = rdr.request()
	if not error:
		error, uid = rdr.anticoll()
		if not error and uid != outlet_previous:
			print("Outlet detected!")
			outlet_previous = uid
			if uid in outlet_allowed:
				if not outlet_plugged:
					r = requests.post("http://charge-it-161217.appspot.com/newcharge/" +  "1")
					print(r.status_code, r.reason)
					if (r.text == "OK"):
						print("Outlet accepted! ID: " + str(uid))
						GPIO.output(37, 1)
						outlet_plugged = True
			else:
				print("Outlet denied!   ID: " + str(uid))
				GPIO.output(35, 1)
				outlet_plugged = False
		elif error: # bad tag reading
			if outlet_previous in outlet_allowed:
				r = requests.post("http://charge-it-161217.appspot.com/newcharge/" +  "1")
			else:
				r = requests.post("http://charge-it-161217.appspot.com/newcharge/" +  "2")
			GPIO.output(37, 0)
			GPIO.output(35, 0)
			outlet_plugged  = False
			outlet_previous = []
	else: # no tag found
		if outlet_previous in outlet_allowed:
			r = requests.post("http://charge-it-161217.appspot.com/newcharge/" +  "1")
		else:
			r = requests.post("http://charge-it-161217.appspot.com/newcharge/" +  "2")
		GPIO.output(37, 0)
		GPIO.output(35, 0)
		outlet_plugged  = False
		outlet_previous = []

rdr.cleanup()
