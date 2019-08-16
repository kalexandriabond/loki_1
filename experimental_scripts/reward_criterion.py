import os,sys,random,datetime,operator
from psychopy import visual,core,event,monitors,info,gui
from pandas import read_csv, DataFrame
from psychopy.tools.colorspacetools import rgb2dklCart
import numpy as np
from random import shuffle

current_time = datetime.datetime.today().strftime("%m%d%Y_%H%M%S")
user_input_dict = { 'CoAx ID [####]': ''}
sub_inf_dlg = gui.DlgFromDict(user_input_dict, title='Subject information',
show=0, order=[ 'CoAx ID [####]'])


# set data path & collect information from experimenter
testing = int(input("Testing? "))
lab_testing = int(input("Testing in the lab? "))


if testing is not 1 and testing is not 0:
    sys.exit('Enter 0 or 1.')

parent_directory = os.path.dirname(os.getcwd())

image_directory = parent_directory + '/images/'
exp_param_directory = parent_directory + '/experimental_parameters/criterion_parameters/reward_criterion_parameters/'
data_directory = parent_directory + '/data/BIDS/'
run_info_directory = parent_directory + '/data/run_info_data/'

# deterministic_exp_param_directory = os.getcwd() + '/experimental_parameters/deterministic_schedules/'

session_n = 0

if testing:
    subj_id = 999
else:
    sub_inf_dlg.show()
    subj_id = int(float(user_input_dict['CoAx ID [####]']))

exp_param_file = exp_param_directory + str(subj_id) + '_reward_criterion_9510.csv'

if not os.path.exists(exp_param_file):
    sys.exit("Experimental parameter file does not exist.")

subj_directory = data_directory + "sub-" + "{:04d}".format(subj_id) + "/"
session_directory = subj_directory + "ses-" + "{:02d}".format(session_n) + "/"

behavioral_directory = session_directory + "beh/"

directories = list([behavioral_directory])

for dir in directories:
    if not os.path.exists(dir):
        os.makedirs(dir)


output_file_name = (
    "sub-"
    + "{:04d}".format(subj_id)
    + "_"
    + "ses"
    + "{:02d}".format(session_n)
    + "_"
    + "task-"
    + "reward-criterion"
    + "_"
    + str(current_time)
)


run_info_path = run_info_directory + output_file_name + "_runInfo.csv"

output_path = behavioral_directory + output_file_name + ".tsv"

if not testing and os.path.exists(output_path):
    sys.exit(output_file_name + " already exists! Overwrite danger...Exiting.")

#specify constants
exp_param = read_csv(exp_param_file, header=0)
#strip whitespace from column names
exp_param.columns = exp_param.columns.str.strip()

reward_t0 = np.round(exp_param.r_t0.values,2).astype('int')
reward_t1 = np.round(exp_param.r_t1.values,2).astype('int')


rewards = np.transpose(np.array([reward_t0,reward_t1]))
max_reward_idx = np.argmax(rewards,1)
min_reward_idx = np.argmin(rewards,1)
n_trials = len(exp_param.cp)
epoch_length = exp_param.epoch_length.tolist()
epoch_trial = exp_param.epoch_trial.tolist()
epoch_number = exp_param.epoch_number.tolist()

f_image = exp_param.f_image.tolist()
m_image = exp_param.m_image.tolist()


n_test_trials = n_trials #needs to be divisible by 2

if testing:
    n_trials = n_test_trials

trial_list = list(np.arange(0, n_trials))

