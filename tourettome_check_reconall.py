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



fsdir_subs    = [sub for sub in os.listdir(fsdir) if sub in tourettome_subjects]
missing_files = [sub for sub in fsdir_subs if 'aparc.DKTatlas+aseg.mgz' not in os.path.join(fsdir, sub, 'mri')]
missing_dirs  = [sub for sub in tourettome_subjects if not os.path.isdir(os.path.join(fsdir, sub))]

print ''
print 'These subjects have no recon-all directory.',  missing_dirs
print 'These subjects have an incomplete recon-all directory.',  missing_files
print 'N=', len(missing_files + missing_dirs)

