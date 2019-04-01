from constants import *
from pygaze import libtime
from pygaze.libscreen import Display, Screen
from pygaze.eyetracker import EyeTracker
from pygaze.libinput import Keyboard
from pygaze.liblog import Logfile
from pygaze.libgazecon import FRL

# timing and initialization
libtime.expstart()

# visuals
disp = Display()
scr = Screen()

# eye tracking
tracker = EyeTracker(disp)
frl = FRL(pos='center', dist=125, size=200)

# input collection and storage
kb = Keyboard(keylist=['escape','space'], timeout=None)
log = Logfile()
log.write(["trialnr", "trialstart", "trialend", "duration", "image"])

# run trials
tracker.calibrate()
for trialnr in range(0,len(IMAGES)):
	# blank display
	disp.fill()
	disp.show()
	libtime.pause(1000)
	# prepare stimulus
	scr.clear()
	scr.draw_image(IMAGES[trialnr])
	# start recording eye movements
	tracker.drift_correction()
	tracker.start_recording()
	tracker.status_msg("trial %d" % trialnr)
	tracker.log("start trial %d" % trialnr)
	# present stimulus
	response = None
	trialstart = libtime.get_time()
	while not response:
		gazepos = tracker.sample()
		frl.update(disp, scr, gazepos)
		response, presstime = kb.get_key(timeout=1)
	# stop tracking and process input
	tracker.stop_recording()
	tracker.log("stop trial %d" % trialnr)
	log.write([trialnr, trialstart, presstime, presstime-trialstart, IMAGES[trialnr]])

# close experiment
log.close()
tracker.close()
disp.close()
libtime.expend()
