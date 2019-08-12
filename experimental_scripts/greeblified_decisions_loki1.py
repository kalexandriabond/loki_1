import os, sys, random, datetime, operator
from psychopy import visual, core, event, monitors, info, gui
from pandas import read_csv, DataFrame
from psychopy.tools.colorspacetools import rgb2dklCart
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


current_time = datetime.datetime.today().strftime("%m%d%Y_%H%M%S")

user_input_dict = {
    "CoAx ID [####]": "",
    "Session [##] (01-11)": "",
    "Reward Code [#]": "",
    "Condition [####] (e.g., 6510)": "",
    "Run [#] (01-05)": "",
}
sub_inf_dlg = gui.DlgFromDict(
    user_input_dict,
    title="Subject information",
    show=0,
    order=[
        "CoAx ID [####]",
        "Session [##] (01-11)",
        "Reward Code [#]",
        "Condition [####] (e.g., 6510)",
        "Run [#] (01-05)",
    ],
)

# set data path & collect information from experimenter
testing = int(input("Testing? "))

if testing is not 1 and testing is not 0:
    sys.exit("Enter 0 or 1.")

parent_directory = os.path.dirname(os.getcwd())

image_directory = parent_directory + "/images/"
exp_param_directory = parent_directory + "/experimental_parameters/reward_parameters/"
data_directory = parent_directory + "/data/BIDS/"
run_info_directory = parent_directory + "/data/run_info_data/"

# deterministic_exp_param_directory = os.getcwd() + '/experimental_parameters/deterministic_schedules/'

sub_inf_dlg.show()
subj_id = int(float(user_input_dict["CoAx ID [####]"]))
session_n = int(float(user_input_dict["Session [##] (01-11)"]))
reward_code = int(float(user_input_dict["Reward Code [#]"]))
condition = int(float(user_input_dict["Condition [####] (e.g., 6510)"]))  # condition is coded as prob-lambda [6510]
run = int(float(user_input_dict["Run [#] (01-05)"]))


subj_directory = data_directory + "sub-" + "{:04d}".format(subj_id) + "/"
session_directory = subj_directory + "ses-" + "{:02d}".format(session_n) + "/"

behavioral_directory = session_directory + "beh/"
func_directory = session_directory + "func/"
edf_directory = session_directory + "pupil/"

directories = list([behavioral_directory, edf_directory, func_directory])

for dir in directories:
    if not os.path.exists(dir):
        os.makedirs(dir)

exp_param_file = (
    exp_param_directory
    + str(subj_id)
    + "_"
    + "reward"
    + str(reward_code)
    + "_"
    + "cond"
    + str(condition)
    + "_"
    + "run"
    + str(run)
    + ".csv"
)

if not os.path.exists(exp_param_file):
    sys.exit("Experimental parameter file does not exist.")

output_file_name = (
    "sub-"
    + "{:04d}".format(subj_id)
    + "_"
    + "sess"
    + "{:02d}".format(session_n)
    + "_"
    + "bold-task-"
    + "lokicat"
    + "_"
    + "run"
    + "{:02d}".format(run)
    + "_"
    + str(current_time)
)

if testing:
    output_file_name = output_file_name + '_test'

# error checking for user input

n_sessions = 11
n_runs = 5

print(str(subj_id), str(run), str(session_n))

try:

    assert len(str(subj_id)) == 3

    assert len(str(run)) == 1
    assert run > 0 & run < (n_runs + 1)

    assert len(str(session_n)) <= 2
    assert session_n > 0 & session_n < (n_sessions + 1)


except AssertionError:
    sys.exit(
        "Format failure. Subject ID should be 4 digits, session number should be 1:11,\
         and run number should be 1:5."
    )


output_path_beh = behavioral_directory + output_file_name + ".json"
output_path_readable_beh = behavioral_directory + output_file_name + ".tsv"

run_info_path = run_info_directory + output_file_name + "_runInfo.csv"
output_path_events = func_directory + output_file_name + "_events.tsv"


if not testing and os.path.exists(output_path_readable_beh):
    sys.exit(output_file_name + " already exists! Overwrite danger...Exiting.")


