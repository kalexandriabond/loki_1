import os,sys,random,datetime,operator
from psychopy import visual,core,event,monitors,info,gui
from pandas import read_csv, DataFrame
from psychopy.tools.colorspacetools import rgb2dklCart
import numpy as np
from random import shuffle

current_time = datetime.datetime.today().strftime("%m%d%Y_%H%M%S")
user_input_dict = {'CoAx ID [####]': ''}
sub_inf_dlg = gui.DlgFromDict(user_input_dict, title='Subject information', show=0, order=['CoAx ID [####]'])

image_directory = '../images/symm_greebles/'
exp_param_directory = '../experimental_parameters/'
analysis_directory = '../analysis/'
data_directory = '../data/pilot_class/'

exp_param_file = exp_param_directory + 'level_matching_parameters.csv'

# set data path & collect information from experimenter
testing = int(input("Testing? "))

if testing is not 1 and testing is not 0:
    sys.exit('Enter 0 or 1.')

if testing:
    subj_id = -1
else:
    sub_inf_dlg.show()
    subj_id = int(float(user_input_dict['CoAx ID [####]']))

output_file_name = "level_matching_subj{}({})".format(subj_id, current_time)

output_path = data_directory + output_file_name + ".json"
run_info_path = os.getcwd() + '/data/pilot_criterion/' + output_file_name + "_runInfo.json"

output_path_readable = data_directory + output_file_name + ".csv"
run_info_path_readable = os.getcwd() + '/data/pilot_criterion/' + output_file_name + "_runInfo.csv"

if not testing and os.path.exists(output_path):
    sys.exit(output_file_name + " already exists! Overwrite danger...Exiting.")


#specify constants
exp_param = read_csv(exp_param_file, header=0)
param = exp_param.values

n_trials = len(param)
n_test_trials = 4 #needs to be divisible by 2

if testing:
    n_trials = n_test_trials

trial_list = list(np.arange(0, n_trials))

vertical_txt_break = "\n"*8
small_vertical_txt_break = "\n"*2
horiz_txt_break = "\t"*9

instruction1 = ("Now you are going to match greebles at different categories. After the fixation point, you will be "
                "presented a sample greeble and four more greebles following it. A category will be given at the "
                "beginning each trial. The categories could be 'family', 'individual', or 'sex'. If the following "
                "greebles match the category of the first one, press the left (yellow) button; if not, press the right "
                "(red) button.")

instruction2 = ("Between trials, focus on the fixation cross.")

between_run_inst = ("Feel free to take a break! \nPress the green button when you're ready to continue.")

#initialize dependent variables
rt_list = []
LR_choice_list = []
id_choice_list = []
cumulative_accuracy_list = []

subj_id_list = [subj_id] * n_trials

#instantiate psychopy object instances
expTime_clock = core.Clock()
trialTime_clock = core.Clock()
matchTime_clock = core.Clock()
rt_clock = core.Clock()

testing_monitor = monitors.Monitor('testing_computer')
# testing_monitor.setSizePix = [1920,1080]
testing_monitor.setSizePix = [1680,1050]
testing_monitor.saveMon()

screen_size = testing_monitor.setSizePix
center=[0,0]

if screen_size != testing_monitor.setSizePix:
    center[0] = (testing_monitor.setSizePix[0]/2) - (screen_size[0]/2)
    center[1] = (testing_monitor.setSizePix[1]/2) - (screen_size[1]/2)

window = visual.Window(size = screen_size, units='pix', monitor = testing_monitor, color = [-1,-1,-1],
                       colorSpace = 'rgb', blendMode = 'avg', useFBO = True, allowGUI = False,
                       fullscr=True, pos=center)

conversionMatrix = testing_monitor.getDKL_RGB(RECOMPUTE=False) #for isoluminance

inst_msg = visual.TextStim(win=window, units='pix',antialias='False',colorSpace='dkl', color=[90,0,1],
                           wrapWidth=screen_size[0]-400, height=screen_size[1]/32)
end_msg = visual.TextStim(win=window, units='pix', antialias='False', wrapWidth=screen_size[0]-400,colorSpace='dkl',
                          color=[90,0,1], height=screen_size[1]/32)
level_msg = visual.TextStim(win=window,units='pix',antialias='False',pos=[0,15], colorSpace='rgb', color=[1,1,1],
                                 height=screen_size[0]/15)


n_reps = n_trials//2
num_matches = 4

mandatory_trial_time = 10

inst_key = 's'
left_key = 'f'
right_key = 'a'

escape_key = 'escape'

neutral_color = [1,1,1] #no change
responded_color = [0,1,0]
go_color = [1,0,0]


greeble = visual.ImageStim(window, image=image_directory + 'f1~11-v1.tif',units='pix',size=[screen_size[0]/4])
greeble_sample = visual.ImageStim(window, image=image_directory + 'f1~11-v1.tif',units='pix',size=[screen_size[0]/4])
#define target coordinates
pos_x = 0
greeble.setPos([pos_x, 15])
greeble_sample.setPos([pos_x, 15])


runtimeInfo = info.RunTimeInfo(author='kb',win=window,userProcsDetailed=False, verbose=True)
fixation_cross = visual.TextStim(win=window,units='pix',antialias='False',pos=[0,15], colorSpace='rgb', color=[1,1,1],
                                 height=screen_size[0]/15)

#initalize lists
id_choice_accuracy_list = []
correct_key_choices = []

#timing lists
stim_onset_list = []
stim_offset_list = []
trial_onset_list = []
abs_response_time_list = []
trial_time = []


