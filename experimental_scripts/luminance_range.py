
import os,numpy,sys,random,datetime,operator
from psychopy import visual,core,event,monitors,info,gui
from pandas import read_csv, DataFrame
from psychopy.tools.colorspacetools import rgb2dklCart, dkl2rgb
import numpy as np
from random import shuffle


#eyetracking
import pylink
from EyeLinkCoreGraphicsPsychoPy import EyeLinkCoreGraphicsPsychoPy
from PIL import Image

dummyMode = False # Simulated connection to the tracker; press ESCAPE to skip calibration/validation

# establish a link to the tracker
if not dummyMode:
    tk = pylink.EyeLink('100.1.1.1')
else:
    tk = pylink.EyeLink(None)


parent_directory = os.path.dirname(os.getcwd())

exp_param_directory = parent_directory + '/experimental_parameters/'
data_directory = parent_directory + '/data/BIDS/'


current_time = datetime.datetime.today().strftime("%m%d%Y_%H%M%S")
user_input_dict = { 'CoAx ID [####]': '', 'Session Number [#]': '',
 'Condition [####] (probability-lambda; e.g., 6510)': '' }
sub_inf_dlg = gui.DlgFromDict(user_input_dict, title='Subject information',
show=0, order=[ 'CoAx ID [####]','Session Number [#]',
'Condition [####] (probability-lambda; e.g., 6510)'])


sub_inf_dlg.show()
subj_id = int(float(user_input_dict['CoAx ID [####]']))
session_n = int(float(user_input_dict['Session Number [#]']))
condition = int(float(user_input_dict['Condition [####] (probability-lambda; e.g., 6510)'])) #condition is coded as prob-lambda [65-10]


subj_directory = data_directory + "sub-" + "{:04d}".format(subj_id) + "/"
session_directory = subj_directory + "ses-" + "{:02d}".format(session_n) + "/"

edf_directory = session_directory + "pupil/"

directories = list([edf_directory])

for dir in directories:
    if not os.path.exists(dir):
        os.makedirs(dir)


output_file_name = (
    "sub-"
    + "{:04d}".format(subj_id)
    + "_"
    + "sess"
    + "{:02d}".format(session_n)
    + "_"
    + "lum-"
    + "lokicat"
    + "_"
    + str(current_time)
)


#eyetracking data
edf_output_file_name = str(subj_id) + 'lum' + str(session_n) #can only be 8 characters

dataFileName = edf_output_file_name + '.EDF'
tk.openDataFile(dataFileName)

tk.sendCommand("add_file_preamble_text " + str(output_file_name))



colors_file = exp_param_directory + 'sinusoidal_colors.csv'
print(colors_file)

if not os.path.exists(colors_file):
    sys.exit("Experimental parameter file does not exist.")

colors = read_csv(colors_file, header=0)
colors.columns = colors.columns.str.strip()

colors_list = colors.color.tolist()

screen_size = (1920., 1080.)  # screen size in pixels
window_size = (1280., 800.)
mon = monitors.Monitor(
    "BOLD_display", width=79.7, distance=138,
)  # width and distance in cm
mon.setSizePix(screen_size)
mon.saveMon()

center = (0,0)



rgb_window = visual.Window(size = screen_size, units='pix', monitor = mon, color = [-1,-1,-1], \
       colorSpace = 'rgb', blendMode = 'avg', useFBO = True, allowGUI = \
       False,fullscr=False, pos=center, screen=1)


fixation_cross = visual.TextStim(win=rgb_window,units='pix',text='+', antialias='False',pos=[0,15], colorSpace='rgb', color=[-1,-1,-1], height=screen_size[0]/15)

wait_interval = 1 #latency of 220-500 ms, Ellis (1981). also went back to default between stimuli.

genv = EyeLinkCoreGraphicsPsychoPy(tk, rgb_window)
pylink.openGraphicsEx(genv)

tk.setOfflineMode() #need to set tracker in offline mode before changing config.
# sampling rate, 250, 500, 1000, or 2000; this command won't work for EyeLInk II/I
tk.sendCommand('sample_rate 1000')

# inform the tracker the resolution of the subject display
# [see Eyelink Installation Guide, Section 8.4: Customizing Your PHYSICAL.INI Settings ]
tk.sendCommand("screen_pixel_coords = 0 0 %d %d" % (screen_size[0]-1, screen_size[1]-1))

# save display resolution in EDF data file for Data Viewer integration purposes
# [see Data Viewer User Manual, Section 7: Protocol for EyeLink Data to Viewer Integration]
tk.sendMessage("DISPLAY_COORDS = 0 0 %d %d" % (screen_size[0]-1, screen_size[1]-1))

# specify the calibration type, H3, HV3, HV5, HV13 (HV = horiz./vertical),
tk.sendCommand("calibration_type = HV5") # tk.setCalibrationType('HV9') also works, see the Pylink manual