edf_output_file_name = str(subj_id) + str(condition) + str(run) # can only be 8 characters
output_path_edf = edf_directory + edf_output_file_name


# create an eye-tracking data (EDF) folder
if not os.path.exists(edf_directory):
    os.makedirs(edf_directory)

dataFileName = edf_output_file_name + ".EDF"
tk.openDataFile(dataFileName)

tk.sendCommand("add_file_preamble_text " + str(output_file_name))

# specify constants
exp_param = read_csv(exp_param_file, header=0)
# strip whitespace from column names
exp_param.columns = exp_param.columns.str.strip()

reward_t0 = np.round(exp_param.r_t0.values, 2).astype("int")
reward_t1 = np.round(exp_param.r_t1.values, 2).astype("int")


rewards = np.transpose(np.array([reward_t0, reward_t1]))
max_reward_idx = np.argmax(rewards, 1)
min_reward_idx = np.argmin(rewards, 1)
n_trials = len(exp_param.cp)
epoch_length = exp_param.epoch_length.tolist()
epoch_trial = exp_param.epoch_trial.tolist()
epoch_number = exp_param.epoch_number.tolist()

f_image = exp_param.f_image.tolist()
m_image = exp_param.m_image.tolist()


run_test_trials = 80


n_test_trials = run_test_trials  # needs to be divisible by 2

if testing:
    n_trials = n_test_trials


print("n_trials: ", n_trials)

trial_list = list(np.arange(0, n_trials))

total_reward = n_trials // 2
response_failure_reward = -5

vertical_txt_break = "\n" * 10
small_vertical_txt_break = "\n" * 2
horiz_txt_break = "\t" * 5

instructions_p1 = (
    "You are going on a treasure hunt! You will start with "
    + str(total_reward)
    + " coins, and you will be able to pay a coin "
    + "to ask one of two greebles if they have money. On each trial you will meet two greebles: one is female, one is male."
    + small_vertical_txt_break
    + "This is a female."
    + horiz_txt_break
    + "This is a male."
    + vertical_txt_break
    + "Note how their features differ. The female greeble has a downward facing appendage, whereas the male greeble has an upward facing appendage.\n\nPress the left button when you're ready to continue to the next instruction screen.  "
)

instructions_p2 = (
    "On each trial you can ask either the male or female greeble for money. If the greeble you ask chooses to give you money, "
    + "he or she will give you a certain number of coins to add to your bank.\n\nSometimes females will give coins more often. Sometimes males will give coins more often. "
    + "Your goal is simply to make as much money as possible by learning which type of greeble will give you more money. "
)

instructions_p3 = (
    "The total amount of money that you have is shown as a bank at the center of the screen:"
    + small_vertical_txt_break * 7
    + "If you earn money, the bank will turn green. "
    + "If you lose money, the bank will turn yellow.\n\nIf you choose too slowly or too quickly, you will lose 5 points and the bank at the center of the screen will turn red.\n\nEach point you earn will correspond to one real cent that you will be paid in addition to your hourly pay. So do the best you can!"
)


instructions_p4 = (
    "To ask the left greeble for money, press the left button with your left thumb. "
    + "To ask the right greeble for money press the right button with your right thumb.\n\n"
    + "Between trials, please focus your eyes on the bank.\n\nPress the left button when you are ready to begin the hunt!"
)


instructions_p5 = (
    "Do your best to focus on the bank. Press the left button to start the task."
)


slow_trial = "Too slow! \nChoose quickly."
fast_trial = "Too fast! \nSlow down."
between_run_inst = (
    "Feel free to take a break! \nPress the left button when you're ready to continue."
)


# initialize dependent variables
rt_list = []
LR_choice_list = []
id_choice_list = []
value_accuracy_list = []
p_accuracy_list = []

subj_id_list = [subj_id] * n_trials
reward_code_list = [reward_code] * n_trials
condition_list = [condition] * n_trials
run_list = [run] * n_trials

# instantiate psychopy object instances
expTime_clock = core.Clock()
trialTime_clock = core.Clock()
rt_clock = core.Clock()

