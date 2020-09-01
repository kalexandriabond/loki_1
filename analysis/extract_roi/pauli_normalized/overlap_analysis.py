import os
import numpy as np
import glob
from pathlib import Path
import pathlib2
import nibabel as nib
import pandas as pd

subject = '790'

Thresholds = ['02','05','07','09']

work_dir = '/home/raghav/Desktop/Git_repo/loki_1/data/BOLD/roi_extract/Pauli_normalized/sub-' + str(subject)

voxel_overlap_dfs = []

for Threshold in Thresholds:

	roi_masks = np.sort(glob.glob(os.path.join(work_dir, 'sub-' + str(subject) + '_pauli_Native_norm_*_2mm_bin_' + Threshold + '.nii.gz')))

	output_file = os.path.join(work_dir,'combined_mask_thres_' + Threshold + '.nii.gz')

	output_file = Path(output_file)

	cmd = ('fslmaths %s'
	           ' -add %s'
	           ' -add %s'
	           ' -add %s'
	           ' -add %s'
	           ' -add %s'
	           ' -add %s'
	           ' -add %s'
	           ' -add %s'
	           ' -add %s'
	           ' -add %s'
	           ' -add %s'
	           ' -add %s'
	           ' -add %s'
	           ' -add %s'
	           ' -add %s'
	           ' %s' % (roi_masks[0],
	           			roi_masks[1],
	           			roi_masks[2],
	           			roi_masks[3],
	           			roi_masks[4],
	           			roi_masks[5],
	           			roi_masks[6], 
	           			roi_masks[7],
	           			roi_masks[8],
	           			roi_masks[9],
	           			roi_masks[10],
	           			roi_masks[11],
	           			roi_masks[12],
	           			roi_masks[13],
	           			roi_masks[14],
	           			roi_masks[15],
	                    output_file)
	          )

	if output_file.exists() is False:
	            print("Combining mask using threshold %s..." % Threshold)
	            os.system(cmd)

	img = nib.load(output_file)
	img_data= img.get_fdata()

	#print(img_data.shape)

	occurrence_1 = np.count_nonzero(img_data == 1)
	occurrence_2 = np.count_nonzero(img_data == 2)
	occurrence_3 = np.count_nonzero(img_data == 3)
	occurrence_4 = np.count_nonzero(img_data == 4)

	voxel_count_total = occurrence_1 + occurrence_2 + occurrence_3 + occurrence_4
	voxel_ratio_1 = occurrence_1 / voxel_count_total *100
	voxel_ratio_2 = occurrence_2 / voxel_count_total *100
	voxel_ratio_3 = occurrence_3 / voxel_count_total *100
	voxel_ratio_4 = occurrence_4 / voxel_count_total *100

	data = [{'subject' : subject,
			 'Threshold' : Threshold,
			 'Total Voxels' : voxel_count_total,
			 'no overlap %' : voxel_ratio_1,
			 '2 roi overlap %' : voxel_ratio_2,
			 '3 roi overlap %' : voxel_ratio_3,
			 '4 roi overlap %' : voxel_ratio_4}]

	voxel_overlap_temp_df = pd.DataFrame(data)
	# voxel_overlap_temp_df['subject'] = subject
	# voxel_overlap_temp_df['Threshold'] = Threshold
	# voxel_overlap_temp_df['Total Voxels'] = voxel_count_total
	# voxel_overlap_temp_df['no overlap %'] = voxel_ratio_1
	# voxel_overlap_temp_df['2 roi overlap %'] = voxel_ratio_2
	# voxel_overlap_temp_df['3 roi overlap %'] = voxel_ratio_3
	# voxel_overlap_temp_df['4 roi overlap %'] = voxel_ratio_4

	print(voxel_overlap_temp_df)
	voxel_overlap_dfs.append(voxel_overlap_temp_df)
	
voxel_overlap_df = pd.concat(voxel_overlap_dfs, axis =0)
file_name = 'sub_' + subject + '_overlap_analysis.csv'

output_analysis_file = os.path.join(work_dir,file_name)

voxel_overlap_df.to_csv(output_analysis_file, index = True)