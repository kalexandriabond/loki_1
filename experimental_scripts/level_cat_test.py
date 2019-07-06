import os, sys, random, datetime, operator
from psychopy import visual, core, event, monitors, info, gui
from pandas import read_csv, DataFrame
from psychopy.tools.colorspacetools import rgb2dklCart
import numpy as np
from random import shuffle
import pickle


current_time = datetime.datetime.today().strftime("%m%d%Y_%H%M%S")
user_input_dict = {"CoAx ID [####]": "", "Session Number [##]": "", "Run [#]": ""}
sub_inf_dlg = gui.DlgFromDict(
    user_input_dict,
    title="Subject information",
    show=0,
    order=["CoAx ID [####]", "Session Number [##]", "Run [#]"],
)

# set data path & collect information from experimenter
testing = int(input("Testing? "))

if testing is not 1 and testing is not 0:
    sys.exit("Enter 0 or 1.")

parent_directory = os.path.dirname(os.getcwd())
print(parent_directory)

image_directory = parent_directory + "/images/symm_greebles/"
exp_param_directory = parent_directory + "/experimental_parameters/"
analysis_directory = parent_directory + "/analysis/"
run_info_directory = parent_directory + "/data/run_info_data/"

exp_param_file = (
    exp_param_directory + "level_matching_parameters.csv"
)  # same for both sessions

if not os.path.exists(exp_param_file):
    sys.exit("Level matching experimental parameter file does not exist.")

if testing:
    subj_id, session_n, run_n = "9999", "01", 5
else:
    sub_inf_dlg.show()
    subj_id = user_input_dict["CoAx ID [####]"]
    session_n = user_input_dict["Session Number [##]"]
    run_n = int(user_input_dict["Run [#]"])

try:
    assert len(str(run_n)) == 1
    assert len(str(session_n)) == 2
    assert run_n < 7
except AssertionError:
    sys.exit(
        "Format failure. Please re-enter 2 digits session number or 1 digit run number (n<7)."
    )


data_directory = parent_directory + "/data/BIDS/sub-{}/ses-{}/func/".format(
    subj_id, session_n
)
if not os.path.isdir(data_directory):
    os.makedirs(data_directory)

### INSTRUCTION ###
vertical_txt_break = "\n" * 8
small_vertical_txt_break = "\n" * 2
horiz_txt_break = "\t" * 9

instruction1 = (
    "Now you are going to match greebles at two different categories: 'sex' or 'family'. The category to match will be "
    "given at the beginning of each trial. After the fixation point, you will see a sample greeble and "
    "four more greebles following it. "
    + small_vertical_txt_break
    + "If the following greebles match the category of the first one, press the left "
    "(yellow) button with your left thumb; if not, press the right (red) button with your right thumb. "
    + small_vertical_txt_break
    + "Press the green button when you are ready to begin!"
)

instruction2 = "Between trials, focus on the fixation cross."

between_run_inst = "Feel free to take a break! \n Press the green button when you're ready to continue."

end_msg = "Awesome! You have finished the matching task. "


# instantiate psychopy object instances
expTime_clock = core.Clock()
trialTime_clock = core.Clock()
matchTime_clock = core.Clock()
rt_clock = core.Clock()


screen_size = [1280, 1024]
mon = monitors.Monitor("ET_display_computer", width=36.0, distance=64.0)
mon.setSizePix(screen_size)
mon.saveMon()

center = [0, 0]

if screen_size != mon.getSizePix():
    center[0] = (mon.getSizePix()[0] / 2) - (screen_size[0] / 2)
    center[1] = (mon.getSizePix()[1] / 2) - (screen_size[1] / 2)


# Specify colors using the DKL colorspace
# DKL = [luminance, hue, saturation] where
# luminance is degrees -90 to 90
# hue is degrees 0 to 360
# saturation is eccentricity 0 to 1

luminance = 10
contrast = 1

dkl_purple = (luminance, 300, contrast)
dkl_red = (luminance, 45, contrast)
dkl_gray = (luminance, 0, 0)
dkl_green = (luminance, 145, contrast)
# dkl_orange = (luminance,45,contrast)
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
    fullscr=True,
    pos=center,
    screen=0,
)