screen_size = (1920., 1080.)  # screen size in pixels
window_size = (1280., 800.)
mon = monitors.Monitor(
    "BOLD_display", width=79.7, distance=138,
)  # width and distance in cm
mon.setSizePix(screen_size)
mon.saveMon()


center = (0,0)

luminance = 10
contrast = 1

dkl_purple = (luminance, 300, contrast)
dkl_red = (luminance, 45, contrast)
dkl_gray = (luminance, 0, 0)
dkl_green = (luminance, 145, contrast)
dkl_orange = (luminance, 45, contrast)
dkl_yellow = (luminance, 80, contrast)

dkl_blue = (luminance, 225, contrast)


greeble_color = dkl_purple
inst_color = [1, 1, 1]
speed_message_color = dkl_red

window = visual.Window(
    size=screen_size,
    units="pix",
    monitor=mon,
    color=dkl_blue,
    colorSpace="dkl",
    blendMode="avg",
    useFBO=True,
    allowGUI=False,
    fullscr=False,
    pos=center,
    screen=1,
)

break_msg = visual.TextStim(
    win=window,
    units="pix",
    antialias="False",
    text=between_run_inst,
    wrapWidth=window_size[0] - 400,
    height=window_size[1] / 32,
)
inst_msg = visual.TextStim(
    win=window,
    units="pix",
    antialias="False",
    colorSpace="dkl",
    color=[90, 0, 1],
    wrapWidth=window_size[0] - 400,
    height=window_size[1] / 28,
)
end_msg = visual.TextStim(
    win=window,
    units="pix",
    antialias="False",
    wrapWidth=window_size[0] - 400,
    colorSpace="dkl",
    color=[90, 0, 1],
    height=window_size[1] / 32,
)
speed_msg = visual.TextStim(
    win=window,
    units="pix",
    antialias="False",
    text=slow_trial,
    wrapWidth=window_size[0] - 400,
    height=window_size[1] / 15,
    alignHoriz="center",
    colorSpace="rgb",
    color=[1, -1, -1],
    bold=True,
)

# m/f from different families to emphasize dimension of interest (sex)
female_greeble_sample = visual.ImageStim(
    window,
    image=image_directory + "symm_greebles/" + "f1~11-v1.tif",
    units="pix",
    size=[window_size[0] / 5],
    colorSpace="dkl",
    color=greeble_color,
)
male_greeble_sample = visual.ImageStim(
    window,
    image=image_directory + "symm_greebles/" + "m2~21-v1.tif",
    units="pix",
    size=[window_size[0] / 5],
    colorSpace="dkl",
    color=greeble_color,
)


genv = EyeLinkCoreGraphicsPsychoPy(tk, window)
pylink.openGraphicsEx(genv)

tk.setOfflineMode()
# sampling rate, 250, 500, 1000, or 2000; #this command won't work for EyeLInk II/I
tk.sendCommand('sample_rate 1000')

# inform the tracker the resolution of the subject display
# [see Eyelink Installation Guide, Section 8.4: Customizing Your PHYSICAL.INI Settings ]
tk.sendCommand("screen_pixel_coords = 0 0 %d %d" % (window_size[0]-1, window_size[1]-1))

# save display resolution in EDF data file for Data Viewer integration purposes
# [see Data Viewer User Manual, Section 7: Protocol for EyeLink Data to Viewer Integration]
tk.sendMessage("DISPLAY_COORDS = 0 0 %d %d" % (window_size[0]-1, window_size[1]-1))

# specify the calibration type, H3, HV3, HV5, HV13 (HV = horiz./vertical),
tk.sendCommand("calibration_type = HV5") #tk.setCalibrationType('HV9') also works, see the #pylink manual


# the model of the tracker, 1-EyeLink I, 2-EyeLink II, 3-Newer models (100/1000Plus/DUO)
eyelinkVer = tk.getTrackerVersion()


# turn off scenelink camera stuff (EyeLink II/I only)
if eyelinkVer == 2: tk.sendCommand("scene_camera_gazemap = NO")

