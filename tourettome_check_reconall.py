__author__ = 'kanaan'

import os
from variables.subject_list import *

print '================================================================'
print '                  Tourettome  Population                        '

# print sample sizes
print '---------------------------------------------'

print 'Tourettome - Leipzig      N=', len(leipzig)
print 'Tourettome - Paris        N=', len(paris)
print 'Tourettome - Hannover_a   N=', len(hannover_a)
print 'Tourettome - Hannover_b   N=', len(hannover_b)

print '---------------------------------------------'


# # check FREESURFER DIR
fsdir= tourettome_freesurfer
missing= [sub for sub in tourettome_subjects if 'aparc.DKTatlas+aseg.mgz' not in os.listdir(os.path.join(fsdir, sub, 'mri'))]

print ''
print 'These subjects have an incomplete recon-all directory. Run them again.',  missing
print 'N=', len(missing)