#give instructions
instruction_phase = True
while instruction_phase:
    inst_msg.text = instruction1
    inst_msg.setAutoDraw(True)
    window.flip()
    inst_keys_1 = event.waitKeys(keyList=[inst_key, escape_key])
    if escape_key in inst_keys_1:
        sys.exit('escape key pressed.')

    inst_msg.text = instruction2
    inst_msg.setAutoDraw(True)
    window.flip()
    inst_keys_2 = event.waitKeys(keyList=[inst_key, escape_key])
    if escape_key in inst_keys_2:
        sys.exit('escape key pressed.')

    instruction_phase = False

inst_msg.setAutoDraw(False)
window.flip()

t=0
#need to timestamp every event.
expTime_clock.reset() #reset so that inst. time is not included
trialTime_clock.reset()
fixation_cross.text = "+"

start_time = expTime_clock.getTime()


#present choices
while t < n_trials:
    #trial has started, get time
    trial_start = expTime_clock.getTime() - start_time
    trial_onset_list.append(trial_start)

    trialTime_clock.reset()

    fixation_cross.setAutoDraw(False)
    level_msg.text = param[t,1] # support to be randomized
    level_msg.setAutoDraw(True)
    window.flip()
    core.wait(5)

    level_msg.setAutoDraw(False)
    fixation_cross.setAutoDraw(True)

    window.flip()
    core.wait(5)

    fixation_cross.setAutoDraw(False)

    greeble_sample.setImage(image_directory+param[t,-2])

    greeble_sample.setAutoDraw(True)
    window.flip()

    stim_onset_time = expTime_clock.getTime()
    stim_onset_list.append(stim_onset_time)
    core.wait(2)

    fixation_cross.color = go_color
    fixation_cross.setAutoDraw(True)
    greeble_sample.setAutoDraw(False)
    window.flip()
    core.wait(8)

    for i in range(num_matches):
        matchTime_clock.reset()  # reset time

        fixation_cross.setAutoDraw(False)
        greeble.setImage(image_directory+param[t, i+2])
        greeble.setAutoDraw(True)
        window.flip()
        stim_onset_time = expTime_clock.getTime()
        stim_onset_list.append(stim_onset_time)

        rt_clock.reset()
        response=event.waitKeys(keyList=[left_key, right_key, escape_key],
          clearEvents=True, maxWait=10)

        abs_response_time = expTime_clock.getTime()
        abs_response_time_list.append(abs_response_time)


        if response is None:
            rt = np.nan #no response
            choice = np.nan
            # id_choice_list.append(np.nan)
        else:
            rt = rt_clock.getTime()
            choice=response[0][0]
            if escape_key in response:
                sys.exit('escape key pressed.')

        if choice == left_key:
            LR_choice_list.append(ord('L'))
        elif choice == right_key:
            LR_choice_list.append(ord('R'))
        elif np.isnan(choice):
            LR_choice_list.append(np.nan)

        core.wait(0.1)
        stim_offset_time = expTime_clock.getTime()
        stim_offset_list.append(stim_offset_time)

        fixation_cross.color = neutral_color
        greeble.setAutoDraw(False)
        fixation_cross.setAutoDraw(True)
        window.flip()

        rt_list.append(rt)

        core.wait(mandatory_trial_time - matchTime_clock.getTime()) #wait until mandatory trial time has passed

        fixation_cross.color = neutral_color
        window.flip()

    trial_time.append(trialTime_clock.getTime())  # trial time will always be set to 10+10*num_matches
    t+=1

fixation_cross.setAutoDraw(False)
total_exp_time = expTime_clock.getTime()
stimulus_duration_list = list(map(operator.sub, stim_offset_list, stim_onset_list))


#save data
header = ('trial, subj_id, LR_choice, rt, total_trial_time, stim_duration, stim_onset, stim_offset, abs_response_time')

data = np.transpose(np.matrix((trial_list,subj_id_list, LR_choice_list,
rt_list, trial_time, stimulus_duration_list, stim_onset_list, stim_offset_list, abs_response_time_list)))


runtime_data = np.matrix((str(runtimeInfo['psychopyVersion']), str(runtimeInfo['pythonVersion']),
str(runtimeInfo['pythonScipyVersion']),str(runtimeInfo['pythonPygletVersion']),
str(runtimeInfo['pythonPygameVersion']),str(runtimeInfo['pythonNumpyVersion']),str(runtimeInfo['pythonWxVersion']),
str(runtimeInfo['windowRefreshTimeAvg_ms']), str(runtimeInfo['experimentRunTime']),
str(runtimeInfo['experimentScript.directory']),str(runtimeInfo['systemRebooted']),
str(runtimeInfo['systemPlatform']),str(runtimeInfo['systemHaveInternetAccess']), total_exp_time))

runtime_header = ("psychopy_version, python_version, pythonScipyVersion,\
pyglet_version, pygame_version, numpy_version, wx_version, window_refresh_time_avg_ms,\
begin_time, exp_dir, last_sys_reboot, system_platform, internet_access,\
 total_exp_time")

np.savetxt(output_path, data, header=header, delimiter=',',comments='')
np.savetxt(run_info_path,runtime_data, header=runtime_header,delimiter=',',comments='',fmt="%s")
np.savetxt(output_path_readable, data, header=header, delimiter=',',comments='')
np.savetxt(run_info_path_readable,runtime_data, header=runtime_header,delimiter=',',comments='',fmt="%s")

end_msg_text = ("Awesome! You are ready to continue to the main task. \nLet the experimenter know that you're finished.")

#dismiss participant
instruction_phase = True
while instruction_phase:

    end_msg.text = end_msg_text

    end_msg.draw()
    window.flip()
    end_keys = event.waitKeys(keyList=[escape_key])
    sys.exit('escape key pressed.')
    instruction_phase = False
    window.flip()

window.flip()
window.close()


