import os,numpy,sys,random,datetime,operator
from psychopy import visual,core,event,monitors,info,gui
from pandas import read_csv, DataFrame
from psychopy.tools.colorspacetools import rgb2dklCart, dkl2rgb
import numpy as np
from random import shuffle



current_time = datetime.datetime.today().strftime("%m%d%Y_%H%M%S")
user_input_dict = { 'CoAx ID [####]': '', 'Session Number [#]': ''}
sub_inf_dlg = gui.DlgFromDict(user_input_dict, title='Subject information',
show=0, order=[ 'CoAx ID [####]','Session Number [#]'])


# set data path & collect information from experimenter
testing = int(input("Testing? "))

if testing is not 1 and testing is not 0:
    sys.exit('Enter 0 or 1.')

parent_directory = os.path.dirname(os.getcwd())

image_directory = parent_directory + '/images/symm_greebles/'
exp_param_directory = parent_directory + '/experimental_parameters/criterion_parameters/perceptual_disc_criterion_parameters/'
analysis_directory = parent_directory + '/analysis/'
data_directory = parent_directory + '/data/BIDS/'

if testing:
    subj_id = 0
    exp_param_file = exp_param_directory + 'test_perceptual_criterion.csv'
else:
    sub_inf_dlg.show()
    subj_id = int(float(user_input_dict['CoAx ID [####]']))
    session_n = int(float(user_input_dict['Session Number [#]']))
    exp_param_file = exp_param_directory + str(subj_id) + '_sess' + str(session_n) + '_' + 'criterion'+'.csv'

    if not os.path.exists(exp_param_file):
        sys.exit("Experimental parameter file does not exist.")

if testing:
    output_file_name =  str(0) + '_' + 'criterion' + '_' + str(current_time)
else:
    output_file_name =  str(subj_id) + '_' + 'criterion' + '_' + str(current_time)


output_path = data_directory + output_file_name + ".json"

output_path_readable = data_directory + output_file_name + ".csv"

if not testing and os.path.exists(output_path):
    sys.exit(output_file_name + " already exists! Overwrite danger...Exiting.")


#specify constants
exp_param = read_csv(exp_param_file, header=0)
#strip whitespace from column names
exp_param.columns = exp_param.columns.str.strip()


n_trials = len(exp_param.trial)
n_test_trials = n_trials #needs to be divisible by 2

if testing:
    n_trials = n_test_trials

trial_list = list(np.arange(0, n_trials))

