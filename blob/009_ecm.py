__author__ = 'kanaan 06.08.2017'

import os
from variables.subject_list import *
from utilities.utils import *
from algorithms.fast_ecm import *
import subprocess

def make_eigenvector_centrality(population,workspace_dir):

    for subject in population:

        residual = os.path.join(workspace_dir, subject, 'DENOISE', 'residuals_wmcsf', 'residual_bp.nii')
        ecm_dir  = mkdir_path(os.path.join(workspace_dir, subject, 'ECM'))
        mask     = os.path.join(workspace_dir, subject, 'REGISTRATION', 'ANATOMICAL_GM_MNI2mm.nii')
        os.chdir(ecm_dir)

        print 'Runnning ECM for subject', subject
        # run fast ecm


        matlab_cmd = ['matlab', '-version', '8.2', '-nodesktop', '-nosplash', '-nojvm',
                      #fastECM( inputfile, rankmap, normmap, degmap, maxiter, maskfile, atlasfile )
                      '-r "fastECM(\'%s\', \'1\', \'1\', \'1\', \'20\', \'%s\') ; quit;"' % (residual, mask)]
        print '    ... Running ECM'
        subprocess.call(matlab_cmd)

        # fastECM(inputfile = '/home/raid3/kanaan/Downloads/fastecm/fmri4d.nii.gz',
        #         maskfile  ='/home/raid3/kanaan/Downloads/fastecm/mask_csf.nii.gz')
        #         # atlasfile = None,
        #         # verbose   = True,
        #         # dynamics  = 1,
        #         # rankmap   = 1,
        #         # normmap   = 1,
        #         # degmap    = 1,
        #         # maxiter   = 42,
        #         # wholemat  = 0)

        # print '...... standradizing data'
        # standardize_expr = ['log((a+1)/(a-1))/2']
        # os.system('3dcalc -a residual_fastECM.nii.gz -expr %s -prefix residual_fastECM_zscore.nii.gz'%standardize_expr)
        #

make_eigenvector_centrality(['LZ032'],tourettome_workspace)