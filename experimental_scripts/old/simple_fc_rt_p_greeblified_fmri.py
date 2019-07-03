import os,sys,random,datetime,operator
from psychopy import visual,core,event,monitors,info,gui
from pandas import read_csv

import numpy as np
from random import shuffle

current_time = datetime.datetime.today().strftime("%m%d%Y_%H%M%S")
user_input_dict = {'CoAx ID [####]': '', 'Session Number [#]': '', 'Condition [##-##]': '', 'Run [#]': ''}
sub_inf_dlg = gui.DlgFromDict(user_input_dict, title='Subject information',
show=0, order=['CoAx ID [####]','Session Number [#]', 'Condition [##-##]', 'Run [#]'])


##this is problematic, will not get input. issue opened.
# from psychopy import prefs
# prefs.general['audioLib'] = ['pygame']
# from psychopy.sound import Sound

# set data path & collect information from experimenter
testing = int(input("Testing? "))

if testing is not 1 and testing is not 0:
    sys.exit('Enter 0 or 1.')

image_directory = os.getcwd() + '/images/'
exp_param_directory = os.getcwd() + '/experimental_parameters/'
analysis_directory = os.getcwd() + '/analysis/'
data_directory = os.getcwd() + '/data/'
# deterministic_exp_param_directory = os.getcwd() + '/experimental_parameters/deterministic_schedules/'

if testing:
    subj_id = -777
    session_n = 0
    condition = 8525
    run = 0
    exp_param_file = exp_param_directory + 'lc_0_test.csv'
    # exp_param_file = deterministic_exp_param_directory + 'test_highV.csv'

else:
    sub_inf_dlg.show()
    subj_id = user_input_dict['CoAx ID [####]']
    session_n = user_input_dict['Session Number [#]']
    condition = user_input_dict['Condition [##-##]'] #condition is coded as prob-lambda [65-10]
    run = user_input_dict['Run [#]']
    exp_param_file = exp_param_directory + subj_id + '_' + 'sess' + session_n + '_' + 'cond' + condition + '.csv'


    if not os.path.exists(exp_param_file):
        sys.exit("Experimental parameter file does not exist.")

if testing:
    output_file_name = str(subj_id) + '_' + 'sess' + str(session_n) + '_' + 'cond' + str(condition)
else:
    output_file_name = subj_id + '_' + 'sess' + session_n + '_' + condition + '_' + 'cond' + current_time

output_path = data_directory + output_file_name + ".json"
run_info_path = os.getcwd() + '/data/' + output_file_name + "_runInfo.json"

output_path_readable = data_directory + output_file_name + ".csv"
run_info_path_readable = os.getcwd() + '/data/' + output_file_name + "_runInfo.csv"

if not testing and os.path.exists(output_path):
    sys.exit(output_file_name + " already exists! Overwrite danger...Exiting.")


#specify constants
exp_param = read_csv(exp_param_file, header=0)
#strip whitespace from column names
exp_param.columns = exp_param.columns.str.strip()


reward_t1 = np.round(exp_param.r_t1.values,2).astype('int')
reward_t2 = np.round(exp_param.r_t2.values,2).astype('int')


rewards = np.transpose(np.array([reward_t1,reward_t2]))
max_reward_idx = np.argmax(rewards,1)
min_reward_idx = np.argmin(rewards,1)
n_trials = len(exp_param.cp)
n_test_trials = 4 #needs to be divisible by 2

if testing:
    n_trials = n_test_trials

trial_list = list(np.arange(0, n_trials))

