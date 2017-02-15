#!/usr/bin/python
# -*- coding: utf-8 -*-

##### CONFIGURATIONS #####

#Pins using Broadcom numbers.
RED_PIN = 17
GREEN_PIN = 22
BLUE_PIN = 24

#Speed of color change
STEPS = .1

##########################


import os
import sys
import termios
import tty
import pigpio
import time
import datetime
from thread import start_new_thread
from urllib2 import Request, urlopen, URLError 
import json
from pprint import pprint

r = 0.0
g = 0.0
b = 0.0

pi = pigpio.pi()

def setLights(pin, brightness):
	realBrightness = int(brightness)
	pi.set_PWM_dutycycle(pin, realBrightness)

setLights(RED_PIN, 0.0)
setLights(GREEN_PIN, 0.0)
setLights(BLUE_PIN, 0.0)

time.sleep(0.5)

pi.stop()