#Set the tracker to parse Events using "GAZE" (or "HREF") data
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


# take in an image list
female_greeble = visual.ImageStim(
    window,
    image=image_directory + "symm_greebles/" + "f1~11-v1.tif",
    units="pix",
    size=[window_size[0] / 4],
    colorSpace="dkl",
    color=greeble_color,
)
male_greeble = visual.ImageStim(
    window,
    image=image_directory + "symm_greebles/" + "m1~11-v1.tif",
    units="pix",
    size=[window_size[0] / 4],
    colorSpace="dkl",
    color=greeble_color,
)

runtimeInfo = info.RunTimeInfo(
    author="kb", win=window, userProcsDetailed=False, verbose=True
)
fixation_point_reward_total = visual.TextStim(
    win=window,
    units="pix",
    antialias="False",
    pos=[0, 15],
    colorSpace="dkl",
    color=dkl_gray,
    height=window_size[0] / 20,
)

cost_per_decision = -1

cue_list = [female_greeble, male_greeble]

high_val_cue = []
low_val_cue = []
high_p_cue = []

# define target coordinates
left_pos_x = -window_size[0] / 5
right_pos_x = window_size[0] / 5


n_reps = n_trials // 2
l_x = np.tile(left_pos_x, n_reps)
r_x = np.tile(right_pos_x, n_reps)
l_r_x_arr = np.concatenate((l_x, r_x))

# shuffle target coordinates
np.random.seed()
np.random.shuffle(l_r_x_arr)


rt_max = 0.75
rt_min = 0.1

mandatory_trial_time = 1.5



left_key = "2"
right_key = "1"
inst_key = left_key

escape_key = "escape"


severe_error_color = dkl_red  # SEVERE error: no response or too fast. -x points.
error_color = dkl_yellow  # SEVERE error: no response or too fast. -x points.

neutral_color = dkl_gray  # no change
good_color = dkl_green  # earned points


# initalize lists
received_rewards = []
total_rewards = []
value_correct_choices = []
p_correct_choices = []
p_correct_ids = []

# timing lists
stim_onset_list = []
stim_offset_list = []
trial_onset_list = []
abs_response_time_list = []

trial_time = []
cp_with_slow_fast = []
obs_cp_with_slow_fast = []
cp_list = exp_param.cp.values[:n_trials].tolist()
obs_cp_list = exp_param.obs_cp.values[:n_trials].tolist()
iti_list = exp_param.iti.values[:n_trials].tolist()
# iti_list = [0] * len(obs_cp_list)

high_p_cue_list = exp_param.p_id_solution[0:n_trials].tolist()
f_images = exp_param.f_image[:n_trials].tolist()
m_images = exp_param.m_image[:n_trials].tolist()


m_image_list = [
    image_directory + "symm_greebles/" + str(m_image) for m_image in m_images
]
f_image_list = [
    image_directory + "symm_greebles/" + str(f_image) for f_image in f_images
]


# show some instructions here.
msg = visual.TextStim(window, text = 'Press ENTER thrice to calibrate the tracker.')
msg.draw()
window.flip()
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


# give instructions
instruction_phase = True
while instruction_phase:
    inst_msg.text = instructions_p1
    inst_msg.setAutoDraw(True)
    female_greeble_sample.setPos([-200, 0])
    male_greeble_sample.setPos([200, 0])
    female_greeble_sample.draw()
    male_greeble_sample.draw()
    window.flip()
    inst_keys_p1 = event.waitKeys(keyList=[inst_key, escape_key])
    if escape_key in inst_keys_p1:
        sys.exit("escape key pressed.")

    inst_msg.text = instructions_p2
    window.flip()
    inst_keys_p2 = event.waitKeys(keyList=[inst_key, escape_key])
    if escape_key in inst_keys_p2:
        sys.exit("escape key pressed.")

    inst_msg.text = instructions_p3
    female_greeble_sample.setPos([-200, 75])
    male_greeble_sample.setPos([200, 75])
    female_greeble_sample.draw()
    male_greeble_sample.draw()
    fixation_point_reward_total.text = str(total_reward)
    fixation_point_reward_total.setPos([0, 75])
    fixation_point_reward_total.draw()
    window.flip()
    inst_keys_p3 = event.waitKeys(keyList=[inst_key, escape_key])
    if escape_key in inst_keys_p3:
        sys.exit("escape key pressed.")

    inst_msg.text = instructions_p4
    window.flip()
    inst_keys_p4 = event.waitKeys(keyList=[inst_key, escape_key])
    if escape_key in inst_keys_p4:
        sys.exit("escape key pressed.")

    inst_msg.text = instructions_p5
    window.flip()
    inst_keys_p4 = event.waitKeys(keyList=[inst_key, escape_key])
    if escape_key in inst_keys_p4:
        sys.exit("escape key pressed.")
    instruction_phase = False

