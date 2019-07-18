import pandas as pd
import numpy as np
import glob, os


home = os.path.expanduser('~')
root_exp_param_path = home + '/Dropbox/loki_1/experimental_parameters/'


training_df = pd.read_csv(root_exp_param_path + 'training_greeble_images.csv')
test_df = pd.read_csv(root_exp_param_path + 'test_greeble_images.csv')

training_images = training_df.values.flatten()
testing_images = test_df.image.values.flatten()


training_runs_df = pd.concat(map(pd.read_csv, glob.glob(root_exp_param_path + 'reward_parameters/*_run*.csv')))
training_runs_images = np.array((training_runs_df.f_image.values, training_runs_df.m_image.values)).flatten()


reward_criterion_task_df = pd.concat(map(pd.read_csv, glob.glob(root_exp_param_path + 'criterion_parameters/reward_criterion_parameters/*_criterion*.csv')))
reward_criterion_task_images = np.array((reward_criterion_task_df.f_image.values, reward_criterion_task_df.m_image.values)).flatten()

perceptual_criterion_task_df = pd.concat(map(pd.read_csv, glob.glob(root_exp_param_path + 'criterion_parameters/perceptual_disc_criterion_parameters/*_criterion*.csv')))
perceptual_criterion_task_images = np.array((perceptual_criterion_task_df.f_image.values, perceptual_criterion_task_df.m_image.values)).flatten()



def check_overlap(training_images, testing_images,
string_id='RL training and perceptual test sets'):


    unique_images_training = np.unique(training_images)
    unique_images_testing = np.unique(testing_images)

    overlapping_values = sum(unique_images_training == unique_images_testing)

    contamination_flag = overlapping_values == 0

    print('training and test sets for {} are unique: '.format(string_id), contamination_flag)


    return (unique_images_training, unique_images_testing,
    overlapping_values, contamination_flag)



def check_identity(training_runs_images, unique_images_training,
 string_id='RL source and implemented training images'):

    unique_images_training_runs = np.unique(training_runs_images)

    overlapping_values = unique_images_training_runs == unique_images_training

    identities_same_flag = len(overlapping_values) == len(unique_images_training_runs)

    print('original and implemented training sets for {} contain the same identities: '.format(string_id),
    identities_same_flag)

    return (overlapping_values, identities_same_flag)





(unique_images_training, unique_images_testing,
overlapping_values, contamination_flag) = check_overlap(training_images,
testing_images) # test that the source sets of training images and test images do not overlap

(overlapping_values, identities_same_flag) = check_identity(training_runs_images,
unique_images_training) # test that the training images used in the RL task are sampled from the source list of training images



# check criterion task images

(overlapping_values, identities_same_flag) = check_identity(reward_criterion_task_images,
unique_images_training, string_id='RL criterion task and RL training images') # test that the criterion task images are sampled from the source list of training images

(unique_images_training, unique_images_testing,
overlapping_values, contamination_flag) = check_overlap(reward_criterion_task_images,
testing_images, string_id='RL criterion task and perceptual testing images') # test that the criterion task images have no overlap with the test images


(overlapping_values, identities_same_flag) = check_identity(perceptual_criterion_task_images,
unique_images_training, string_id='perceptual criterion task and RL training images') # test that the criterion task images are sampled from the source list of training images

(unique_images_training, unique_images_testing,
overlapping_values, contamination_flag) = check_overlap(perceptual_criterion_task_images,
testing_images, string_id='perceptual criterion task and perceptual testing images') # test that the criterion task images have no overlap with the test images
