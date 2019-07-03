import os,sys,random,datetime,operator
from psychopy import visual,core,event,monitors,info,gui
from pandas import read_csv, DataFrame
from psychopy.tools.colorspacetools import rgb2dklCart
import numpy as np
from random import shuffle


current_time = datetime.datetime.today().strftime("%m%d%Y_%H%M%S")
user_input_dict = {'Scanning?': '', 'CoAx ID [####]': '', 'Session Number [#]': '', 'Condition [##-##]': '', 'Run [#]': ''}
sub_inf_dlg = gui.DlgFromDict(user_input_dict, title='Subject information',
show=0, order=['Scanning?', 'CoAx ID [####]','Session Number [#]', 'Condition [##-##]', 'Run [#]'])


##this is problematic, will not get input. issue opened.
# from psychopy import prefs
# prefs.general['audioLib'] = ['pygame']
# from psychopy.sound import Sound

# set data path & collect information from experimenter
testing = int(input("Testing? "))
test_scan = int(input("Testing scanning config.? "))
button_box = int(input("Using button box? "))

if testing is not 1 and testing is not 0:
    sys.exit('Enter 0 or 1.')

image_directory = os.getcwd() + '/images/symm_greebles/'
exp_param_directory = os.getcwd() + '/experimental_parameters/'
analysis_directory = os.getcwd() + '/analysis/'
data_directory = os.getcwd() + '/data/'
# deterministic_exp_param_directory = os.getcwd() + '/experimental_parameters/deterministic_schedules/'

if testing:
    if test_scan:
        scanning = 1
    else:
        scanning = 0
    # subj_id = -777
    # session_n = 0
    # condition = 8515
    # run = 0
    subj_id = -1
    session_n = 0
    condition = 8515
    run = 0
    exp_param_file = exp_param_directory + 'lc_0_test.csv'
    passive_param_file = exp_param_directory + 'passive_viewing_test.csv'
    # exp_param_file = deterministic_exp_param_directory + 'test_highV.csv'

else:
    sub_inf_dlg.show()
    scanning = user_input_dict['Scanning?']
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

passive_param = read_csv(passive_param_file, header=0)
passive_param.columns = passive_param.columns.str.strip()



reward_t1 = np.round(exp_param.r_t1.values,2).astype('int')
reward_t2 = np.round(exp_param.r_t2.values,2).astype('int')


rewards = np.transpose(np.array([reward_t1,reward_t2]))
max_reward_idx = np.argmax(rewards,1)
min_reward_idx = np.argmin(rewards,1)
n_trials = len(exp_param.cp)
n_test_trials = n_trials #needs to be divisible by 2

if testing:
    n_trials = n_test_trials

trial_list = list(np.arange(0, n_trials))