inst_msg.setAutoDraw(False)
window.flip()


trigger = "5"
trigger_wait_instructions = "Waiting for trigger from the scanner..."


# test the trigger
inst_msg.text = trigger_wait_instructions
inst_msg.setAutoDraw(True)
window.flip()
print("Waiting for trigger...")
trigger_output = event.waitKeys(keyList=[trigger], clearEvents=True)

start_time = expTime_clock.getTime() # experiment starts now

inst_msg.setAutoDraw(False)
window.flip()


t = 0


expTime_clock.reset()  # reset so that inst. time is not included
trialTime_clock.reset()
fixation_point_reward_total.text = str(total_reward)
fixation_point_reward_total.setPos([0, 15])




# present choices
while t < n_trials:

    # reverse high value target according to reward vec.
    if obs_cp_list[t] == 1:
        cue_list.reverse()

    # trial has started, get time
    trial_start = expTime_clock.getTime() - start_time
    tk.sendMessage('trial_start')
    tk.sendMessage('TRIALID') #this is a parsing signal for the proprietary data viewer

    trial_onset_list.append(trial_start)

    trialTime_clock.reset()  # reset time

    fixation_point_reward_total.setAutoDraw(True)

    female_greeble.setPos([l_r_x_arr[t], 15])
    male_greeble.setPos([-l_r_x_arr[t], 15])

    female_greeble.setImage(f_image_list[t])
    male_greeble.setImage(m_image_list[t])

    cue_list[0].setAutoDraw(True)
    cue_list[1].setAutoDraw(True)
    window.flip()

    stim_onset_time = expTime_clock.getTime()
    tk.sendMessage('stim_onset')

    stim_onset_list.append(stim_onset_time)

    rt_clock.reset()
    response = event.waitKeys(
        keyList=[left_key, right_key, escape_key], clearEvents=True, maxWait=rt_max
    )

    abs_response_time = expTime_clock.getTime()
    abs_response_time_list.append(abs_response_time)
    tk.sendMessage('response')

    if response is None:
        rt = np.nan  # no response
        choice = np.nan
        id_choice_list.append(np.nan)
        p_accuracy_list.append(np.nan)
        value_accuracy_list.append(np.nan)
    else:
        rt = rt_clock.getTime()
        choice = response[0][0]
        if escape_key in response:
            sys.exit("escape key pressed.")

    # any reason to record the family of high v target?
    # record the identity of the high value target in ascii
    if cue_list[0] == female_greeble:
        high_val_cue.append(ord("f"))  # female
        low_val_cue.append(ord("m"))
    elif cue_list[0] == male_greeble:
        high_val_cue.append(ord("m"))  # male
        low_val_cue.append(ord("f"))

    if (
        cue_list[0].pos[0] == left_pos_x
    ):  # if the pos. of the first (high val) cue in the list is left, then left key is correct
        value_correct_choice = left_key
        value_correct_choices.append(ord("L"))
    else:
        value_correct_choice = right_key  # else, right key is correct
        value_correct_choices.append(ord("R"))

    # record the identity of the high p(r) target in ascii
    if high_p_cue_list[t] == ord("f"):
        high_p_cue.append(ord("f"))  # female
    elif high_p_cue_list[t] == ord("m"):
        high_p_cue.append(ord("m"))  # male

    if (high_val_cue[t] == high_p_cue_list[t]) & (
        cue_list[0].pos[0] == left_pos_x
    ):  # find the left-right soln. for the p_id_soln
        p_correct_choice = left_key
        p_correct_choices.append(ord("L"))
        p_correct_ids.append(high_val_cue[t])

    elif (high_val_cue[t] != high_p_cue_list[t]) & (cue_list[0].pos[0] == left_pos_x):
        p_correct_choice = right_key
        p_correct_choices.append(ord("R"))
        p_correct_ids.append(low_val_cue[t])

    elif (high_val_cue[t] == high_p_cue_list[t]) & (cue_list[0].pos[0] == right_pos_x):
        p_correct_choice = right_key
        p_correct_choices.append(ord("R"))
        p_correct_ids.append(high_val_cue[t])

    elif (high_val_cue[t] != high_p_cue_list[t]) & (cue_list[0].pos[0] == right_pos_x):
        p_correct_choice = left_key
        p_correct_choices.append(ord("L"))
        p_correct_ids.append(low_val_cue[t])

    if choice == left_key:
        LR_choice_list.append(ord("L"))
    elif choice == right_key:
        LR_choice_list.append(ord("R"))
    elif np.isnan(choice):
        LR_choice_list.append(np.nan)

    if rt < rt_max and rt > rt_min:
        if choice == value_correct_choice:
            id_choice_list.append(high_val_cue[t])
            received_rewards.append(rewards[t, max_reward_idx[t]])
            total_reward += rewards[t, max_reward_idx[t]]
            fixation_point_reward_total.color = good_color
            window.flip()

        elif choice != value_correct_choice:
            id_choice_list.append(low_val_cue[t])
            received_rewards.append(rewards[t, min_reward_idx[t]])
            total_reward += rewards[t, min_reward_idx[t]] + cost_per_decision
            fixation_point_reward_total.color = error_color  # think about this...
            # fixation_point_reward_total.color = neutral_color
            window.flip()

    elif rt >= rt_max or rt <= rt_min:
        if choice == value_correct_choice:
            id_choice_list.append(high_val_cue[t])
        elif choice != value_correct_choice:
            id_choice_list.append(low_val_cue[t])
        received_rewards.append(0)
        total_reward += response_failure_reward
        fixation_point_reward_total.color = severe_error_color
        window.flip()

    elif np.isnan(rt):
        received_rewards.append(0)
        total_reward += response_failure_reward
        fixation_point_reward_total.color = severe_error_color
        window.flip()

    fixation_point_reward_total.text = str("{:,}".format(total_reward))
    window.flip()

    total_rewards.append(total_reward)
    rt_list.append(rt)

    if choice in [left_key, right_key]:
        value_accuracy_list.append(choice == value_correct_choice)
        p_accuracy_list.append(choice == p_correct_choice)

    core.wait(
        mandatory_trial_time - trialTime_clock.getTime()
    )  # wait until mandatory trial time has passed
    tk.sendMessage('trial_end')

    cue_list[0].setAutoDraw(False)
    cue_list[1].setAutoDraw(False)

    trial_time.append(
        trialTime_clock.getTime()
    )  # trial time will always be set, sanity check

    # jitter iti & continue to show bank as fixation point
    fixation_point_reward_total.color = neutral_color
    window.flip()
    stim_offset_time = expTime_clock.getTime()
    tk.sendMessage('stim_offset')

    stim_offset_list.append(stim_offset_time)
    tk.sendMessage('iti_begin')

    core.wait(iti_list[t])
    response = event.getKeys(keyList=[escape_key])
    if escape_key in response:
        sys.exit()
    tk.sendMessage('iti_end')
    tk.sendMessage('TRIAL_RESULT') #this is a parsing signal for the proprietary data viewer

    window.flip()

    t += 1

