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
print 'Tourettome - Hamburg      N=', len(hamburg)
print ''
print 'Tourettome - All          N=', len(tourettome_subjects)
print 'Tourettome - Unusable     N=', len(unsuable_datasets)
print '---------------------------------------------'


# # check FREESURFER DIR
fsdir= tourettome_freesurfer
fsdir = '/data/pt_nmr093_gts/freesurfer'

fsdir_subs       = sorted([sub for sub in os.listdir(fsdir) if sub in tourettome_subjects if sub != 'LZ050'])
finished_subs    = sorted([sub for sub in fsdir_subs if  'rh.thickness' in os.listdir(os.path.join(fsdir, sub, 'surf'))])
running_subs     = sorted([i for i in tourettome_subjects if i not in finished_subs ])
not_running_subs = sorted([i for i in tourettome_subjects if i not in fsdir_subs])

print 'Recon-all completed for %s subjects --> ' #%(len(finished_subs), finished_subs)
print 'Currently runnning  for %s subjects --> %s' %(len(finished_subs), finished_subs)
print 'NOT       runnning  for %s subjects --> %s' %(len(not_running_subs), not_running_subs)
# missing_files = [sub for sub in fsdir_subs if 'aparc.DKTatlas+aseg.mgz' not in os.listdir(os.path.join(fsdir, sub, 'mri'))]
# missing_dirs  = [sub for sub in tourettome_subjects if not os.path.isdir(os.path.join(fsdir, sub))]
#
# print ''
# print 'These subjects have no recon-all directory.',  missing_dirs
# print 'These subjects have an incomplete recon-all directory.',  missing_files
# print 'N=', len(missing_files + missing_dirs)
#
