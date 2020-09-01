import os
import numpy as np
from pathlib import Path
import pathlib2
from nilearn import image, masking
import glob
from .coord_transform import voxcoord_to_mm, get_3D_coordmap, mm_to_voxcoord
import pandas as pd

# Section 1

class BaseExtract(object):

  def resample_2mm(self, 
                   input_file,  
                   output_dir):
      
      input_file = Path(input_file)
      output_dir = Path(output_dir)
      
      output_file = input_file.name.split(".nii.gz")[0]
      output_file = output_file + "_2mm.nii.gz"
      output_file = output_dir.joinpath(output_file)        
      
      cmd = ('fslmaths '
             ' %s'
             ' -subsamp2'
             ' %s' % (input_file.absolute().as_posix(),
                      output_file.absolute().as_posix())
             )
      
      
      if output_file.exists() is False:
          print("Resampling to bold resolution (2 mm)...")
          os.system(cmd)
      
      return output_file
  
  
  def binarise_mask(self,
                    input_file, 
                    threshold,
                    output_dir):
      
      input_file = Path(input_file)
      output_dir = Path(output_dir)
      
      # Ensure threshold is float
      threshold = float(threshold)
      
      # Pass threshold to string to print that in the name
      thr_string = str(threshold).replace(".", "")
      
      outuput_file = input_file.name.split(".nii.gz")[0] + "_bin_%s.nii.gz" % thr_string
      outuput_file = output_dir.joinpath(outuput_file)
      
      cmd = ('fslmaths %s'
             ' -thr %f -bin'
             ' %s' % (input_file.absolute().as_posix(),
                      threshold, 
                      outuput_file.absolute().as_posix())
            )
      
      if outuput_file.exists() is False:
          print("Binarising mask using threshold %f..." % threshold)
          os.system(cmd)
      
      return outuput_file
            
        
class MaskExtract(BaseExtract):
    
    def __init__(self, 
                 anat_file, 
                 subject,
                 output_dir,
                 fmriprep_path,
                 analysis_path,
                 threshold,
                 name = ''):
        
        self.anat_file = Path(anat_file)
        self.subject = subject
        self.output_dir = Path(output_dir)
        self.fmriprep_path = Path(fmriprep_path)
        self.analysis_path = Path(analysis_path)
        self.threshold = threshold
        self.name = name
        
    def process(self):
        
        anat_file = self.anat_file
        threshold = self.threshold
        name = self.name
        subject = self.subject
        fmriprep_path= self.fmriprep_path
        analysis_path= self.analysis_path

        
        if self.name:
            mask_name = self.name 
        else:
            mask_name = 'mask'
            for elem in self.index:
                mask_name += "_" + str(elem).zfill(2)
            
        output_dir = self.output_dir        
        if output_dir.exists() == False:
            output_dir.mkdir(parents=True)

        atlas_filename = os.path.join(output_dir, 'raw_masks_norm/sub-' + subject + '_pauli_det_Native_norm_' + name + '.nii.gz')
        self.atlas_filename = Path(atlas_filename)

        # 1- Downsample mask to BOLD resolution (2mm) using fslmaths        
        mask_anat_2mm_file = self.resample_2mm(input_file = atlas_filename,
                                                output_dir = output_dir)


        # 2- Binarise mask using a given threshold 
        mask_anat_bin_file = self.binarise_mask(input_file = mask_anat_2mm_file, 
                                                threshold = threshold,
                                                output_dir = output_dir)

        mask_anat_bin_file = image.load_img(mask_anat_bin_file.absolute().as_posix())


        ## Specify sessions to extract
        sessions = np.arange(2,11)

        # Section 2

        ## Comment out the section below for overlap analysis and uncomment for voxel extraction


        ## Loop through sessions to extract bold runs to apply mask

        for session in sessions:
          session_epi_fns = np.sort(glob.glob(os.path.join(fmriprep_path, 'sub-' + str(subject) + '/ses-*' + str(session) + '/func/sub-' + str(subject) + '_ses-*'+ str(session) + '_task-lokicat_run-*_space-T1w_desc-preproc_bold.nii.gz')))
          print (session_epi_fns)

          for bold_file in session_epi_fns:

            run = str(bold_file[99:101])
            # print(run)
            ses = str(bold_file[79:81])
            # print(ses)
            bold_img = image.load_img(bold_file)
            bold_mean_img = image.mean_img(bold_img)
            # print(bold_img.shape)

            ii, jj, kk = np.where(mask_anat_bin_file.get_fdata()==1)
      
            cm_mask = get_3D_coordmap(mask_anat_bin_file)
            cm_bold = get_3D_coordmap(bold_img)
      
            data = np.zeros(shape=(bold_mean_img.shape), dtype=int)
            for i, j, k in zip(ii, jj, kk):
                x, y, z = voxcoord_to_mm(cm_mask, i, j, k)
                i_new, j_new, z_new = mm_to_voxcoord(cm_bold, x, y, z)
                i_new = int(i_new)
                j_new = int(j_new)
                z_new = int(z_new)

                data[i_new, j_new, z_new] = 1
        
            mask_bold_img = image.new_img_like(image.mean_img(bold_img), 
                                           data = data)

            mask_bold_file = 'sub-' + str(subject) + '_ses-' + str(ses) + '_' + mask_name + "_bold.nii.gz"
            mask_bold_file = output_dir.joinpath(mask_bold_file)
            if mask_bold_file.exists() is False:
              mask_bold_img.to_filename(output_dir.joinpath(mask_bold_file))

            ## Apply mask to extract the time series
            time_series_temp = masking.apply_mask(bold_img, mask_bold_img)
            time_series_extract_file = 'sub-' + str(subject) + '_ses-' + str(ses) + '_run-' + str(run) + '_' + mask_name + '_ts.txt'
            
            np.savetxt(output_dir.joinpath(time_series_extract_file), time_series_temp.T)

            print(time_series_temp.shape)
            print(f"Time series extraction completed for ses-" + ses + "_run-" + run + "_" + mask_name)



        