total_reward = (n_trials // 2)
response_failure_reward = -5

vertical_txt_break = "\n"*10
small_vertical_txt_break = "\n"*2
horiz_txt_break = "\t"*5

instructions_p1 = ("You are going on a treasure hunt! You will start with " + str(total_reward) +  " coins, and you will be able to pay a coin " +
"to ask one of two greebles if they have money. On each trial you will meet two greebles: one is female, one is male." + small_vertical_txt_break + "This is a female." + horiz_txt_break +
"This is a male." + vertical_txt_break +
"Note how their features differ. The female greeble has a downward facing appendage, whereas the male greeble has an upward facing appendage.\n\nPress the left button when you're ready to continue to the next instruction screen.  ")

instructions_p2 = ("On each trial you can ask either the male or female greeble for money. If the greeble you ask chooses to give you money, " +
"he or she will give you a certain number of coins to add to your bank.\n\nSometimes females will give coins more often. Sometimes males will give coins more often. " +
"Your goal is simply to make as much money as possible by learning which type of greeble will give you more money. ")

instructions_p3 = ("The total amount of money that you have is shown as a bank at the center of the screen:" + small_vertical_txt_break*7 + "If you earn money, the bank will turn green. " +
"If you lose money, the bank will turn yellow.\n\nIf you choose too slowly or too quickly, you will lose 5 points and the bank at the center of the screen will turn red.\n\nEach point you earn will correspond to one real cent that you will be paid in addition to your hourly pay. So do the best you can!")


instructions_p4 = ("To ask the left greeble for money, press the left button with your left thumb. " +
"To ask the right greeble for money press the right button with your right thumb.\n\n" +
"Between trials, please focus your eyes on the bank.\n\nPress the left button when you are ready to begin the hunt!")


instructions_p5 = ("Do your best to focus on the bank. Press the left button to start the task.")


slow_trial = ("Too slow! \nChoose quickly.")
fast_trial = ("Too fast! \nSlow down.")
between_run_inst = ("Feel free to take a break! \nPress the left button when you're ready to continue.")



#initialize dependent variables
rt_list = []
LR_choice_list = []
id_choice_list = []
value_accuracy_list = []
p_accuracy_list = []

subj_id_list = [subj_id] * n_trials

#instantiate psychopy object instances
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
dkl_orange = (luminance,45,contrast)
dkl_yellow = (luminance, 80, contrast)

dkl_blue = (luminance, 225, contrast)


greeble_color = dkl_purple
inst_color = [1,1,1]
speed_message_color = dkl_red

window = visual.Window(size = screen_size, units='pix', monitor = mon, color = dkl_blue, \
       colorSpace = 'dkl', blendMode = 'avg', useFBO = True, allowGUI = \
       False,fullscr=True, pos=center, screen=0)

break_msg = visual.TextStim(win=window, units='pix',antialias='False', text=between_run_inst, wrapWidth=window_size[0]-400, height=window_size[1]/32)
inst_msg = visual.TextStim(win=window, units='pix',antialias='False',colorSpace='dkl', color=[90,0,1], wrapWidth=window_size[0]-400, height=window_size[1]/32)
end_msg = visual.TextStim(win=window, units='pix', antialias='False', wrapWidth=window_size[0]-400,colorSpace='dkl', color=[90,0,1], height=window_size[1]/32)
speed_msg = visual.TextStim(win=window, units='pix',antialias='False', text=slow_trial,  wrapWidth=window_size[0]-400, height=window_size[1]/15,
alignHoriz='center', colorSpace='rgb',color=[1,-1,-1], bold=True)


#m/f from different families to emphasize dimension of interest (sex)
female_greeble_sample = visual.ImageStim(window, image=image_directory + 'symm_greebles/' + 'f1~11-v1.tif',units='pix',size=[window_size[0]/5], colorSpace='dkl', color=greeble_color)
male_greeble_sample = visual.ImageStim(window, image=image_directory + 'symm_greebles/' + 'm2~21-v1.tif',units='pix',size=[window_size[0]/5], colorSpace='dkl', color=greeble_color)

#take in an image list
female_greeble = visual.ImageStim(window, image=image_directory + 'symm_greebles/' + 'f1~11-v1.tif',units='pix',size=[window_size[0]/4],colorSpace='dkl', color=greeble_color)
male_greeble = visual.ImageStim(window, image=image_directory + 'symm_greebles/' +'m1~11-v1.tif',units='pix',size=[window_size[0]/4],colorSpace='dkl', color=greeble_color)

runtimeInfo = info.RunTimeInfo(author='kb',win=window,userProcsDetailed=False, verbose=True)
fixation_point_reward_total = visual.TextStim(win=window,units='pix',antialias='False',pos=[0,15], colorSpace='dkl', color=dkl_gray,height=window_size[0]/20)


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

#define target coordinates
left_pos_x = -window_size[0]/5
right_pos_x = window_size[0]/5


n_reps = n_trials//2
l_x = np.tile(left_pos_x, n_reps)
r_x = np.tile(right_pos_x, n_reps)
l_r_x_arr = np.concatenate((l_x, r_x))

#shuffle target coordinates
np.random.seed()
np.random.shuffle(l_r_x_arr)


rt_max = 0.75
rt_min = .1

mandatory_trial_time = 1.5

if lab_testing:
    left_key = 'f'
    right_key = 'a'
    inst_key = 's'
else:
    left_key = "2"
    right_key = "1"
    inst_key = left_key

escape_key = "escape"


severe_error_color = dkl_red #SEVERE error: no response or too fast. -x points.
error_color = dkl_yellow #SEVERE error: no response or too fast. -x points.

neutral_color = dkl_gray #no change
good_color = dkl_green #earned points


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

high_p_cue_list = exp_param.p_id_solution[:n_trials].tolist()
f_images = exp_param.f_image[:n_trials].tolist()
m_images = exp_param.m_image[:n_trials].tolist()



m_image_list = [image_directory+ 'symm_greebles/'+str(m_image) for m_image in m_images]
f_image_list = [image_directory+ 'symm_greebles/'+str(f_image) for f_image in f_images]


#give instructions
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
        sys.exit('escape key pressed.')

    inst_msg.text = instructions_p2
    window.flip()
    inst_keys_p2 = event.waitKeys(keyList=[inst_key,escape_key])
    if escape_key in inst_keys_p2:
        sys.exit('escape key pressed.')

    inst_msg.text = instructions_p3
    female_greeble_sample.setPos([-200, 75])
    male_greeble_sample.setPos([200, 75])
    female_greeble_sample.draw()
    male_greeble_sample.draw()
    fixation_point_reward_total.text = str(total_reward)
    fixation_point_reward_total.setPos([0, 75])
    fixation_point_reward_total.draw()
    window.flip()
    inst_keys_p3 = event.waitKeys(keyList=[inst_key,escape_key])
    if escape_key in inst_keys_p3:
        sys.exit('escape key pressed.')

    inst_msg.text = instructions_p4
    window.flip()
    inst_keys_p4 = event.waitKeys(keyList=[inst_key,escape_key])
    if escape_key in inst_keys_p4:
        sys.exit('escape key pressed.')


    inst_msg.text = instructions_p5
    window.flip()
    inst_keys_p4 = event.waitKeys(keyList=[inst_key,escape_key])
    if escape_key in inst_keys_p4:
        sys.exit('escape key pressed.')
    instruction_phase = False

inst_msg.setAutoDraw(False)
window.flip()


t=0


expTime_clock.reset()
trialTime_clock.reset()
fixation_point_reward_total.text = str(total_reward)


start_time = expTime_clock.getTime()

acc_window = 20
criterion = 0.8


#present choices
while t < n_trials:

    #reverse high value target according to reward vec.
    if obs_cp_list[t] == 1:
        cue_list.reverse()

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



    if cue_list[0] == female_greeble:
        high_val_cue.append(ord('f')) #female
        print(high_val_cue)
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


    if t >= acc_window:
        if (sum(p_accuracy_list[-acc_window:])/acc_window) >= criterion:
            inst_msg.setAutoDraw(False)
            cue_list[0].setAutoDraw(False)
            cue_list[1].setAutoDraw(False)
            core.wait(mandatory_trial_time - trialTime_clock.getTime()) #wait until mandatory trial time has passed
            #jitter iti & continue to show bank as fixation point
            fixation_point_reward_total.color = neutral_color
            window.flip()
            stim_offset_time = expTime_clock.getTime()
            stim_offset_list.append(stim_offset_time)
            core.wait(iti_list[t])
            break

    inst_msg.setAutoDraw(False)
    cue_list[0].setAutoDraw(False)
    cue_list[1].setAutoDraw(False)
    core.wait(mandatory_trial_time - trialTime_clock.getTime()) #wait until mandatory trial time has passed
    #jitter iti & continue to show bank as fixation point
    fixation_point_reward_total.color = neutral_color
    window.flip()
    stim_offset_time = expTime_clock.getTime()
    stim_offset_list.append(stim_offset_time)
    core.wait(iti_list[t])

    t+=1

fixation_point_reward_total.setAutoDraw(False)
total_exp_time = expTime_clock.getTime()
stimulus_duration_list = list(map(operator.sub, stim_offset_list, stim_onset_list))

#save tsv events data
events_header = ('stim_onset, stim_duration, trial_type, rt, accuracy, epoch_length,\
epoch_trial, epoch_number')
events_data = np.transpose(np.matrix((stim_onset_list[:t], stimulus_duration_list[:t],
    trial_list[:t], rt_list[:t], p_accuracy_list[:t], epoch_length[:t], epoch_trial[:t],
    epoch_number[:t])))
np.savetxt(output_path, events_data, header=events_header, delimiter='\t',comments='')


runtime_header = ("psychopy_version, python_version, pythonScipyVersion,\
pyglet_version, pygame_version, numpy_version, wx_version, window_refresh_time_avg_ms,\
begin_time, exp_dir, last_sys_reboot, system_platform, internet_access,\
 total_exp_time")
runtime_data = np.matrix((str(runtimeInfo['psychopyVersion']), str(runtimeInfo['pythonVersion']),
str(runtimeInfo['pythonScipyVersion']),str(runtimeInfo['pythonPygletVersion']),
str(runtimeInfo['pythonPygameVersion']),str(runtimeInfo['pythonNumpyVersion']),str(runtimeInfo['pythonWxVersion']),
str(runtimeInfo['windowRefreshTimeAvg_ms']), str(runtimeInfo['experimentRunTime']),
str(runtimeInfo['experimentScript.directory']),str(runtimeInfo['systemRebooted']),
str(runtimeInfo['systemPlatform']),str(runtimeInfo['systemHaveInternetAccess']), total_exp_time))
np.savetxt(run_info_path,runtime_data, header=runtime_header,delimiter=',',comments='',fmt="%s")



end_msg_text = ("Awesome! You have " + fixation_point_reward_total.text + " coins. \nLet the experimenter know that you're finished.")
end_msg.text = end_msg_text


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

window.close()
core.quit()
