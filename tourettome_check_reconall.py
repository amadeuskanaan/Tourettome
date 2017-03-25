__author__ = 'kanaan'

import os
from variables.subject_list import *

print '================================================================'
print '                  Tourettome  Population                        '



print 'Tourettome - Leipzig      N=', len(leipzig)
print 'Tourettome - Paris        N=', len(paris)
print 'Tourettome - Hannover_a   N=', len(hannover_a)
print 'Tourettome - Hannover_b   N=', len(hannover_b)



fsdir= tourettome_freesurfer
population = [i for i in sorted(os.listdir(fsdir)) if os.path.isdir(os.path.join(fsdir, i))]

missing = []

for subject in population:
	subdir = os.path.join(fsdir, subject, 'mri')
	if 'aparc.DKTatlas+aseg.mgz' not in os.listdir(subdir):
		missing.append(subject)

print 'These subjects have an incomplete recon-all directory. Run them again.',  missing
print 'N=', len(missing)