inst_msg = visual.TextStim(
    win=window,
    units="pix",
    antialias="False",
    colorSpace="rgb",
    color=inst_color,
    wrapWidth=screen_size[0] - 400,
    height=screen_size[1] / 32,
)
end_msg = visual.TextStim(
    win=window,
    units="pix",
    antialias="False",
    wrapWidth=screen_size[0] - 400,
    colorSpace="rgb",
    color=inst_color,
    height=screen_size[1] / 32,
)

level_msg = visual.TextStim(
    win=window,
    units="pix",
    antialias="False",
    pos=[0, 15],
    colorSpace="rgb",
    color=[1, 1, 1],
    height=screen_size[0] / 15,
)


mandatory_trial_time = 10

inst_key = "s"
left_key = "a"
right_key = "f"

escape_key = "escape"

neutral_color = dkl_gray
good_color = dkl_green
go_color = dkl_red


greeble = visual.ImageStim(
    window,
    # image=image_directory + "f1~11-v1.tif",
    units="pix",
    size=[screen_size[0] / 4],
    colorSpace="dkl",
    color=greeble_color,
)
greeble_sample = visual.ImageStim(
    window,
    # image=image_directory + "f1~11-v1.tif",
    units="pix",
    size=[screen_size[0] / 4],
    colorSpace="dkl",
    color=greeble_color,
)
# define target coordinates
pos_x = 0
greeble.setPos([pos_x, 15])
greeble_sample.setPos([pos_x, 15])


runtimeInfo = info.RunTimeInfo(
    author="kb", win=window, userProcsDetailed=False, verbose=True
)
fixation_cross = visual.TextStim(
    win=window,
    units="pix",
    text="+",
    antialias="False",
    pos=[0, 15],
    colorSpace="dkl",
    color=dkl_gray,
    height=screen_size[0] / 15,
)

# give instructions
instruction_phase = True
while instruction_phase:
    inst_msg.text = instruction1
    inst_msg.setAutoDraw(True)
    window.flip()
    inst_keys_1 = event.waitKeys(keyList=[inst_key, escape_key])
    if escape_key in inst_keys_1:
        sys.exit("escape key pressed.")

    inst_msg.text = instruction2
    inst_msg.setAutoDraw(True)
    window.flip()
    inst_keys_2 = event.waitKeys(keyList=[inst_key, escape_key])
    if escape_key in inst_keys_2:
        sys.exit("escape key pressed.")

    instruction_phase = False

inst_msg.setAutoDraw(False)
window.flip()

# experiment specific variables
num_matches = 4
df = read_csv(exp_param_file, header=0)

