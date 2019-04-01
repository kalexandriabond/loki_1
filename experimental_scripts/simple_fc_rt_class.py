import os,sys,random,datetime,operator
from psychopy import visual,core,event,monitors,info,gui
from pandas import read_csv, DataFrame
from psychopy.tools.colorspacetools import rgb2dklCart
import numpy as np
from random import shuffle



current_time = datetime.datetime.today().strftime("%m%d%Y_%H%M%S")
user_input_dict = {'CoAx ID [####]': ''}
sub_inf_dlg = gui.DlgFromDict(user_input_dict, title='Subject information',
show=0, order=['CoAx ID [####]'])


##this is problematic, will not get input. issue opened.
# from psychopy import prefs
# prefs.general['audioLib'] = ['pygame']
# from psychopy.sound import Sound

# set data path & collect information from experimenter
testing = int(input("Testing? "))

if testing is not 1 and testing is not 0:
    sys.exit('Enter 0 or 1.')

image_directory = os.getcwd() + '/images/symm_greebles/'
exp_param_directory = os.getcwd() + '/experimental_parameters/'
analysis_directory = os.getcwd() + '/analysis/'
data_directory = os.getcwd() + '/data/pilot_class/'

if testing:
    subj_id = -1
    exp_param_file = exp_param_directory + 'random_classification_task_parameters.csv'

else:
    sub_inf_dlg.show()
    subj_id = int(float(user_input_dict['CoAx ID [####]']))
    # exp_param_file = exp_param_directory + subj_id + '_' + 'sess' + session_n + '_' + 'cond' + condition + '.csv'
    exp_param_file = exp_param_directory + 'random_classification_task_parameters.csv'


    if not os.path.exists(exp_param_file):
        sys.exit("Experimental parameter file does not exist.")

if testing:
    output_file_name = str(subj_id) + '_criterion' + '_' + str(current_time)
else:
    output_file_name = str(subj_id) + '_criterion' + '_' + str(current_time)

output_path = data_directory + output_file_name + ".json"
run_info_path = os.getcwd() + '/data/pilot_criterion/' + output_file_name + "_runInfo.json"

output_path_readable = data_directory + output_file_name + ".csv"
run_info_path_readable = os.getcwd() + '/data/pilot_criterion/' + output_file_name + "_runInfo.csv"

if not testing and os.path.exists(output_path):
    sys.exit(output_file_name + " already exists! Overwrite danger...Exiting.")


#specify constants
exp_param = read_csv(exp_param_file, header=0)
#strip whitespace from column names
exp_param.columns = exp_param.columns.str.strip()


n_trials = len(exp_param.trial)
n_test_trials = 10 #needs to be divisible by 2

if testing:
    n_trials = n_test_trials

trial_list = list(np.arange(0, n_trials))

#total_reward = (n_trials // 2)

vertical_txt_break = "\n"*8
small_vertical_txt_break = "\n"*2
horiz_txt_break = "\t"*9

#these will be randomly presented greebles, sex division doesn't matter.
instructions_p1 = ("Now, as before, you will be presented with a pair of greebles. But instead of identifying the sex of each greeble, you will be asked whether you think the pair of greebles belongs to the same family. " +
"\n\nUnlike before, you will no longer know whether you were correct or incorrect about your choice, and the cross will remain white after you make a choice.  However, if you choose too slowly or too quickly, the cross will turn red and you will have to wait five seconds before you can proceed.\n\n" +
 "For this task, if you think that the greebles DO belong to the same family, press the left (yellow) button with your left thumb. If you think that the greebles do NOT belong to the same family, press the right (red) button with your right thumb.\n\n" +
 "Press the green button when you are ready to begin.")

instructions_p2 = ("Between trials, focus on the fixation cross.")

slow_trial = ("Too slow! \nChoose quickly.")
fast_trial = ("Too fast! \nSlow down.")

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
rt_clock = core.Clock()

testing_monitor = monitors.Monitor('testing_computer')
# testing_monitor.setSizePix = [1920,1080]
testing_monitor.setSizePix = [1280,1024]
testing_monitor.saveMon()

screen_size = testing_monitor.setSizePix
center=[0,0]

if screen_size != testing_monitor.setSizePix:
    center[0] = (testing_monitor.setSizePix[0]/2) - (screen_size[0]/2)
    center[1] = (testing_monitor.setSizePix[1]/2) - (screen_size[1]/2)

window = visual.Window(size = screen_size, units='pix', monitor = testing_monitor, color = [-1,-1,-1], \
       colorSpace = 'rgb', blendMode = 'avg', useFBO = True, allowGUI = \
       False,fullscr=True, pos=center)

conversionMatrix = testing_monitor.getDKL_RGB(RECOMPUTE=False) #for isoluminance

