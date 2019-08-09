
import os

def main():
    ''' Rename experimental parameter files. '''

    src_folder = os.path.join("/home/coaxlab/Dropbox/loki_1/experimental_parameters/",
    "criterion_parameters/",
    "perceptual_disc_criterion_parameters/")

    os.chdir(src_folder)

    for filename in os.listdir(src_folder):

        print(filename)

        subj_id = filename[:4]
        session_n = filename[4:9]

        dest = subj_id + session_n + '_perceptual_criterion.csv'

        os.rename(filename, dest)

if __name__ == '__main__':

    main()