fixation_point_reward_total.setAutoDraw(False)
total_exp_time = expTime_clock.getTime() - start_time
stimulus_duration_list = list(map(operator.sub, stim_offset_list, stim_onset_list))


# save data
header = (
    "trial, subj_id, reward_code, condition, run, LR_choice, value_accuracy, value_LR_solution, reward,"
    + "cumulative_reward, rt, total_trial_time, iti, cp_list, obs_cp_list,high_val_cue,"
    + "high_p_cue, p_accuracy, p_LR_solution, p_id_solution, id_choice, stim_duration,"
    + "stim_onset, stim_offset, abs_response_time, epoch_length, epoch_trial,"
    + "epoch_number"
)


data = np.transpose(
    np.matrix(
        (
            trial_list,
            subj_id_list,
            reward_code_list,
            condition_list,
            run_list,
            LR_choice_list,
            value_accuracy_list,
            value_correct_choices,
            received_rewards,
            total_rewards,
            rt_list,
            trial_time,
            iti_list,
            cp_list,
            obs_cp_list,
            high_val_cue,
            high_p_cue,
            p_accuracy_list,
            p_correct_choices,
            p_correct_ids,
            id_choice_list,
            stimulus_duration_list,
            stim_onset_list,
            stim_offset_list,
            abs_response_time_list,
            epoch_length,
            epoch_trial,
            epoch_number,
        )
    )
)