total_reward = (n_trials // 2)

vertical_txt_break = "\n"*10
small_vertical_txt_break = "\n"*2
horiz_txt_break = "\t"*5


instructions_p1 = ("You are going on a treasure hunt! You will start with a certain number of coins, and you will be able to pay a coin " +
"to ask one of two greebles if they have money. On each trial you will meet two greebles: one is female, one is male." + small_vertical_txt_break + "This is a female." + horiz_txt_break +
"This is a male." + vertical_txt_break +
"Note how their features differ. The female greeble has a downward facing appendage, whereas the male greeble has an upward facing appendage.\n\nPress the left button when you're ready to continue to the next instruction screen.  ")

instructions_p2 = ("So that you can earn the most money, we will start with a test of whether you can accurately identify the sex of each greeble. \n\nSpecifically, you will be asked to choose the greeble that you think is FEMALE. \n\n"
+"A fixation cross will be shown at the center of the screen. If you correctly choose the female greeble, the cross will turn green. " +
"If you incorrectly choose the male greeble, the cross will turn yellow. If you choose too slowly or too quickly, the cross will turn red and you will have to wait five seconds before you can proceed.\n\n" +
"To identify the left greeble as female, press the left button with your left thumb. " +
"To identify the right greeble as female, press the right button with your right thumb.\n\nPress the left button when you are ready to begin!")

instructions_p3 = ("Do your best to focus on the fixation cross. Press the left button to start the task.")


slow_trial = ("Too slow! \nChoose quickly.")
fast_trial = ("Too fast! \nSlow down.")

between_run_inst = ("Feel free to take a break! \nPress the left button when you're ready to continue.")



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

screen_size = (1920., 1080.)  # screen size in pixels
window_size = (1280., 800.)
mon = monitors.Monitor(
    "BOLD_display", width=79.7, distance=138,
)  # width and distance in cm
mon.setSizePix(screen_size)
mon.saveMon()

center = (0,0)



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
inst_color = [1,1,1]
speed_message_color = dkl_red

window = visual.Window(size = screen_size, units='pix', monitor = mon, color = dkl_blue, \
       colorSpace = 'dkl', blendMode = 'avg', useFBO = True, allowGUI = \
       False,fullscr=True, pos=center, screen=0)

inst_msg = visual.TextStim(win=window, units='pix',antialias='False',colorSpace='rgb', color=inst_color, wrapWidth=screen_size[0]-400, height=screen_size[1]/32)
end_msg = visual.TextStim(win=window, units='pix', antialias='False', wrapWidth=screen_size[0]-400,colorSpace='rgb', color=inst_color, height=screen_size[1]/32)
speed_msg = visual.TextStim(win=window, units='pix',antialias='False', text=slow_trial,  wrapWidth=screen_size[0]-400, height=screen_size[1]/15,
alignHoriz='center', colorSpace='dkl',color=speed_message_color, bold=False)

slow_trial = ("Too slow! \nChoose quickly.")
fast_trial = ("Too fast! \nSlow down. \nYou can continue in 5 seconds.")

#m/f from different families to emphasize dimension of interest (sex)
female_greeble_sample = visual.ImageStim(window, image=image_directory + 'f1~11-v1.tif',units='pix',size=[screen_size[0]/5], colorSpace='dkl', color=greeble_color)
male_greeble_sample = visual.ImageStim(window, image=image_directory + 'm2~21-v1.tif',units='pix',size=[screen_size[0]/5], colorSpace='dkl', color=greeble_color)

bank_sample = visual.ImageStim(window, image=parent_directory + '/images/bank_sample.png',units='pix',size=None,colorSpace='dkl', color=[90,0,1])


#take in an image list
female_greeble = visual.ImageStim(window, image=image_directory + 'f1~11-v1.tif',units='pix',size=[screen_size[0]/4],colorSpace='dkl', color=greeble_color)
male_greeble = visual.ImageStim(window, image=image_directory + 'm1~11-v1.tif',units='pix',size=[screen_size[0]/4],colorSpace='dkl', color=greeble_color)


fixation_cross = visual.TextStim(win=window,units='pix',text='+', antialias='False',pos=[0,15], colorSpace='dkl', color=dkl_gray, height=screen_size[0]/15)


cue_list = [female_greeble, male_greeble]


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
mandatory_trial_time = 1.5


acc_window = 20 #accuracy window for moving average
criterion = .95 #accuracy

response_failure_reward = -5


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
id_choice_accuracy_list = []
correct_key_choices = []

#timing lists
stim_onset_list = []
stim_offset_list = []
trial_onset_list = []
abs_response_time_list = []
trial_time = []

iti_list = exp_param.iti.values[:n_trials].tolist()

id_solution_list = exp_param.p_id_solution[0:n_trials].tolist()
f_images = exp_param.f_image[:n_trials].tolist()
m_images = exp_param.m_image[:n_trials].tolist()



m_image_list = [image_directory+str(m_image) for m_image in m_images]
f_image_list = [image_directory+str(f_image) for f_image in f_images]


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
    window.flip()
    inst_keys_p3 = event.waitKeys(keyList=[inst_key,escape_key])
    if escape_key in inst_keys_p3:
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

female_greeble_code = ord('f')
male_greeble_code = ord('m')


#present choices
while t < n_trials:

    #trial has started, get time
    trial_start = expTime_clock.getTime() - start_time

    trial_onset_list.append(trial_start)

    trialTime_clock.reset() #reset time

    fixation_cross.setAutoDraw(True)

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
    else:
        rt = rt_clock.getTime()
        choice=response[0][0]
        if escape_key in response:
            sys.exit('escape key pressed.')


    #get identity of selection
    #if the position of the female is on the left
    if female_greeble.pos[0] == left_pos_x: #if the pos. of the solution is on the left, then left key is correct
        correct_key_choice = left_key
        correct_key_choices.append(ord('L'))
    else:
        correct_key_choice = right_key #else, right key is correct
        correct_key_choices.append(ord('R'))


    if choice == left_key:
        LR_choice_list.append(ord('L'))
    elif choice == right_key:
        LR_choice_list.append(ord('R'))
    elif np.isnan(choice):
        LR_choice_list.append(np.nan)


    if rt < rt_max and rt > rt_min:
        if choice == correct_key_choice:
            id_choice_list.append(female_greeble_code)

        elif choice != correct_key_choice:
            id_choice_list.append(male_greeble_code)

        if id_choice_list[t] == female_greeble_code:
            received_rewards.append(1)
            total_reward += received_rewards[t]
            fixation_cross.setColor(good_color, "dkl")
            window.flip()

        elif id_choice_list[t] != female_greeble_code:
            received_rewards.append(0)
            total_reward += received_rewards[t]
            fixation_cross.setColor(error_color, "dkl")
            window.flip()

    elif rt >= rt_max or rt <= rt_min:
        if choice == correct_key_choice:
            id_choice_list.append(female_greeble_code)
        elif choice != correct_key_choice:
            id_choice_list.append(male_greeble_code)
        received_rewards.append(0)
        total_reward += response_failure_reward
        fixation_cross.setColor(severe_error_color, "dkl")

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
        received_rewards.append(0)
        total_reward += response_failure_reward
        fixation_cross.setColor(severe_error_color, "dkl")
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

    total_rewards.append(total_reward)
    rt_list.append(rt)


    if choice in [left_key, right_key]:
        id_choice_accuracy_list.append(id_choice_list[t] == female_greeble_code)
        cumulative_accuracy_list.append(np.nansum(id_choice_accuracy_list)/(t+1))
    else:
        id_choice_accuracy_list.append(np.nan)
        cumulative_accuracy_list.append(np.nan)


    if t >= acc_window:
        if (sum(id_choice_accuracy_list[-acc_window:])/acc_window) >= criterion:
            inst_msg.setAutoDraw(False)
            cue_list[0].setAutoDraw(False)
            cue_list[1].setAutoDraw(False)
            core.wait(mandatory_trial_time - trialTime_clock.getTime()) #wait until mandatory trial time has passed
            window.flip()
            core.wait(iti_list[t])
            break


    core.wait(mandatory_trial_time - trialTime_clock.getTime()) #wait until mandatory trial time has passed

    cue_list[0].setAutoDraw(False)
    cue_list[1].setAutoDraw(False)

    trial_time.append(trialTime_clock.getTime()) #trial time will always be set, sanity check


    fixation_cross.setColor(neutral_color, "dkl")
    window.flip()
    stim_offset_time = expTime_clock.getTime()

    stim_offset_list.append(stim_offset_time)

    core.wait(iti_list[t])

    window.flip()

    t+=1

fixation_cross.setAutoDraw(False)
total_exp_time = expTime_clock.getTime()


#save data
header = ('trial, subj_id, LR_choice, reward,' +
'cumulative_reward, rt, total_trial_time, iti,' +
 'id_choice, id_solution, id_choice_acc, cum_acc, stim_onset, stim_offset, abs_response_time')

data = np.transpose(np.matrix((trial_list[:t],subj_id_list[:t], LR_choice_list[:t],
received_rewards[:t], total_rewards[:t], rt_list[:t], trial_time[:t], iti_list[:t], id_choice_list[:t], id_solution_list[:t],
id_choice_accuracy_list[:t], cumulative_accuracy_list[:t],
  stim_onset_list[:t], stim_offset_list[:t], abs_response_time_list[:t])))



np.savetxt(output_path, data, header=header, delimiter=',',comments='')
np.savetxt(output_path_readable, data, header=header, delimiter=',',comments='')

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
core.quit()
