import os
import numpy as np
import pathlib2
from pathlib2 import Path
from nilearn import image, masking
from glob import glob

class BaseExtract(object):
   
    def binarize_atlas(self,
                   input_file, 
                   output_dir,
                   name,
                   idx1,
                   idx2):
        
        input_file = Path(input_file)
        output_dir = Path(output_dir)
        
        outuput_file = input_file.name.split("space-T1w_desc-aseg_dseg.nii.gz")[0] + str(name) + ".nii.gz"
        outuput_file = output_dir.joinpath(outuput_file)
        
        cmd = ('/home/raghav/freesurfer/bin/mri_binarize'
               ' --i %s'
               ' --o %s' 
               ' --match %s %s' % (input_file.absolute().as_posix(),
                            outuput_file.absolute().as_posix(),
                            idx1,
                            idx2)
              )
        
        if outuput_file.exists() is False:
            os.system(cmd)
        
        return outuput_file
           
class MaskExtract(BaseExtract):
    
    def __init__(self, 
                 anat_file,
                 output_dir,
                 subject,
                 fmriprep_path,
                 index = [],
                 name = ''):
        
        self.anat_file = Path(anat_file)
        self.output_dir = Path(output_dir)
        self.subject = subject
        self.fmriprep_path = Path(fmriprep_path)
        self.index = index
        self.name = name
        
    def process(self):
        
        anat_file = self.anat_file
        name = self.name
        index = self.index
        subject = self.subject
        fmriprep_path= self.fmriprep_path

        import glob

        if self.name:
                mask_name = self.name 
        else:
            mask_name = 'mask'
            for elem in self.index:
                mask_name += "_" + str(elem).zfill(2)

        if isinstance(self.index, list) is False:
            raise ValueError("Index is not a list")
            
        if not self.index:
            raise ValueError("List is empty")
            
        output_dir = self.output_dir        
        if output_dir.exists() == False:
            output_dir.mkdir(parents=True) 

        sessions = np.arange(2,11)

        for session in sessions:
          session_epi_fns = np.sort(glob.glob(os.path.join(fmriprep_path, 'sub-' + str(subject) + '/fmriprep/sub-' + str(subject) + '/ses-*' + str(session) + '/func/sub-' + str(subject) + '_ses-*'+ str(session) + '_task-lokicat_run-*_space-T1w_desc-preproc_bold.nii.gz')))
          print (session_epi_fns)

          for bold_file in session_epi_fns:
            run = str(bold_file[95:97])
            ses = str(bold_file[75:77])
            self.bold_file = Path(bold_file)
            bold_file = self.bold_file
            bold_img = image.load_img(bold_file.absolute().as_posix())
            bold_mean_img = image.mean_img(bold_img)
            aseg_file = os.path.join(fmriprep_path, 'sub-' + str(subject) + '/fmriprep/sub-' + str(subject) + '/ses-' + str(ses) + '/func/sub-' + str(subject) + '_ses-'+ str(ses) + '_task-lokicat_run-' + str(run) + '_space-T1w_desc-aseg_dseg.nii.gz')
            self.aseg_file = Path(aseg_file)

            #binarise for mask file
            mask_img_file = self.binarize_atlas(input_file = aseg_file,
                                                output_dir= output_dir,
                                                name = name,
                                                idx1 = index[0],
                                                idx2 = index[1])
            
            # Select from the created atlas the regions
            mask_img = image.load_img(mask_img_file.absolute().as_posix())
            
            ## Apply mask to extract the time series
            mask_ts = masking.apply_mask(bold_img, mask_img)
            mask_ts_file = 'sub-' + str(subject) + '_ses-' + str(ses) + '_run-' + str(run) + '_' + mask_name + '_ts.txt'
            
            np.savetxt(output_dir.joinpath(mask_ts_file), mask_ts.T)
        

        