# experiment will start with run_n and ended with the last run
while run_n < 7:  # TODO

    # initalize lists
    id_choice_accuracy_list = []
    correct_key_choices = []

    # timing lists
    stim_list = []
    stim_onset_list = []
    stim_offset_list = []
    trial_onset_list = []
    abs_response_time_list = []
    trial_time = []
    level_list = []

    # initialize dependent variables
    rt_list = []
    LR_choice_list = []

    if testing:
        output_file_name = "sub-{}_ses_{}_task-level_run-0{}_testing".format(
            subj_id, session_n, run_n
        )
    else:
        output_file_name = "sub-{}_ses_{}_task-level_run-0{}".format(
            subj_id, session_n, run_n
        )

    output_path = data_directory + output_file_name + "_events.tsv"
    output_path_json = data_directory + output_file_name + "_events.json"

    run_info_path = run_info_directory + output_file_name + "_runInfo.csv"

    if not testing and os.path.exists(output_path):
        sys.exit(output_file_name + " already exists! Overwrite danger...Exiting.")

    # specify constants

    exp_param = df[df["run"] == run_n]
    param = exp_param.values

    n_trials = len(param)  # num of trials in a run
    n_test_trials = 1

    if testing:
        n_trials = n_test_trials

    trial_list = list(np.arange(0, n_trials))

    # need to timestamp every event.
    expTime_clock.reset()  # reset so that inst. time is not included
    trialTime_clock.reset()

    start_time = expTime_clock.getTime()

    t = 0
    # present choices
    while t < n_trials:
        # trial has started, get time
        trial_start = expTime_clock.getTime() - start_time
        trial_onset_list.append(trial_start)

        trialTime_clock.reset()

        fixation_cross.setAutoDraw(False)
        level_msg.text = param[t, 1]  # support to be randomized
        level_list.append(param[t, 1])

        level_msg.setAutoDraw(True)
        window.flip()
        core.wait(5)

        level_msg.setAutoDraw(False)
        fixation_cross.setAutoDraw(True)

        window.flip()
        core.wait(5)

        fixation_cross.setAutoDraw(False)

        greeble_sample.setImage(image_directory + param[t, 2])  # TODO: check this
        stim_list.append(image_directory + param[t, 2])

        greeble_sample.setAutoDraw(True)
        window.flip()

        stim_onset_time = expTime_clock.getTime()
        stim_onset_list.append(stim_onset_time)
        core.wait(2)

        fixation_cross.color = go_color
        fixation_cross.setAutoDraw(True)
        greeble_sample.setAutoDraw(False)
        window.flip()
        stim_offset_time = expTime_clock.getTime()
        stim_offset_list.append(stim_offset_time)

        core.wait(8)

        for i in range(num_matches):
            matchTime_clock.reset()  # reset time

            fixation_cross.setAutoDraw(False)
            greeble.setImage(image_directory + param[t, i + 3])
            stim_list.append(image_directory + param[t, i + 3])

            greeble.setAutoDraw(True)
            window.flip()
            stim_onset_time = expTime_clock.getTime()
            stim_onset_list.append(stim_onset_time)

            rt_clock.reset()
            response = event.waitKeys(
                keyList=[left_key, right_key, escape_key], clearEvents=True, maxWait=10
            )

            abs_response_time = expTime_clock.getTime()
            abs_response_time_list.append(abs_response_time)

            if response is None:
                rt = np.nan  # no response
                choice = np.nan
                # id_choice_list.append(np.nan)
            else:
                rt = rt_clock.getTime()
                choice = response[0][0]
                if escape_key in response:
                    sys.exit("escape key pressed.")

            if choice == left_key:
                LR_choice_list.append(ord("L"))
            elif choice == right_key:
                LR_choice_list.append(ord("R"))
            elif np.isnan(choice):
                LR_choice_list.append(np.nan)

            # core.wait(0.1)
            fixation_cross.color = neutral_color
            greeble.setAutoDraw(False)
            fixation_cross.setAutoDraw(True)
            window.flip()
            stim_offset_time = expTime_clock.getTime()
            stim_offset_list.append(stim_offset_time)

            rt_list.append(rt)

            core.wait(
                mandatory_trial_time - matchTime_clock.getTime()
            )  # wait until mandatory trial time has passed

            fixation_cross.color = neutral_color
            window.flip()

        trial_time.append(
            trialTime_clock.getTime()
        )  # trial time will always be set to 10+10*num_matches
        t += 1

    fixation_cross.setAutoDraw(False)
    total_exp_time = expTime_clock.getTime()
    stimulus_duration_list = list(map(operator.sub, stim_offset_list, stim_onset_list))

    # save tsv events data
    events_header = "stim_onset, stim_duration, stim_greebles, trial_num, trial_type, rt, choice"
    events_data = np.transpose(
        np.matrix(
            (
                stim_onset_list,
                stimulus_duration_list,
                stim_list,
                trial_list,
                level_list,
                rt_list,
                LR_choice_list,
            )
        )
    )
    np.savetxt(
        output_path,
        events_data,
        header=events_header,
        fmt="%s",
        delimiter="\t",
        comments="",
    )

    np.savetxt(
        output_path_json,
        events_data,
        header=events_header,
        delimiter=",",
        fmt="%s",
        comments="",
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

    np.savetxt(
        run_info_path,
        runtime_data,
        header=runtime_header,
        delimiter=",",
        comments="",
        fmt="%s",
    )

    inst_msg.text = between_run_inst
    inst_msg.setAutoDraw(True)
    window.flip()
    between_run_key = event.waitKeys(keyList=[inst_key, escape_key])
    if escape_key in between_run_key:
        sys.exit("escape key pressed.")
    inst_msg.setAutoDraw(False)
    window.flip()

    run_n += 1  # TODO: check run proceeds


# dismiss participant
instruction_phase = True
while instruction_phase:
    end_msg.text = end_msg_text
    end_msg.draw()
    window.flip()
    end_keys = event.waitKeys(keyList=[escape_key])
    sys.exit("escape key pressed.")
    instruction_phase = False
    window.flip()

window.flip()
window.close()
core.quit()