runtime_data = np.matrix(
    (
        str(runtimeInfo["psychopyVersion"]),
        str(runtimeInfo["pythonVersion"]),
        str(runtimeInfo["pythonScipyVersion"]),
        str(runtimeInfo["pythonPygletVersion"]),
        str(runtimeInfo["pythonPygameVersion"]),
        str(runtimeInfo["pythonNumpyVersion"]),
        str(runtimeInfo["pythonWxVersion"]),
        str(runtimeInfo["windowRefreshTimeAvg_ms"]),
        str(runtimeInfo["experimentRunTime"]),
        str(runtimeInfo["experimentScript.directory"]),
        str(runtimeInfo["systemRebooted"]),
        str(runtimeInfo["systemPlatform"]),
        str(runtimeInfo["systemHaveInternetAccess"]),
        total_exp_time,
    )
)

runtime_header = "psychopy_version, python_version, pythonScipyVersion,\
pyglet_version, pygame_version, numpy_version, wx_version, window_refresh_time_avg_ms,\
begin_time, exp_dir, last_sys_reboot, system_platform, internet_access,\
 total_exp_time"

run_end_msg_text = (
    "Awesome! You have "
    + fixation_point_reward_total.text
    + " coins.\nYou have reached the end of the run.\nPlease wait for the experimenter to continue."
)
# dismiss participant
tk.sendMessage('instruction_phase_onset')
end_msg.text = run_end_msg_text
end_msg.draw()
core.wait(2)
window.flip()
tk.sendMessage('instruction_phase_offset')

pylink.pumpDelay(100)
tk.stopRecording() # stop recording


# save tsv events data
events_header = ("stim_onset, stim_duration, trial_type, rt, accuracy, epoch_length,\
epoch_trial, epoch_number")
events_data = np.transpose(
    np.matrix(
        (
            stim_onset_list[:t],
            stimulus_duration_list[:t],
            trial_list[:t],
            rt_list[:t],
            p_accuracy_list[:t],
            epoch_length[:t],
            epoch_trial[:t],
            epoch_number[:t],
        )
    )
)
np.savetxt(
    output_path_events, events_data, header=events_header, delimiter="\t", comments=""
)


np.savetxt(output_path_beh, data, header=header, delimiter=",", comments="")
np.savetxt(output_path_readable_beh, data, header=header, delimiter="\t",  comments="")

np.savetxt(
    run_info_path,
    runtime_data,
    header=runtime_header,
    delimiter=",",
    comments="",
    fmt="%s",
)



# close the EDF data file
tk.setOfflineMode()
tk.closeDataFile()
pylink.pumpDelay(50)

# Get the EDF data and say goodbye
msg.text='EDF data transferring...'
msg.draw()
window.flip()
tk.receiveDataFile(dataFileName, edf_directory + dataFileName)
core.wait(2)
#close the link to the tracker
tk.close()

# close the graphics
pylink.closeGraphics()


response = event.waitKeys(keyList=[escape_key])

if escape_key in response:
    window.close()
    core.quit()
