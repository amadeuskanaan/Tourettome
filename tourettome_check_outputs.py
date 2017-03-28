__author__ = 'kanaan... 28.03.2017'

import os.path as op
from variables.subject_list import tourettome_subjects, tourettome_workspace



def check_outputs(population, workspace):

    for subject in population:
        if op.isfile(op.join(workspace, subject, 'ANATOMICAL/ANATOMICAL_GM.nii.gz')):
            print '%s Anatomical complete' %subject
        else:
            print 'Subject %s anatomical preprocessing still running'



check_outputs(tourettome_subjects, tourettome_workspace)