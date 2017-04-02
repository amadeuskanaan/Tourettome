__author__ = 'kanaan'

import os
from variables.subject_list import *

print '================================================================'
print '                  Tourettome  Population                        '

# print sample sizes
print '---------------------------------------------'
print ''
print 'Tourettome - Leipzig      N=', len(leipzig)
print 'Tourettome - Paris        N=', len(paris)
print 'Tourettome - Hannover_a   N=', len(hannover_a)
print 'Tourettome - Hannover_b   N=', len(hannover_b)
print ''
print '---------------------------------------------'


# # check FREESURFER DIR
fsdir= tourettome_freesurfer
missing_files = [sub for sub in os.listdir(fsdir)  if 'aparc.DKTatlas+aseg.mgz' not in os.listdir(os.path.join(fsdir, sub, 'mri'))]
missing_dirs  = [sub for sub in tourettome_subjects if not os.path.isdir(os.path.join(fsdir, sub))]

print ''
print 'These subjects have an incomplete recon-all directory. Run them again.',  missing_files + missing_dirs
print 'N=', len(missing_files + missing_dirs)