inst_msg = visual.TextStim(win=window, units='pix',antialias='False',colorSpace='dkl', color=[90,0,1], wrapWidth=screen_size[0]-400, height=screen_size[1]/32)
end_msg = visual.TextStim(win=window, units='pix', antialias='False', wrapWidth=screen_size[0]-400,colorSpace='dkl', color=[90,0,1], height=screen_size[1]/32)
speed_msg = visual.TextStim(win=window, units='pix',antialias='False', text=slow_trial,  wrapWidth=screen_size[0]-400, height=screen_size[1]/15,
alignHoriz='center', colorSpace='rgb',color=[1,-1,-1], bold=True)

slow_trial = ("Too slow! \nChoose quickly.")
fast_trial = ("Too fast! \nSlow down. \nYou can continue in 5 seconds.")

#m/f from different families to emphasize dimension of interest (sex)
greeble_1_sample = visual.ImageStim(window, image=image_directory + 'f1~11-v1.tif',units='pix',size=[screen_size[0]/5], colorSpace='dkl', color=[90,0,1])
greeble_2_sample = visual.ImageStim(window, image=image_directory + 'm2~21-v1.tif',units='pix',size=[screen_size[0]/5], colorSpace='dkl', color=[90,0,1])




#take in an image list
greeble_1 = visual.ImageStim(window, image=image_directory + 'f1~11-v1.tif',units='pix',size=[screen_size[0]/4])
greeble_2 = visual.ImageStim(window, image=image_directory + 'm1~11-v1.tif',units='pix',size=[screen_size[0]/4])


runtimeInfo = info.RunTimeInfo(author='kb',win=window,userProcsDetailed=False, verbose=True)
fixation_cross = visual.TextStim(win=window,units='pix',antialias='False',pos=[0,15], colorSpace='rgb', color=[1,1,1],height=screen_size[0]/15)


cue_list = [greeble_1, greeble_2]


#define target coordinates
left_pos_x = -screen_size[0]/5
right_pos_x = screen_size[0]/5


n_reps = n_trials//2
l_x = np.tile(left_pos_x, n_reps)
r_x = np.tile(right_pos_x, n_reps)
l_r_x_arr = np.concatenate((l_x, r_x))

#shuffle target coordinates
np.random.seed()
np.random.shuffle(l_r_x_arr)


fast_penalty_time = 5 #this is insignificant relative to the ITI now. Can't punish them with time. might also interfere with run time.

rt_max = 1.2
rt_min = .1

response_failure_reward = -5

mandatory_trial_time = 1.5

inst_key = 's'

left_key = 'f'
right_key = 'a'


escape_key = 'escape'


severe_error_color = [1,0,0] #SEVERE error: no response or too fast. -x points.
# error_color = [1,1,0] #SEVERE error: no response or too fast. -x points.

neutral_color = [1,1,1] #no change
# good_color = [0,1,0] #earned points

#initalize lists
received_rewards = []
#total_rewards = []
id_choice_accuracy_list = []
correct_key_choices = []

#timing lists
stim_onset_list = []
stim_offset_list = []
trial_onset_list = []
abs_response_time_list = []
trial_time = []



iti_list = exp_param.iti.values[:n_trials].tolist()

id_solution_list = exp_param.LR_solution[0:n_trials].tolist() #this is now left-right sol.
t1_images = exp_param.t1_image[:n_trials].tolist()
t2_images = exp_param.t2_image[:n_trials].tolist()


t1_image_list = [image_directory+str(t1_image) for t1_image in t1_images]
t2_image_list = [image_directory+str(t2_image) for t2_image in t2_images]

#get family code from m_image list

# #Change the picture from RGB to DKL, an isoluminant color space
# dkl_m_image_list = [rgb2dklCart(m_image_list[t], conversionMatrix=conversionMatrix) for t in range(n_trials)]
# dkl_f_image_list = [rgb2dklCart(f_image_list[t], conversionMatrix=conversionMatrix) for t in range(n_trials)]

