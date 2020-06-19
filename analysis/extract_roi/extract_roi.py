import os

# Install required packages

#os.system('pip install numpy == 1.17.0')
#os.system('pip install nilearn')
#os.system('pip install nipy')

from src import MaskExtract

#Specify subject
subject = '811'

## Define files/paths to pass to this object

#Fmriprep path
fmriprep_path = '/home/raghav/loki1/output/'
# T1
anat_img = os.path.join(fmriprep_path,'sub-' + str(subject) + '/fmriprep/sub-' + str(subject) + '/anat/sub-' + str(subject) + '_desc-preproc_T1w.nii.gz') 
# Output directory where dump all the outpus
output_dir = 'loki1/loki_mask_extract/extract/sub-' + str(subject)


# # PUTAMEN

putamen_idxs = [12, 51]
name_roi = 'putamen'

putamen_extract = MaskExtract(anat_file = anat_img,
                           output_dir = output_dir,
                           index = putamen_idxs,
                           name = name_roi,
                           subject = subject,
                           fmriprep_path = fmriprep_path)

putamen_extract.process()


# # CAUDATE

caudate_idxs = [11, 50]
name_roi = 'caudate'

caudate_extract = MaskExtract(anat_file = anat_img, 
                              output_dir = output_dir,
                              index = caudate_idxs,
                              name=name_roi,
                              subject = subject,
                           	  fmriprep_path = fmriprep_path)

caudate_extract.process()


# # ACCUMBENS

accumbens_idxs = [26, 58]
name_roi = 'accumbens'

accumbens_extract = MaskExtract(anat_file = anat_img,
                              output_dir = output_dir,
                              index = accumbens_idxs,
                              name=name_roi,
                              subject = subject,
                              fmriprep_path = fmriprep_path)

accumbens_extract.process()