# the model of the tracker, 1-EyeLink I, 2-EyeLink II, 3-Newer models (100/1000Plus/DUO)
eyelinkVer = tk.getTrackerVersion()


#turn off scenelink camera stuff (EyeLink II/I only)
if eyelinkVer == 2: tk.sendCommand("scene_camera_gazemap = NO")

# Set the tracker to parse Events using "GAZE" (or "HREF") data
tk.sendCommand("recording_parse_type = GAZE")

# Online parser configuration: 0-> standard/coginitve, 1-> sensitive/psychophysiological
# the Parser for EyeLink I is more conservative, see below
# [see Eyelink User Manual, Section 4.3: EyeLink Parser Configuration]
if eyelinkVer>=2: tk.sendCommand('select_parser_configuration 0')

# get Host tracking software version
hostVer = 0
if eyelinkVer == 3:
    tvstr  = tk.getTrackerVersionString()
    vindex = tvstr.find("EYELINK CL")
    hostVer = int(float(tvstr[(vindex + len("EYELINK CL")):].strip()))


# specify the EVENT and SAMPLE data that are stored in EDF or retrievable from the Link
# See Section 4 Data Files of the EyeLink user manual
tk.sendCommand("file_event_filter = LEFT,FIXATION,SACCADE,BLINK,MESSAGE,BUTTON,INPUT")
tk.sendCommand("link_event_filter = LEFT,FIXATION,FIXUPDATE,SACCADE,BLINK,BUTTON,INPUT")
if hostVer>=4:
    tk.sendCommand("file_sample_data  = LEFT,GAZE,AREA,GAZERES,STATUS,HTARGET,INPUT")
    tk.sendCommand("link_sample_data  = LEFT,GAZE,GAZERES,AREA,STATUS,HTARGET,INPUT")
else:
    tk.sendCommand("file_sample_data  = LEFT,GAZE,AREA,GAZERES,STATUS,INPUT")
    tk.sendCommand("link_sample_data  = LEFT,GAZE,GAZERES,AREA,STATUS,INPUT")


tk.setPupilSizeDiameter("YES")  #get pupil diameter, not area

# show some instructions here.
msg = visual.TextStim(rgb_window, text = 'Press ENTER to calibrate the tracker.')
msg.draw()
rgb_window.flip()
event.waitKeys()

# set up the camera and calibrate the tracker at the beginning of each block
tk.doTrackerSetup()

# start recording, parameters specify whether events and samples are
# stored in file, and available over the link
error = tk.startRecording(1,1,1,1)
pylink.pumpDelay(100) # wait for 100 ms to make sure data of interest is recorded

#determine which eye(s) are available
eyeTracked = tk.eyeAvailable()
if eyeTracked==2: eyeTracked = 1




left_key = "2"
right_key = "1"
inst_key = left_key

escape_key = 'escape'

instructions = ("Now we are going to test the range of your pupillary response. During this task, simply focus on the cross at the center of the screen. \n\nPress the left button when you are ready to start.")
inst_msg = visual.TextStim(win=rgb_window, units='pix',antialias='False',colorSpace='rgb', color=[1,1,1], wrapWidth=screen_size[0]-400, height=screen_size[1]/32)

#give instructions
instruction_phase = True
while instruction_phase:
    inst_msg.text = instructions
    inst_msg.setAutoDraw(True)
    rgb_window.flip()
    inst_keys = event.waitKeys(keyList=[inst_key, escape_key])
    if escape_key in inst_keys:
        sys.exit('escape key pressed.')
    instruction_phase = False

inst_msg.setAutoDraw(False)
rgb_window.flip()


for color in range(len(colors)):
    tk.sendMessage('trial_start')
    tk.sendMessage('TRIALID') #this is a parsing signal for the proprietary data viewer
    fixation_cross.setAutoDraw(True)
    rgb_window.flip()
    tk.sendMessage('stim_onset')
    rgb_window.setColor(np.repeat(colors_list[color],3)) #list, repeat to form rgb vector
    rgb_window.flip()
    core.wait(wait_interval)
    tk.sendMessage('stim_offset')
    keys = event.getKeys(keyList=[escape_key, inst_key])
    if escape_key in keys:
        sys.exit('escape key pressed.')
    tk.sendMessage('TRIAL_RESULT') #this is a parsing signal for the proprietary data viewer
    tk.sendMessage('trial_end') #this is a parsing signal for the proprietary data viewer


fixation_cross.setAutoDraw(False)
pylink.pumpDelay(100)
tk.stopRecording() # stop recording


# close the EDF data file
tk.setOfflineMode()
tk.closeDataFile()
pylink.pumpDelay(50)


rgb_window.color = [-1,-1,-1]
rgb_window.flip()
# Get the EDF data and say goodbye
msg.text='Data transferring.....'
msg.draw()
rgb_window.flip()
tk.receiveDataFile(dataFileName, edf_directory + dataFileName)
core.wait(2)
#close the link to the tracker
tk.close()

# close the graphics
pylink.closeGraphics()
rgb_window.close()
core.quit()