total_reward = (n_trials // 2)
response_failure_reward = -5

#this narrative will have to change
instructions_p1 = ("You're going on a treasure hunt! You will start with " + str(total_reward) + " points, and you'll be able to pay a point to ask one of two greebles if they have money. When you query one of these greebles, you will get a certain number of points, depending on their identity. However, asking the same greeble for money will not always give you the same amount, and each choice costs one coin. \n\nAfter making your choice, you will receive feedback about how much money you have. Your goal is to make as much money as possible. \n\nPress the green button when you're ready to continue.")
instructions_p2 = ("Ask the left greeble for money by pressing the left button with your left thumb and ask the right greeble by pressing the right button with your right thumb. \n\nNote that if you choose too slowly or too quickly, you WILL NOT earn any coins. If your response is too slow, you'll see the circle in the center of the screen turn yellow to tell you to speed up. If your response is too fast, you'll see the circle turn red to tell you to slow down. Finally, remember to make your choice based on the identity of the greeble. \n\nPress the green button when you're ready to begin the hunt!")
slow_trial = ("Too slow! \nChoose quickly.")
fast_trial = ("Too fast! \nSlow down.")
between_run_inst = ("Feel free to take a break! \nPress the green button when you're ready to continue.")



#initialize dependent variables
rt_list = []
LR_choice_list = []
id_choice_list = []
value_accuracy_list = []
p_accuracy_list = []

subj_id_list = [subj_id] * n_trials
session_n_list = [session_n] * n_trials
condition_list = [condition] * n_trials
run_list = [run] * n_trials

#instantiate psychopy object instances
expTime_clock = core.Clock()
trialTime_clock = core.Clock()
rt_clock = core.Clock()

testing_monitor = monitors.Monitor('testing_computer')
testing_monitor.setSizePix = [1920,1080]
testing_monitor.saveMon()

screen_size = testing_monitor.setSizePix
center=[0,0]

if screen_size != testing_monitor.setSizePix:
    center[0] = (testing_monitor.setSizePix[0]/2) - (screen_size[0]/2)
    center[1] = (testing_monitor.setSizePix[1]/2) - (screen_size[1]/2)

window = visual.Window(size = screen_size, units='pix', monitor = testing_monitor, color = [-1,-1,-1], \
       colorSpace = 'rgb', blendMode = 'avg', useFBO = True, allowGUI = \
       False,fullscr=True, pos=center)

break_msg = visual.TextStim(win=window, units='pix',antialias='False', text=between_run_inst, wrapWidth=screen_size[0]-400, height=screen_size[1]/25)
inst_msg = visual.TextStim(win=window, units='pix',antialias='False', wrapWidth=screen_size[0]-400, height=screen_size[1]/25)
end_msg = visual.TextStim(win=window, units='pix', antialias='False', wrapWidth=screen_size[0]-400, height=screen_size[1]/25)
speed_msg = visual.TextStim(win=window, units='pix',antialias='False', text=slow_trial,  wrapWidth=screen_size[0]-400, height=screen_size[1]/15,
alignHoriz='center', colorSpace='rgb',color=[1,-1,-1], bold=True)

female_greeble = visual.ImageStim(window, image='./images/greebles/f1~11-v1.tif',units='pix',size=[screen_size[0]/5])
male_greeble= visual.ImageStim(window, image='./images/greebles/m1~11-v1.tif',units='pix',size=[screen_size[0]/5])
coin = visual.ImageStim(window, image='./images/coin.png',units='pix',size=[screen_size[0]/25], pos=[0,350])
treasure_chest = visual.ImageStim(window, image='./images/treasure_chest.png',units='pix',size=[screen_size[0]/14], pos=[800,screen_size[1]/3])


runtimeInfo = info.RunTimeInfo(author='kb',win=window,userProcsDetailed=False, verbose=True)
fixation_point_reward_total = visual.TextStim(win=window,units='pix',antialias='False',pos=[0,15], colorSpace='rgb', color=[1,1,1],height=screen_size[0]/20)

cost_per_decision = -1

cue_list = [female_greeble, male_greeble]
high_val_cue = []
low_val_cue = []
high_p_cue = []

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

#set timing variables
# fb_time = 1

# iti_min = 8
# iti_max = 20
# iti_min = 0.1
# iti_max = 1

# fast_penalty_time = 5 #this is insignificant relative to the ITI now. Can't punish them with time. might also interfere with run time.

rt_max = 1
rt_min = .1

mandatory_trial_time = 1.5
# mandatory_trial_time = 10

inst_key = 's'
left_key = 'f'
right_key = 'a'

escape_key = "escape"
trigger = "space" #confirm carat as trigger


error_color = [1,0,0] #SEVERE error: no response or too fast. -x points.
neutral_color = [1,1,1] #no change
good_color = [0,1,0] #earned points

#initalize lists
received_rewards = []
total_rewards = []
value_correct_choices = []
p_correct_choices = []
p_correct_ids = []

#timing lists
stim_onset_list = []
stim_offset_list = []
trial_onset_list = []

trial_time = []
cp_with_slow_fast = []
obs_cp_with_slow_fast = []
cp_list = exp_param.cp.values[0:n_trials].tolist()
obs_cp_list = exp_param.obs_cp.values[0:n_trials].tolist()
iti_list = exp_param.iti.values[0:n_trials].tolist()

high_p_cue_list = exp_param.p_id_solution[0:n_trials].tolist()

instruction_phase = False
print('Waiting for trigger...')
trigger_output = event.waitKeys(keyList=[trigger], clearEvents=True)
print('Trigger recieved.')

start_time = expTime_clock.getTime()

#give instructions
instruction_phase = True
while instruction_phase:
    window.flip()
    inst_msg.text = instructions_p1
    inst_msg.setAutoDraw(True)
    window.flip()
    inst_keys_p1 = event.waitKeys(keyList=[inst_key, escape_key])
    if escape_key in inst_keys_p1:
        sys.exit('escape key pressed.')

    inst_msg.text = instructions_p2
    inst_msg.setAutoDraw(True)
    window.flip()
    inst_keys_p2 = event.waitKeys(keyList=[inst_key,escape_key])
    if escape_key in inst_keys_p2:
        sys.exit('escape key pressed.')
    instruction_phase = False

inst_msg.setAutoDraw(False)
window.flip()


t=0

#breaks will be between runs. #so these need to be divided into runs (5 in total).

#need to timestamp every event.
expTime_clock.reset() #reset so that inst. time is not included
trialTime_clock.reset()
fixation_point_reward_total.text = str(total_reward)

n_runs = 5
n_trials_per_run = n_trials / n_runs
run_intervals = np.arange(0, n_trials, n_trials_per_run)



#present choices
while t < n_trials:

    #trial has started, get time
    trial_start = expTime_clock.getTime() - start_time
    trial_onset_list.append(trial_start)

    trialTime_clock.reset() #reset time

    fixation_point_reward_total.setAutoDraw(True)

    female_greeble.setPos([l_r_x_arr[t], 15])
    male_greeble.setPos([-l_r_x_arr[t], 15])

    cue_list[0].setAutoDraw(True)
    cue_list[1].setAutoDraw(True)
    window.flip()

    stim_onset_time = expTime_clock.getTime()
    stim_onset_list.append(stim_onset_time)

    rt_clock.reset()
    response=event.waitKeys(keyList=[left_key, right_key, escape_key],
      clearEvents=True, maxWait=rt_max)

    if response is None:
        rt = np.nan #no response
        choice = np.nan
        id_choice_list.append(np.nan)
        p_accuracy_list.append(np.nan)
        value_accuracy_list.append(np.nan)
    else:
        rt = rt_clock.getTime()
        choice=response[0][0]
        if escape_key in response:
            sys.exit('escape key pressed.')

    #reverse high value target according to reward vec.
    if obs_cp_list[t] == 1:
        cue_list.reverse()
    #record the identity of the high value target in ascii
    if cue_list[0] == female_greeble:
        high_val_cue.append(ord('f')) #female
        low_val_cue.append(ord('m'))
    elif cue_list[0] == male_greeble :
        high_val_cue.append(ord('m')) #male
        low_val_cue.append(ord('f'))

    if cue_list[0].pos[0] == left_pos_x: #if the pos. of the first (high val) cue in the list is left, then left key is correct
        value_correct_choice = left_key
        value_correct_choices.append(ord('L'))
    else:
        value_correct_choice = right_key #else, right key is correct
        value_correct_choices.append(ord('R'))

    #record the identity of the high p(r) target in ascii
    if high_p_cue_list[t] == ord('f'):
        high_p_cue.append(ord('f')) #female
    elif high_p_cue_list[t] == ord('m'):
        high_p_cue.append(ord('m')) #male

    if (high_val_cue[t] == high_p_cue_list[t]) & (cue_list[0].pos[0] == left_pos_x):  #find the left-right soln. for the p_id_soln
        p_correct_choice = left_key
        p_correct_choices.append(ord('L'))
        p_correct_ids.append(high_val_cue[t])

    elif (high_val_cue[t] != high_p_cue_list[t]) & (cue_list[0].pos[0] == left_pos_x):
        p_correct_choice = right_key
        p_correct_choices.append(ord('R'))
        p_correct_ids.append(low_val_cue[t])

    elif (high_val_cue[t] == high_p_cue_list[t]) & (cue_list[0].pos[0] == right_pos_x):
        p_correct_choice = right_key
        p_correct_choices.append(ord('R'))
        p_correct_ids.append(high_val_cue[t])

    elif (high_val_cue[t] != high_p_cue_list[t]) & (cue_list[0].pos[0] == right_pos_x):
        p_correct_choice = left_key
        p_correct_choices.append(ord('L'))
        p_correct_ids.append(low_val_cue[t])

    if choice == left_key:
        LR_choice_list.append(ord('L'))
    elif choice == right_key:
        LR_choice_list.append(ord('R'))
    elif np.isnan(choice):
        LR_choice_list.append(np.nan)


    if rt < rt_max and rt > rt_min:
        if choice == value_correct_choice:
            id_choice_list.append(high_val_cue[t])
            received_rewards.append(rewards[t,max_reward_idx[t]])
            total_reward += rewards[t,max_reward_idx[t]]
            fixation_point_reward_total.color = good_color
            window.flip()


        elif choice != value_correct_choice:
            id_choice_list.append(low_val_cue[t])
            received_rewards.append(rewards[t,min_reward_idx[t]])
            total_reward += rewards[t,min_reward_idx[t]]
            fixation_point_reward_total.color = error_color
            window.flip()

    elif rt >= rt_max or rt <= rt_min:
        if choice == value_correct_choice:
            id_choice_list.append(high_val_cue[t])
        elif choice != value_correct_choice:
            id_choice_list.append(low_val_cue[t])
        received_rewards.append(0)
        total_reward += response_failure_reward
        fixation_point_reward_total.color = error_color
        window.flip()

    elif np.isnan(rt):
        received_rewards.append(0)
        total_reward += response_failure_reward
        fixation_point_reward_total.color = error_color
        window.flip()


    fixation_point_reward_total.text = str("{:,}".format(total_reward))
    window.flip()

    total_rewards.append(total_reward)
    rt_list.append(rt)


    if choice in [left_key, right_key]:
        value_accuracy_list.append(choice == value_correct_choice)
        p_accuracy_list.append(choice == p_correct_choice)

    core.wait(mandatory_trial_time - trialTime_clock.getTime()) #wait until mandatory trial time has passed

    cue_list[0].setAutoDraw(False)
    cue_list[1].setAutoDraw(False)

    trial_time.append(trialTime_clock.getTime()) #trial time will always be set, sanity check

    # core.wait(fb_time) #wait for feedback time

    #jitter iti & continue to show bank as fixation point
    fixation_point_reward_total.color = neutral_color
    window.flip()
    stim_offset_time = expTime_clock.getTime()
    stim_offset_list.append(stim_offset_time)

    core.wait(iti_list[t])
    window.flip()

    t+=1

fixation_point_reward_total.setAutoDraw(False)
total_exp_time = expTime_clock.getTime()
stimulus_duration_list = list(map(operator.sub, stim_offset_list, stim_onset_list))

print(stimulus_duration_list, stim_offset_list, stim_onset_list, trial_list, subj_id_list, session_n_list, condition_list, run_list)

#save data
header = ('trial, subj_id, session_n, condition, run, LR_choice, value_accuracy, value_LR_solution, reward,' +
'cumulative_reward, rt, total_trial_time, iti, cp_list, obs_cp_list,high_val_cue,' +
 'high_p_cue, p_accuracy, p_LR_solution, p_id_solution, id_choice, stim_duration, stim_onset, stim_offset')

data = np.transpose(np.matrix((trial_list,subj_id_list, session_n_list, condition_list, run_list, LR_choice_list, value_accuracy_list, value_correct_choices,
 received_rewards, total_rewards, rt_list, trial_time, iti_list, cp_list,
  obs_cp_list, high_val_cue, high_p_cue, p_accuracy_list, p_correct_choices, p_correct_ids, id_choice_list, stimulus_duration_list, stim_onset_list, stim_offset_list)))

# print(data)
# print(type(data[1,:]))


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
end_msg.text = ("Awesome! You have " + fixation_point_reward_total.text + " coins. \nLet the experimenter know that you're finished.")
np.savetxt(output_path_readable, data, header=header, delimiter=',',comments='')
np.savetxt(run_info_path_readable,runtime_data, header=runtime_header,delimiter=',',comments='',fmt="%s")

#dismiss participant
instruction_phase = True
while instruction_phase:
    end_msg.setAutoDraw(True)
    window.flip()
    end_keys = event.waitKeys(keyList=[escape_key])
    sys.exit('escape key pressed.')
    instruction_phase = False
    window.flip()

end_msg.setAutoDraw(False)
window.flip()
window.close()
