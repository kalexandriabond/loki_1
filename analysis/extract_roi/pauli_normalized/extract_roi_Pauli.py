import os

# Install required packages

# os.system('pip install numpy')
# os.system('pip install nilearn')
# os.system('pip install nipy')
# os.system('pip install nistats')

from src import MaskExtract


#Specify subject
subject = '811'

#Specify threshold for masks
threshold = '0.5'

## Define files/paths to pass to this object

#Fmriprep path
fmriprep_path = '.../loki_1/data/BOLD'
# T1
anat_img = os.path.join(fmriprep_path,'sub-' + str(subject) + '/fmriprep/sub-' + str(subject) + '/anat/sub-' + str(subject) + '_desc-preproc_T1w.nii.gz') 
# Output directory where dump all the outpus
output_dir = '.../loki_1/data/BOLD/roi_extract/Pauli_normalized/sub-' + str(subject)
# Path to scripts
analysis_path = '.../loki_1/analysis/extract_roi/pauli_normalized'



# # PUTAMEN

name_roi = 'Pu'

Pu_extract = MaskExtract(anat_file = anat_img,
                           output_dir = output_dir,
                           name = name_roi,
                           subject = subject,
                           analysis_path = analysis_path,
                           threshold = threshold,
                           fmriprep_path = fmriprep_path)

Pu_extract.process()


# # CAUDATE

name_roi = 'Ca'

Ca_extract = MaskExtract(anat_file = anat_img, 
                              output_dir = output_dir,
                              name=name_roi,
                              analysis_path = analysis_path,
                              subject = subject,
                              threshold = threshold,
                              fmriprep_path = fmriprep_path)

Ca_extract.process()

# # GPi

name_roi = 'GPi'

GPi_extract = MaskExtract(anat_file = anat_img,
                              output_dir = output_dir,
                              name=name_roi,
                              subject = subject,
                              analysis_path = analysis_path,
                              threshold = threshold,
                              fmriprep_path = fmriprep_path)

GPi_extract.process()

# # GPe

name_roi = 'GPe'

GPe_extract = MaskExtract(anat_file = anat_img,
                              output_dir = output_dir,
                              name=name_roi,
                              subject = subject,
                              threshold = threshold,
                              analysis_path = analysis_path,
                              fmriprep_path = fmriprep_path)

GPe_extract.process()

# # Ventral Pallidum

name_roi = 'VeP'

VeP_extract = MaskExtract(anat_file = anat_img,
                              output_dir = output_dir,
                              name=name_roi,
                              subject = subject,
                              threshold = threshold,
                              analysis_path = analysis_path,
                              fmriprep_path = fmriprep_path)

VeP_extract.process()

# # SNc

name_roi = 'SNc'

SNc_extract = MaskExtract(anat_file = anat_img,
                              output_dir = output_dir,
                              threshold = threshold,
                              name=name_roi,
                              subject = subject,
                              analysis_path = analysis_path,
                              fmriprep_path = fmriprep_path)

SNc_extract.process()

# # RN

name_roi = 'RN'

RN_extract = MaskExtract(anat_file = anat_img,
                              output_dir = output_dir,
                              threshold = threshold,
                              name=name_roi,
                              subject = subject,
                              analysis_path = analysis_path,
                              fmriprep_path = fmriprep_path)

RN_extract.process()


# # SNr

name_roi = 'SNr'

SNr_extract = MaskExtract(anat_file = anat_img,
                              output_dir = output_dir,
                              threshold = threshold,
                              name=name_roi,
                              subject = subject,
                              analysis_path = analysis_path,
                              fmriprep_path = fmriprep_path)

SNr_extract.process()


# # ACCUMBENS

name_roi = 'NAC'

NAC_extract = MaskExtract(anat_file = anat_img,
                              output_dir = output_dir,
                              threshold = threshold,
                              name=name_roi,
                              subject = subject,
                              analysis_path = analysis_path,
                              fmriprep_path = fmriprep_path)

NAC_extract.process()

# # Extended Amygdala

name_roi = 'EXA'

EXA_extract = MaskExtract(anat_file = anat_img,
                              output_dir = output_dir,
                              threshold = threshold,
                              name=name_roi,
                              subject = subject,
                              analysis_path = analysis_path,
                              fmriprep_path = fmriprep_path)

EXA_extract.process()

# # PBP

name_roi = 'PBP'

PBP_extract = MaskExtract(anat_file = anat_img,
                              output_dir = output_dir,
                              threshold = threshold,
                              name=name_roi,
                              subject = subject,
                              analysis_path = analysis_path,
                              fmriprep_path = fmriprep_path)

PBP_extract.process()

# # VTA

name_roi = 'VTA'

VTA_extract = MaskExtract(anat_file = anat_img,
                              output_dir = output_dir,
                              threshold = threshold,
                              name=name_roi,
                              subject = subject,
                              analysis_path = analysis_path,
                              fmriprep_path = fmriprep_path)

VTA_extract.process()

# # HN

name_roi = 'HN'

HN_extract = MaskExtract(anat_file = anat_img,
                              output_dir = output_dir,
                              threshold = threshold,
                              name=name_roi,
                              subject = subject,
                              analysis_path = analysis_path,
                              fmriprep_path = fmriprep_path)

HN_extract.process()

# # HTH

name_roi = 'HTH'

HTH_extract = MaskExtract(anat_file = anat_img,
                              output_dir = output_dir,
                              threshold = threshold,
                              name=name_roi,
                              subject = subject,
                              analysis_path = analysis_path,
                              fmriprep_path = fmriprep_path)

HTH_extract.process()

# # MN

name_roi = 'MN'

MN_extract = MaskExtract(anat_file = anat_img,
                              output_dir = output_dir,
                              threshold = threshold,
                              name=name_roi,
                              subject = subject,
                              analysis_path = analysis_path,
                              fmriprep_path = fmriprep_path)

MN_extract.process()

# # STH

name_roi = 'STH'

STH_extract = MaskExtract(anat_file = anat_img,
                              output_dir = output_dir,
                              threshold = threshold,
                              name=name_roi,
                              subject = subject,
                              analysis_path = analysis_path,
                              fmriprep_path = fmriprep_path)

STH_extract.process()