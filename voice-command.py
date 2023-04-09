import fauxmo
import logging
import time
import os
import subprocess
import signal
import urllib2

from debounce_handler import debounce_handler

logging.basicConfig(level=logging.DEBUG)

cloudpid = 0
mode = "";

class device_handler(debounce_handler):
    """Publishes the on/off state requested,
       and the IP address of the Echo making the request.
    """

    TRIGGERS = {"cloud": 52000, "rgb": 52001, "fade": 52002, "slow fade": 52003}

    def act(self, client_address, state, name):
	global cloudpid
	global mode
        print "State", state, "on ", name, "from client @", client_address
	if name == "cloud":
		if state:
			print "\n-----Cloud Activated-----\n"
			os.system("sudo pigpiod")
			proc = subprocess.Popen(['node', 'index.js'], shell=False)
			time.sleep(3)
			cloudpid = proc.pid
			mode = "off"
		else:
			response = urllib2.urlopen('http://10.0.0.7:5000/led?mode=off')
			time.sleep(5)
			os.kill(cloudpid, signal.SIGTERM)
			cloudpid = 0
			mode = "off"
			print "\n-----Cloud Deactivated-----\n"
	elif name == "rgb" and cloudpid != 0:
		if state and mode != "rgb":
			response = urllib2.urlopen('http://10.0.0.7:5000/led?mode=rgb')
			mode = "rgb"
		elif not state and mode == "rgb":
			response = urllib2.urlopen('http://10.0.0.7:5000/led?mode=off')
			mode = "off"
			
	elif name == "fade" and cloudpid != 0:
		if state and mode != "fade":
			response = urllib2.urlopen('http://10.0.0.7:5000/led?mode=fading')
			mode = "fade"
		elif not state and mode == "fade":
			response = urllib2.urlopen('http://10.0.0.7:5000/led?mode=off')
			mode = "off"
	elif name == "slow fade" and cloudpid != 0:
		if state and mode != "fadeslow":
			response = urllib2.urlopen('http://10.0.0.7:5000/led?mode=fadingslow')
			mode = "fadeslow"
		elif not state and mode == "fadeslow":
			response = urllib2.urlopen('http://10.0.0.7:5000/led?mode=off')
			mode = "off"
        return True

if __name__ == "__main__":
    # Startup the fauxmo server
    fauxmo.DEBUG = True
    p = fauxmo.poller()
    u = fauxmo.upnp_broadcast_responder()
    u.init_socket()
    p.add(u)

    # Register the device callback as a fauxmo handler
    d = device_handler()
    for trig, port in d.TRIGGERS.items():
        fauxmo.fauxmo(trig, u, p, None, port, d)

    # Loop and poll for incoming Echo requests
    logging.debug("Entering fauxmo polling loop")
    while True:
        try:
            # Allow time for a ctrl-c to stop the process
            p.poll(100)
            time.sleep(0.1)
        except Exception, e:
            logging.critical("Critical exception: " + str(e))
            break
