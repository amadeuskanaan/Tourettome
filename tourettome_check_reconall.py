__author__ = 'kanaan'

import os
from variables.subject_list import *

print '================================================================'
print '                  Tourettome  Population                        '

# print sample sizes
print 'Tourettome - Leipzig      N=', len(leipzig)
print 'Tourettome - Paris        N=', len(paris)
print 'Tourettome - Hannover_a   N=', len(hannover_a)
print 'Tourettome - Hannover_b   N=', len(hannover_b)

# # check recon-all outputs
# fsdir= tourettome_freesurfer
# population= [i for i in sorted(os.listdir(fsdir)) if os.path.isdir(os.path.join(fsdir, i))]
# missing= [sub for sub in population if 'aparc.DKTatlas+aseg.mgz' not in os.listdir(os.path.join(fsdir, sub, 'mri'))]
#
# print ''
# print 'These subjects have an incomplete recon-all directory. Run them again.',  missing
# print 'N=', len(missing)
#



def run_reconchecker(population, fs_dir):

    for subject in population:

        os.system('$QA_TOOLS/recon_checker '
                  '-s %s '
                  '-snaps-out '
                  '-snaps-detailed '
                  '-gen-outputFOF '
                  %(subject))








run_thick2surf(tourettome_subjects, tourettome_freesurfer)