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
#from xml.dom import minidom...used for xml

bright = 255
r = 183.0
g = 112.0
b = 38.0

brightChanged = False
abort = False
state = True

mode = 'temp'

pi = pigpio.pi()

def setLights(pin, brightness):
	realBrightness = int(int(brightness) * (float(bright) / 255.0))
	pi.set_PWM_dutycycle(pin, realBrightness)


def getCh():
	fd = sys.stdin.fileno()
	old_settings = termios.tcgetattr(fd)

	try:
		tty.setraw(fd)
		ch = sys.stdin.read(1)
	finally:
		termios.tcsetattr(fd, termios.TCSADRAIN, old_settings)
	
	tty.setcbreak(fd)
	return ch


def checkKey():
	global bright
	global brightChanged
	global state
	global abort
	global mode

	while True:
		c = getCh()
		
		if c == 't':
			mode = 'temp'
		if c == 'w':
			mode = 'weather'
		if c == 'z':
			mode = 'crazy'
		if c == 'g':
			mode = 'rgb'
		if c == 'c' and not abort:
			abort = True
			break


def checkWeather():	
	request = Request('http://api.openweathermap.org/data/2.5/weather?id=4928096&units=imperial&APPID=cbfc62062e0959c6da8eb13c6e979d28')

	try:
		response = urlopen(request)
		weatherdata = response.read()
		weather = json.loads(weatherdata)
		#pprint(weather)
		#print weather[u'main'][u'temp']
		
		if mode == 'temp':
			temp = weather[u'main'][u'temp']
			if temp < 30:
				temp = 30
			if temp > 80:
				temp = 80
			temp = temp - 30 #scale temp to 0-50
			r = 255 * float(temp / 50.0)
			g = ((1.0 - float(temp / 50.0)) * 80) + 20
			b = 255 - r
			print (r)
			print (g)
			print (b)
	
		if mode == 'weather':
			condition = 0
		
		setLights(RED_PIN, r)
		setLights(GREEN_PIN, g)
		setLights(BLUE_PIN, b)	
		
	except URLError, e:
		print 'Error: no weather information obtained: ', e
	

start_new_thread(checkKey, ())

print ('c = Abort Program')

setLights(RED_PIN, r)
setLights(GREEN_PIN, g)
setLights(BLUE_PIN, b)

checkWeather()

print (r)
print (g)
print (b)

elapsedtime = datetime.datetime.now()

while abort == False:
	newtime = datetime.datetime.now()
	deltatime = newtime - elapsedtime
	if mode == 'temp' or mode == 'weather':
		if deltatime > datetime.timedelta(seconds=30):
			print "Check weather"
			checkWeather()
			elapsedtime = datetime.datetime.now()

print ("Aborting...")

setLights(RED_PIN, 0)
setLights(GREEN_PIN, 0)
setLights(BLUE_PIN, 0)

time.sleep(0.5)

pi.stop()
