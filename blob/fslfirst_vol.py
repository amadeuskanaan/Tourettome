
# ####### Count number of non-zero voxels for FSL-FIRST subcortical segmentations

# # create bilateral masks
# for roi in ['Caud', 'Puta', 'Pall',  'Amyg', 'Hipp', 'Accu', 'Thal']:
#     if not os.path.isfile(os.path.join(anatdir, 'seg_first/FIRST-%s_first.nii.gz'%roi)):
#         os.chdir(firstdir)
#         os.system('fslmaths FIRST-R_%s_first.nii.gz -add FIRST-L_%s_first.nii.gz -bin FIRST-%s_first.nii.gz' %(roi, roi, roi))
#
# # Get jacobian deteminant from anat2mni.mat and multiply by bincount
# jacobian_det = np.linalg.det(np.genfromtxt(os.path.join(anatdir, 'seg_first', 'anat2mni.mat')))
# print jacobian_det
#
# # Make count
# df = pd.DataFrame(index = ['%s'%subject], columns = rois)
# if not os.path.isfile(os.path.join(anatdir, 'seg_first/first_count_jac.csv')):
#     for roi in rois:
#         first = os.path.join(firstdir,'FIRST-%s_first.nii.gz' %roi )
#         count = np.count_nonzero(nb.load(first).get_data()) * jacobian_det
#         df.ix['%s'%subject, roi] = count
#
# df.to_csv(os.path.join(firstdir, 'bin_count_jac.csv'))
# print df