total_reward = (n_trials // 2)
response_failure_reward = -5

vertical_txt_break = "\n"*7
small_vertical_txt_break = "\n"*2
horiz_txt_break = "\t"*5


instructions_p1 = ("You are going on a treasure hunt! You will start with " + str(total_reward) +  " coins, and you will be able to pay a coin " +
"to ask one of two greebles if they have money. On each trial you will meet two greebles: one is female, one is male." + small_vertical_txt_break + "This is a female." + horiz_txt_break +
"This is a male." + vertical_txt_break +
"Note how their features differ. The female greeble has a downward facing appendage, whereas the male greeble has an upward facing appendage.\n\nPress the green button when you're ready to continue to the next instruction screen.  ")

# instructions_p1 = ("You are going on a treasure hunt! You will start with " + str(total_reward) +  " coins, and you will be able " +
# "to ask one of two greebles if they have money. On each trial you will meet two greebles: one is female, one is male." + small_vertical_txt_break + "This is a female." + horiz_txt_break +
# "This is a male." + vertical_txt_break +
# "Note how their features differ. The female greeble has a downward facing appendage, whereas the male greeble has an upward facing appendage.\n\n Press the green button when you're ready to continue to the next instruction screen.  ")


#task to ask them to choose the male/female?

instructions_p2 = ("On each trial you can ask either the male or female greeble for money. If the greeble you ask chooses to give you money, " +
"he or she will give you a certain number of coins to add to your bank.\n\nSometimes females will give coins more often. Sometimes males will give coins more often. " +
"Your goal is simply to make as much money as possible by learning which type of greeble will give you more money. ")

instructions_p3 = ("The total amount of money that you have is shown as a bank at the center of the screen:" + small_vertical_txt_break*5 + "If you earn money, the bank will turn green. " +
"If you lose money, the bank will turn yellow.\n\nIf you choose too slowly or too quickly, you will lose 5 points and the bank at the center of the screen will turn red.\n")

# instructions_p3 = ("The total amount of money that you have is shown as a bank at the center of the screen:" + small_vertical_txt_break*5 + " If you earn money, the bank will turn green. " +
# "If your points do not change, the bank will remain white.\n\n If you choose too slowly or too quickly, you WILL NOT earn any coins. " +
# "Instead, you will lose 5 points and the bank at the center of the screen will turn red.\n")

# instructions_p3 = ("The total amount of money that you have is shown as a bank at the center of the screen:" + small_vertical_txt_break*5 + " If you earn money, the bank will turn green. " +
# "If your points do not change, the bank will remain white.\n\n If you lose money, the bank will turn red. If you choose too slowly or too quickly, you WILL NOT earn any coins. " +
# "Instead, you will lose 5 points and the bank at the center of the screen will turn red.\n") #should they still pay a coin?


instructions_p4 = ("To ask the left greeble for money, press the left (yellow) button with your left thumb. " +
"To ask the right greeble for money press the right (red) button with your right thumb.\n\n" +
"Between trials, please focus your eyes on the bank.\n\nPress the green button when you are ready to begin the hunt!")


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
testing_monitor.setSizePix = [1280,1024]
# testing_monitor.setSizePix = [1920,1080]
testing_monitor.saveMon()

screen_size = testing_monitor.setSizePix
center=[0,0]

if screen_size != testing_monitor.setSizePix:
    center[0] = (testing_monitor.setSizePix[0]/2) - (screen_size[0]/2)
    center[1] = (testing_monitor.setSizePix[1]/2) - (screen_size[1]/2)

window = visual.Window(size = screen_size, units='pix', monitor = testing_monitor, color = [-1,-1,-1], \
       colorSpace = 'rgb', blendMode = 'avg', useFBO = True, allowGUI = \
       False,fullscr=True, pos=center, screen=0)

conversionMatrix = testing_monitor.getDKL_RGB(RECOMPUTE=False) #for isoluminance

break_msg = visual.TextStim(win=window, units='pix',antialias='False', text=between_run_inst, wrapWidth=screen_size[0]-400, height=screen_size[1]/32)
inst_msg = visual.TextStim(win=window, units='pix',antialias='False',colorSpace='dkl', color=[90,0,1], wrapWidth=screen_size[0]-400, height=screen_size[1]/32)
end_msg = visual.TextStim(win=window, units='pix', antialias='False', wrapWidth=screen_size[0]-400,colorSpace='dkl', color=[90,0,1], height=screen_size[1]/32)
speed_msg = visual.TextStim(win=window, units='pix',antialias='False', text=slow_trial,  wrapWidth=screen_size[0]-400, height=screen_size[1]/15,
alignHoriz='center', colorSpace='rgb',color=[1,-1,-1], bold=True)

#m/f from different families to emphasize dimension of interest (sex)
female_greeble_sample = visual.ImageStim(window, image=image_directory + 'f1~11-v1.tif',units='pix',size=[screen_size[0]/5], colorSpace='dkl', color=[90,0,1])
male_greeble_sample = visual.ImageStim(window, image=image_directory + 'm2~21-v1.tif',units='pix',size=[screen_size[0]/5], colorSpace='dkl', color=[90,0,1])

bank_sample = visual.ImageStim(window, image='./images/bank_sample.png',units='pix',size=None,colorSpace='dkl', color=[90,0,1])




#take in an image list
female_greeble = visual.ImageStim(window, image=image_directory + 'f1~11-v1.tif',units='pix',size=[screen_size[0]/4])
male_greeble = visual.ImageStim(window, image=image_directory + 'm1~11-v1.tif',units='pix',size=[screen_size[0]/4])
passive_greeble = visual.ImageStim(window, image=image_directory + 'm1~11-v1.tif',units='pix',size=[screen_size[0]/5])

runtimeInfo = info.RunTimeInfo(author='kb',win=window,userProcsDetailed=False, verbose=True)
fixation_point_reward_total = visual.TextStim(win=window,units='pix',antialias='False',pos=[0,15], colorSpace='rgb', color=[1,1,1],height=screen_size[0]/20)

cost_per_decision = -1
#should we actually have a cost per decision? then they'll never have a white bank. not sure of the point of that fb inst.

cue_list = [female_greeble, male_greeble]
holdout_cue_list = [female_greeble, male_greeble]

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

# rt_max = 1
rt_max = 1.2
rt_min = .1

mandatory_trial_time = 1.5
# mandatory_trial_time = 10


inst_key = 's'

if button_box:
    left_key = 'f'
    right_key = 'a'
else:
    left_key = 'a'
    right_key = 'f'

escape_key = 'escape'
trigger = 'asciicircum' #this is the caret code


severe_error_color = [1,0,0] #SEVERE error: no response or too fast. -x points.
error_color = [1,1,0] #SEVERE error: no response or too fast. -x points.


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
abs_response_time_list = []

trial_time = []
cp_with_slow_fast = []
obs_cp_with_slow_fast = []
cp_list = exp_param.cp.values[:n_trials].tolist()
obs_cp_list = exp_param.obs_cp.values[:n_trials].tolist()
iti_list = exp_param.iti.values[:n_trials].tolist()

high_p_cue_list = exp_param.p_id_solution[0:n_trials].tolist()
f_images = exp_param.f_image[:n_trials].tolist()
m_images = exp_param.m_image[:n_trials].tolist()

passive_images = passive_param.image[:n_trials].tolist()

#this works! just need to set the image list properly now. need to
#write sampling procedure to span families / genders appropriately
#write selections to exp_param file for each trial
m_image_list = [image_directory+str(m_image) for m_image in m_images]
f_image_list = [image_directory+str(f_image) for f_image in f_images]

passive_list = [image_directory+str(image) for image in passive_images]

#
# #Change the picture from RGB to DKL, an isoluminant color space
# dkl_m_image_list = [rgb2dklCart(m_image_list[t], conversionMatrix=conversionMatrix) for t in range(n_trials)]
# dkl_f_image_list = [rgb2dklCart(f_image_list[t], conversionMatrix=conversionMatrix) for t in range(n_trials)]

#give instructions
instruction_phase = True
while instruction_phase:
    inst_msg.text = instructions_p1
    inst_msg.setAutoDraw(True)
    female_greeble_sample.setPos([-300, -10])
    male_greeble_sample.setPos([200, -10])
    female_greeble_sample.draw()
    male_greeble_sample.draw()
    window.flip()
    inst_keys_p1 = event.waitKeys(keyList=[inst_key, escape_key])
    if escape_key in inst_keys_p1:
        sys.exit('escape key pressed.')

    inst_msg.text = instructions_p2
    window.flip()
    inst_keys_p2 = event.waitKeys(keyList=[inst_key,escape_key])
    if escape_key in inst_keys_p2:
        sys.exit('escape key pressed.')


    inst_msg.text = instructions_p3
    bank_sample.setPos([-80, 120])
    bank_sample.draw()
    window.flip()
    inst_keys_p3 = event.waitKeys(keyList=[inst_key,escape_key])
    if escape_key in inst_keys_p3:
        sys.exit('escape key pressed.')


    inst_msg.text = instructions_p4
    window.flip()
    inst_keys_p4 = event.waitKeys(keyList=[inst_key,escape_key])
    if escape_key in inst_keys_p4:
        sys.exit('escape key pressed.')
    instruction_phase = False

inst_msg.setAutoDraw(False)
window.flip()


# while t < n_trials:
#     #trial has started, get time
#     passive_trial_start = expTime_clock.getTime() - start_time
#     passive_trial_onset_list.append(passive_trial_start)
#
#     trialTime_clock.reset() #reset time
#
#     fixation_point_reward_total.setAutoDraw(True) #make new fixation point
#
#     passive_greeble.setPos([0, 0])
#
#     passive_greeble.setImage(passive_list[t])
#
#     passive_greeble.draw()
#     window.flip()
#
#     stim_onset_time = expTime_clock.getTime()
#     stim_onset_list.append(stim_onset_time)
#
#     rt_clock.reset()
#     response=event.waitKeys(keyList=[left_key, right_key, escape_key],
#       clearEvents=True, maxWait=rt_max)
#
#     abs_response_time = expTime_clock.getTime()
#     abs_response_time_list.append(abs_response_time)
#
#
#     if response is None:
#         rt = np.nan #no response
#         choice = np.nan
#         id_choice_list.append(np.nan)
#         p_accuracy_list.append(np.nan)
#         value_accuracy_list.append(np.nan)
#     else:
#         rt = rt_clock.getTime()
#         choice=response[0][0]
#         if escape_key in response:
#             sys.exit('escape key pressed.')


t=0

#breaks will be between runs. #so these need to be divided into runs (5 in total).

#need to timestamp every event.
expTime_clock.reset() #reset so that inst. time is not included
trialTime_clock.reset()
fixation_point_reward_total.text = str(total_reward)

# n_runs = 5
# n_trials_per_run = n_trials / n_runs
# run_intervals = np.arange(0, n_trials, n_trials_per_run)

if scanning:
    inst_msg.text = 'Waiting for trigger...'
    inst_msg.draw()
    window.flip()
    trigger_output = event.waitKeys(keyList=[trigger, escape_key], clearEvents=True)
    # inst_msg.text = 'Trigger received.'
    # window.flip()
    # core.wait(1.5)
start_time = expTime_clock.getTime()

#present choices
while t < n_trials:

    #trial has started, get time
    trial_start = expTime_clock.getTime() - start_time
    trial_onset_list.append(trial_start)

    trialTime_clock.reset() #reset time

    fixation_point_reward_total.setAutoDraw(True)

    female_greeble.setPos([l_r_x_arr[t], 15])
    male_greeble.setPos([-l_r_x_arr[t], 15])

    female_greeble.setImage(f_image_list[t])
    male_greeble.setImage(m_image_list[t])

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

    #any reason to record the family of high v target?
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
            total_reward += rewards[t,min_reward_idx[t]] + cost_per_decision
            fixation_point_reward_total.color = error_color #think about this...
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
print(f_image_list)

#save data
header = ('trial, subj_id, session_n, condition, run, LR_choice, value_accuracy, value_LR_solution, reward,' +
'cumulative_reward, rt, total_trial_time, iti, cp_list, obs_cp_list,high_val_cue,' +
 'high_p_cue, p_accuracy, p_LR_solution, p_id_solution, id_choice, stim_duration, stim_onset, stim_offset, abs_response_time')

# df_header = ('trial, subj_id, session_n, condition, run, LR_choice, value_accuracy, value_LR_solution, reward,' +
# 'cumulative_reward, rt, total_trial_time, iti, cp_list, obs_cp_list,high_val_cue,' +
# 'high_p_cue, p_accuracy, p_LR_solution, p_id_solution, id_choice, stim_duration, stim_onset, stim_offset, abs_response_time, f_image, m_image')
#
data = np.transpose(np.matrix((trial_list,subj_id_list, session_n_list, condition_list, run_list, LR_choice_list, value_accuracy_list, value_correct_choices,
 received_rewards, total_rewards, rt_list, trial_time, iti_list, cp_list,
  obs_cp_list, high_val_cue, high_p_cue, p_accuracy_list, p_correct_choices,
   p_correct_ids, id_choice_list, stimulus_duration_list, stim_onset_list, stim_offset_list, abs_response_time_list)))


#test this in console
# df = DataFrame(np.column_stack((trial_list,subj_id_list, session_n_list, condition_list, run_list, LR_choice_list, value_accuracy_list, value_correct_choices,
#  received_rewards, total_rewards, rt_list, trial_time, iti_list, cp_list,
#   obs_cp_list, high_val_cue, high_p_cue, p_accuracy_list, p_correct_choices,
#    p_correct_ids, id_choice_list, stimulus_duration_list, stim_onset_list, stim_offset_list, abs_response_time_list, f_images, m_images)), columns = df_header)
#
#
# df.to_csv(output_path + '__init__df', index=False)
#make this into a df to capture image on each trial

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
np.savetxt(output_path_readable, data, header=header, delimiter=',',comments='')
np.savetxt(run_info_path_readable,runtime_data, header=runtime_header,delimiter=',',comments='',fmt="%s")

end_msg_text = ("Awesome! You have " + fixation_point_reward_total.text + " coins. \nLet the experimenter know that you're finished.")
run_end_msg_text = ('You have reached the end of the run.\n Please wait for the experimenter to continue.')
#dismiss participant
instruction_phase = True
while instruction_phase:
    if scanning:
        end_msg.text = run_end_msg_text
    else:
        end_msg.text = end_msg_text

    end_msg.draw()
    window.flip()
    end_keys = event.waitKeys(keyList=[escape_key])
    sys.exit('escape key pressed.')
    instruction_phase = False
    window.flip()

window.flip()
window.close()