#give instructions
instruction_phase = True
while instruction_phase:
    inst_msg.text = instructions_p1
    inst_msg.setAutoDraw(True)
    window.flip()
    inst_keys_p1 = event.waitKeys(keyList=[inst_key, escape_key])
    if escape_key in inst_keys_p1:
        sys.exit('escape key pressed.')

    inst_msg.text = instructions_p2
    inst_msg.setAutoDraw(True)
    window.flip()
    inst_keys_p2 = event.waitKeys(keyList=[inst_key, escape_key])
    if escape_key in inst_keys_p2:
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

    trialTime_clock.reset() #reset time

    fixation_cross.setAutoDraw(True)

    greeble_1.setPos([l_r_x_arr[t], 15])
    greeble_2.setPos([-l_r_x_arr[t], 15])

    greeble_1.setImage(t1_image_list[t])
    greeble_2.setImage(t2_image_list[t])

    cue_list[0].setAutoDraw(True)
    cue_list[1].setAutoDraw(True)
    window.flip()

    stim_onset_time = expTime_clock.getTime()
    stim_onset_list.append(stim_onset_time)

    rt_clock.reset()
    response=event.waitKeys(keyList=[left_key, right_key, escape_key],
      clearEvents=True, maxWait=rt_max)

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


    #get identity of selection
    #if the position of the female is on the left
    # if greeble_1.pos[0] == left_pos_x: #if the pos. of the solution is on the left, then left key is correct
    #     correct_key_choice = left_key
    #     correct_key_choices.append(ord('L'))
    # else:
    #     correct_key_choice = right_key #else, right key is correct
    #     correct_key_choices.append(ord('R'))

    correct_key_choice = left_key
    incorrect_key_choice = right_key


    if choice == left_key:
        LR_choice_list.append(ord('L'))
    elif choice == right_key:
        LR_choice_list.append(ord('R'))
    elif np.isnan(choice):
        LR_choice_list.append(np.nan)


    if rt < rt_max and rt > rt_min:
            #total_reward += received_rewards[t]
            fixation_cross.color = neutral_color
            window.flip()

    elif rt >= rt_max or rt <= rt_min:
                #total_reward += response_failure_reward
        fixation_cross.color = severe_error_color

        if rt >= rt_max:
            speed_msg.text = slow_trial
        if rt <= rt_min:
            speed_msg.text = fast_trial

        speed_msg.setAutoDraw(True)
        cue_list[0].setAutoDraw(False)
        cue_list[1].setAutoDraw(False)
        fixation_cross.setAutoDraw(False)
        inst_msg.setAutoDraw(False)
        window.flip()
        core.wait(fast_penalty_time)
        speed_msg.setAutoDraw(False)


    elif np.isnan(rt):
        # received_rewards.append(0)
        #total_reward += response_failure_reward
        fixation_cross.color = severe_error_color
        speed_msg.text = slow_trial
        speed_msg.setAutoDraw(True)
        cue_list[0].setAutoDraw(False)
        cue_list[1].setAutoDraw(False)
        inst_msg.setAutoDraw(False)
        fixation_cross.setAutoDraw(False)
        window.flip()
        core.wait(fast_penalty_time)
        speed_msg.setAutoDraw(False)


    window.flip()

    #total_rewards.append(#total_reward)
    rt_list.append(rt)


    if choice in [left_key, right_key]:
        id_choice_accuracy_list.append(LR_choice_list[t] == ord('L'))
    else:
        id_choice_accuracy_list.append(np.nan)

    core.wait(mandatory_trial_time - trialTime_clock.getTime()) #wait until mandatory trial time has passed

    cue_list[0].setAutoDraw(False)
    cue_list[1].setAutoDraw(False)

    trial_time.append(trialTime_clock.getTime()) #trial time will always be set, sanity check


    fixation_cross.color = neutral_color
    window.flip()
    stim_offset_time = expTime_clock.getTime()
    stim_offset_list.append(stim_offset_time)

    core.wait(iti_list[t])
    window.flip()

    t+=1

fixation_cross.setAutoDraw(False)
total_exp_time = expTime_clock.getTime()
stimulus_duration_list = list(map(operator.sub, stim_offset_list, stim_onset_list))


#save data
header = ('trial, subj_id, LR_choice,' +
 'rt, total_trial_time, iti,' +
 'id_solution, id_choice_acc, stim_duration, stim_onset, stim_offset, abs_response_time')

data = np.transpose(np.matrix((trial_list,subj_id_list, LR_choice_list,
rt_list, trial_time, iti_list, id_solution_list,
id_choice_accuracy_list,
 stimulus_duration_list, stim_onset_list, stim_offset_list, abs_response_time_list)))

#
# data_dict = {'trial':trial_list[:t], 'subj_id': subj_id_list[:t], 'LR_choice': LR_choice_list[:t], 'reward': received_rewards[:t],
# 'cumulative_reward': #total_rewards[:t], 'rt': rt_list[:t], 'total_trial_time': trial_time[:t], 'iti': iti_list[:t],
# 'id_choice':id_choice_list[:t], 'id_solution': id_solution_list[:t],
# 'id_choice_acc': id_choice_accuracy_list[:t], 'cum_acc': cumulative_accuracy_list[:t],
# 'stim_duration': stimulus_duration_list[:t], 'stim_onset': stim_onset_list[:t],
# 'stim_offset': stim_offset_list[:t], 'abs_response_time': abs_response_time_list[:t]}

# data = np.transpose(np.matrix((trial_list,subj_id_list, LR_choice_list,
# received_rewards, #total_rewards, rt_list, trial_time, iti_list, id_choice_list, id_solution_list,
# id_choice_accuracy_list, cumulative_accuracy_list,
# stimulus_duration_list, stim_onset_list, stim_offset_list, abs_response_time_list)))


# df_header = ['trial', 'subj_id', 'LR_choice', 'reward',
# 'cumulative_reward', 'rt', 'total_trial_time', 'iti,'
# 'id_choice', 'id_solution', 'id_choice_acc', 'cum_acc', 'stim_duration', 'stim_onset', 'stim_offset', 'abs_response_time']
#
# exp_data_df = DataFrame(data_dict)
# exp_data_df.to_csv(output_path, header=True, index=False)
# exp_data_df.to_csv(output_path_readable, header=True, index=False)

# print(data)
# type(data)

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
